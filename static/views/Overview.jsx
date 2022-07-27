import * as React from 'react';

import DeployChart from 'app/components/DeployChart';
import LoadingIndicator from 'app/components/LoadingIndicator';
import TaskSummary from 'app/components/TaskSummary';
import useDeployFinishedNotification from 'app/hooks/useDeployFinishedNotification';
import usePolling from 'app/hooks/usePolling';

function Overview() {
  const [deploys, setDeploys] = React.useState(null);
  usePolling({url: '/deploys/', handleRecieveData: setDeploys});

  // Trigger a notification when any deploy changes it's status to `finished`.
  useDeployFinishedNotification(deploys ?? []);

  if (deploys === null) {
    return (
      <div className="container" style={{textAlign: 'center'}}>
        <LoadingIndicator>
          <p>Loading list of deploys.</p>
        </LoadingIndicator>
      </div>
    );
  }

  const activedeployNodes = [];
  const pendingdeployNodes = [];
  const previousdeployNodes = [];

  deploys.forEach(deploy => {
    const node = <TaskSummary key={deploy.id} task={deploy} />;
    if (deploy.status === 'in_progress') {
      activedeployNodes.unshift(node);
    } else if (deploy.status === 'pending') {
      pendingdeployNodes.unshift(node);
    } else {
      previousdeployNodes.push(node);
    }
  });

  return (
    <div>
      <div className="section">
        <div className="section-header">
          <h2>Active Deploys</h2>
        </div>
        {activedeployNodes.length || pendingdeployNodes.length ? (
          <div className="deploy-list">
            {activedeployNodes}
            {pendingdeployNodes}
          </div>
        ) : (
          <p>There are no active deploys.</p>
        )}
      </div>

      <div className="section">
        <div className="section-header">
          <h2>Deploy History</h2>
        </div>

        <DeployChart />

        {previousdeployNodes.length ? (
          <div className="deploy-list">{previousdeployNodes}</div>
        ) : (
          <p>There are no historical deploys.</p>
        )}
      </div>
    </div>
  );
}

export default Overview;
