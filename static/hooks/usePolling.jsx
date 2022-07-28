import {useCallback, useEffect, useRef} from 'react';

import api from 'app/api';

/**
 * How long between polls
 */
const DEFAULT_DELAY = 3000;

/**
 * How long between polls if the most recent poll request failed
 */
const BACKOFF_DELAY = 10000;

function usePolling({url, handleRecieveData, pollingActive = true}) {
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
  }, [url, handleRecieveData]);

  const pollTimeoutRef = useRef(undefined);

  /**
   * Starts chain triggering the makeRequest
   */
  const triggerPolling = useCallback(async () => {
    if (!pollingActive) {
      return;
    }

    const wasSuccess = await makeRequest();

    pollTimeoutRef.current = window.setTimeout(
      triggerPolling,
      wasSuccess ? DEFAULT_DELAY : BACKOFF_DELAY
    );

    return;
  }, [makeRequest, pollingActive]);

  useEffect(() => {
    triggerPolling();

    return () => {
      window.clearTimeout(pollTimeoutRef.current);
      pollTimeoutRef.current = undefined;
    };
  }, [triggerPolling]);
}

export default usePolling;
