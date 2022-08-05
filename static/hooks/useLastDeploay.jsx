import {useCallback, useEffect, useState} from 'react';

import useApi from 'app/hooks/useApi';

/**
 * Fetches the most recent deploy details for an app/env
 */
function useLastDeploy({app, env}) {
  const api = useApi();

  const [lastDeploy, setLastDeploy] = useState(undefined);

  const fetchLastDeploy = useCallback(async () => {
    setLastDeploy(undefined);
    api.clear();

    const deploysResp = await api.request('/deploys/', {
      query: {app, env, status: 'finished'},
    });

    if (deploysResp.ok) {
      const deploys = await deploysResp.json();
      setLastDeploy(deploys[0] ?? null);
    }
  }, [api, app, env]);

  useEffect(() => void fetchLastDeploy(), [fetchLastDeploy]);

  return lastDeploy;
}

export default useLastDeploy;
