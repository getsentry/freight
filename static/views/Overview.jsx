import {useEffect, useState} from 'react';
import {useOutletContext, useParams} from 'react-router-dom';
// eslint-disable-next-line no-restricted-imports
import {marked} from 'marked';

import DeployChart from 'app/components/DeployChart';
import LoadingIndicator from 'app/components/LoadingIndicator';
import TaskSummary from 'app/components/TaskSummary';
import useDeployFinishedNotification from 'app/hooks/useDeployFinishedNotification';
import usePolling from 'app/hooks/usePolling';

function Overview() {
  const params = useParams();

  // If the app is specified look for it in the app list
  const {appList} = useOutletContext();
  const app = appList.find(a => a.name === params.app);

  const [deploys, setDeploys] = useState(null);

  usePolling({
    url: app ? `/deploys/?app=${app.name}` : '/deploys/',
    handleRecieveData: setDeploys,
    resetkey: app?.name,
  });

  // Reset deploylist if app changes
  useEffect(() => setDeploys(null), [app?.name]);

  // Trigger a notification when any deploy changes it's status to `finished`.
  useDeployFinishedNotification(deploys ?? []);

  if (params.app !== undefined && !app) {
    return <h2>Invalid app name</h2>;
  }

  if (deploys === null) {
    return (
      <div className="container" style={{textAlign: 'center'}}>
        <LoadingIndicator>
          <p>Loading list of deploys.</p>
        </LoadingIndicator>
      </div>
    );
  }

  const activeDeploys = [];
  const pendingDeploys = [];
  const previousDeploys = [];

  deploys.forEach(deploy => {
    const node = <TaskSummary key={deploy.id} task={deploy} />;
    if (deploy.status === 'in_progress') {
      activeDeploys.unshift(node);
    } else if (deploy.status === 'pending') {
      pendingDeploys.unshift(node);
    } else {
      previousDeploys.push(node);
    }
  });

  const lockedAlerts = appList
    .filter(a => a.lockedReason !== null)
    .map(a => (
      <div key={a.name} className="locked-status alert alert-danger">
        <div dangerouslySetInnerHTML={{__html: marked(a.lockedReason)}} />
        <div>
          <span className="label label-danger">{a.name} Locked</span>
        </div>
      </div>
    ));

  return (
    <div>
      <div className="section">
        {lockedAlerts}
        <div className="section-header">
          <h2>Active Deploys</h2>
        </div>
        {activeDeploys.length || pendingDeploys.length ? (
          <div className="deploy-list">
            {activeDeploys}
            {pendingDeploys}
          </div>
        ) : (
          <p>There are no active deploys.</p>
        )}
      </div>

      <div className="section">
        <div className="section-header">
          <h2>Deploy History</h2>
        </div>

        <DeployChart app={app?.name} />

        {previousDeploys.length ? (
          <div className="deploy-list">{previousDeploys}</div>
        ) : (
          <p>There are no historical deploys.</p>
        )}
      </div>
    </div>
  );
}

export default Overview;
