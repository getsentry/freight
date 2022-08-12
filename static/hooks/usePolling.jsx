import {useCallback, useEffect, useRef} from 'react';

import useApi from 'app/hooks/useApi';

/**
 * How long between polls
 */
const DEFAULT_DELAY = 3000;

/**
 * How long between polls if the most recent poll request failed
 */
const BACKOFF_DELAY = 10000;

/**
 * Makes an API request with polling timeouts.
 *
 * handleRecieveData must be a stable reference, otherwise requests will be
 * re-triggered on each render.
 *
 * If pollingActive is set to false, new API requests will not be made after
 * the first is triggered (or any further when any parameter changes)
 *
 * Use the `resetKey` parameter to cause the polling timeout to reset and
 * trigger a new request immediately. This is useful if you want to change the
 * polling URL and immediately trigger a new request.
 */
function usePolling({
  url,
  handleRecieveData,
  timeout = DEFAULT_DELAY,
  backoffTimeout = BACKOFF_DELAY,
  pollingActive = true,
  resetkey = null,
}) {
  const api = useApi();

  /**
   * Returns true if request was successful, false otherwise.
   */
  const makeRequest = useCallback(async () => {
    const pollResp = await api.request(url);

    if (pollResp.ok) {
      const data = await pollResp.json();
      handleRecieveData(data);
    }

    return pollResp.ok;
  }, [api, url, handleRecieveData]);

  const pollTimeoutRef = useRef(undefined);

  // XXX: Because the function which triggers makeRequest will recursively call
  // itself via a setTimeout, we use a ref here to hold reference to the
  // callback so it will correctly handle
  //
  // See: https://overreacted.io/making-setinterval-declarative-with-react-hooks/
  const triggerRef = useRef(() => undefined);

  const enqueNextTrigger = useCallback(
    (wasSuccess = true) => {
      pollTimeoutRef.current = window.setTimeout(
        triggerRef.current,
        wasSuccess ? timeout : backoffTimeout
      );
    },
    [timeout, backoffTimeout]
  );

  const trigger = useCallback(async () => {
    const wasSuccess = await makeRequest();

    if (pollingActive) {
      enqueNextTrigger(wasSuccess);
    }
  }, [makeRequest, pollingActive, enqueNextTrigger]);

  triggerRef.current = trigger;

  // Track if we've triggered the first request. After the first poll all
  // triggers of the useEffect should put triggerPolling in a setTimeout.
  const triggerImmediate = useRef(false);

  // Reset the triggerImmediate flag if the resetKey changes
  useEffect(() => {
    triggerImmediate.current = false;
  }, [resetkey]);

  useEffect(() => {
    // First trigger happens immediately, otherwise if polling is active
    // enqueue the next trigger
    if (triggerImmediate.current && pollingActive) {
      enqueNextTrigger();
    } else {
      trigger();
    }

    triggerImmediate.current = true;

    return () => {
      api.clear();
      window.clearTimeout(pollTimeoutRef.current);
      pollTimeoutRef.current = undefined;
    };
  }, [api, pollingActive, enqueNextTrigger, trigger]);
}

export default usePolling;
