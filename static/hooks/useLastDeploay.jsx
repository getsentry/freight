import {useCallback, useEffect, useState} from 'react';

import api from 'app/api';

/**
 * Fetches the most recent deploy details for an app/env
 */
function useLastDeploy({app, env}) {
  const [lastDeploy, setLastDeploy] = useState(undefined);

  const fetchLastDeploy = useCallback(async () => {
    setLastDeploy(undefined);

    const deploysResp = await api.request('/deploys/', {
      query: {app, env, status: 'finished'},
    });

    if (deploysResp.ok) {
      const deploys = await deploysResp.json();
      setLastDeploy(deploys[0] ?? null);
    }
  }, [app, env]);

  useEffect(() => void fetchLastDeploy(), [fetchLastDeploy]);

  return lastDeploy;
}

export default useLastDeploy;
