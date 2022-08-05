import {useCallback, useEffect, useRef} from 'react';

import Client from 'app/api';

/**
 * Returns an API client that will have it's requests canceled when the owning
 * React component is unmounted (may be disabled via options).
 */
function useApi({persistInFlight} = {}) {
  const localApi = useRef();

  if (localApi.current === undefined) {
    localApi.current = new Client();
  }

  // Use the provided client if available
  const api = localApi.current;

  // Clear API calls on unmount (if persistInFlight is disabled
  const clearOnUnmount = useCallback(() => {
    if (!persistInFlight) {
      api.clear();
    }
  }, [api, persistInFlight]);

  useEffect(() => clearOnUnmount, [clearOnUnmount]);

  return api;
}

export default useApi;
