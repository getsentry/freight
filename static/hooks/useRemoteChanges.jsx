import {useCallback, useEffect, useState} from 'react';

import useApi from 'app/hooks/useApi';

/**
 * Fetches the expected changes for an app, given the start and end ref.
 */
function useRemoteChanges({app, startRef, endRef}) {
  const api = useApi();
  const [changes, setChanges] = useState(undefined);

  const fetchRemoteChanges = useCallback(async () => {
    setChanges(undefined);
    api.clear();

    if (!startRef || !endRef) {
      setChanges([]);
      return;
    }

    const changesResp = await api.request(`/remote-changes/${app}/`, {
      query: {startRef, endRef},
    });

    if (changesResp.ok) {
      setChanges(await changesResp.json());
    } else {
      setChanges(null);
    }
  }, [api, app, endRef, startRef]);

  useEffect(() => void fetchRemoteChanges(), [fetchRemoteChanges]);

  return changes;
}

export default useRemoteChanges;
