import * as React from 'react';

import api from 'app/api';

import TaskSummary from './TaskSummary';

function ExpectedChanges({app, env}) {
  const [lastDeploy, setLastDeploy] = React.useState(undefined);

  const fetchLastDeploy = React.useCallback(async () => {
    const deploysResp = await api.request('/deploys/', {
      query: {app, env, status: 'finished'},
    });

    if (deploysResp.ok) {
      const deploys = await deploysResp.json();
      setLastDeploy(deploys[0] ?? null);
    }
  }, [app, env]);

  React.useEffect(() => void fetchLastDeploy(), [fetchLastDeploy]);

  if (lastDeploy === undefined) {
    return (
      <div>
        <label>Previous Deploy</label>
        <p>Loading previous deploy info</p>
      </div>
    );
  }

  if (lastDeploy === null) {
    return (
      <div>
        <label>Previous Deploy</label>
        <p>
          This will be the first deploy of {app}/{env}
        </p>
      </div>
    );
  }

  return (
    <div>
      <label>Previous Deploy</label>
      <TaskSummary task={lastDeploy} />
    </div>
  );
}

export default ExpectedChanges;
