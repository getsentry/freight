import * as React from 'react';
import {useParams} from 'react-router-dom';

import DeployChart from 'app/components/DeployChart';
import LoadingIndicator from 'app/components/LoadingIndicator';
import TaskSummary from 'app/components/TaskSummary';
import useApi from 'app/hooks/useApi';
import usePolling from 'app/hooks/usePolling';

function AppDetails() {
  const params = useParams();
  const api = useApi();
  const [error, setError] = React.useState(false);

  const [app, setApp] = React.useState(null);
  const [deploys, setDeploys] = React.useState(null);

  const loadApp = React.useCallback(async () => {
    const appResp = await api.request(`/apps/${params.app}/`);

    if (appResp.ok) {
      setApp(await appResp.json());
    } else {
      const errorMessage =
        appResp.status === 404
          ? `Invalid application: ${params.app}`
          : 'Error fetching data';
      setError(errorMessage);
    }
  }, [api, params.app]);

  // Load app
  React.useEffect(() => void loadApp(), [loadApp]);

  // Poll for deploys
  usePolling({url: `/deploys/?app=${params.app}`, handleRecieveData: setDeploys});

  if (error) {
    return <h2>{error}</h2>;
  }

  if (deploys === null || app === null) {
    return <LoadingIndicator />;
  }

  const activeDeployNodes = [];
  const pendingDeployNodes = [];
  const previousDeployNodes = [];

  deploys.forEach(deploy => {
    const node = <TaskSummary key={deploy.id} task={deploy} />;
    if (deploy.status === 'in_progress') {
      activeDeployNodes.unshift(node);
    } else if (deploy.status === 'pending') {
      pendingDeployNodes.unshift(node);
    } else {
      previousDeployNodes.push(node);
    }
  });

  return (
    <div>
      <div className="section">
        <div className="section-header">
          <h2>{app.name} - Active Deploys</h2>
        </div>

        {activeDeployNodes.length || pendingDeployNodes.length ? (
          <div className="deploy-list">
            {activeDeployNodes}
            {pendingDeployNodes}
          </div>
        ) : (
          <p>There are no active deploys.</p>
        )}
      </div>

      <div className="section">
        <div className="section-header">
          <h2>{app.name} - Deploy History</h2>
        </div>

        <DeployChart app={app.name} />

        {previousDeployNodes.length ? (
          <div className="deploy-list">{previousDeployNodes}</div>
        ) : (
          <p>There are no historical deploys.</p>
        )}
      </div>
    </div>
  );
}

export default AppDetails;
