import {useCallback, useEffect, useState} from 'react';

import api from 'app/api';

/**
 * Fetches the expected changes for an app, given the start and end ref.
 */
function useRemoteChanges({app, startRef, endRef}) {
  const [changes, setChanges] = useState(undefined);

  const fetchRemoteChanges = useCallback(async () => {
    setChanges(undefined);

    if (startRef === undefined || endRef === undefined) {
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
  }, [app, endRef, startRef]);

  useEffect(() => void fetchRemoteChanges(), [fetchRemoteChanges]);

  return changes;
}

export default useRemoteChanges;
