import * as React from 'react';
import {useLocation, useNavigate, useOutletContext} from 'react-router-dom';

import ExpectedChanges from 'app/components/ExpectedChanges';
import TaskSummary from 'app/components/TaskSummary';
import useApi from 'app/hooks/useApi';
import useLastDeploy from 'app/hooks/useLastDeploay';
import useLocalStorage from 'app/hooks/useLocalStorage';
import useRemoteChanges from 'app/hooks/useRemoteChanges';

function CreateDeploy() {
  const location = useLocation();
  const navigate = useNavigate();
  const {appList} = useOutletContext();

  const api = useApi();
  const firstApp = appList.length !== 0 ? appList[0] : null;

  const [lastApp, setLastApp] = useLocalStorage('lastApp', null);

  const defaultApp = location.query?.app ?? lastApp ?? firstApp?.name ?? null;

  const [app, setApp] = React.useState(defaultApp);

  const appObj = React.useMemo(
    () => appList.find(appEntry => appEntry.name === app),
    [app, appList]
  );

  const envMap = React.useMemo(() => appObj?.environments ?? {}, [appObj]);
  const envList = React.useMemo(() => Object.keys(envMap), [envMap]);

  const [env, setEnv] = React.useState(envList?.[0] ?? null);
  const [ref, setRef] = React.useState(envMap[env]?.defaultRef ?? 'master');

  // update environment when environment list changes
  React.useEffect(() => void setEnv(envList?.[0] ?? null), [envList]);

  // Update refs when app or env changes
  React.useEffect(
    () => void setRef(envMap?.[env]?.defaultRef ?? 'master'),
    [env, envMap]
  );

  const changeLabels = React.useMemo(() => appObj?.changeLabels ?? [], [appObj]);

  const [submitError, setSubmitError] = React.useState(false);
  const [submitInProgress, setSubmitInProgress] = React.useState(false);

  const lastDeploy = useLastDeploy({app, env});

  // gaurd against stale last deploys when changing apps
  const lastDeploySha = lastDeploy?.app.name === app ? lastDeploy.sha : null;

  const changes = useRemoteChanges({app, startRef: ref, endRef: lastDeploySha});

  const startDeploy = React.useCallback(async () => {
    const deployResp = await api.request('/deploys/', {
      method: 'POST',
      data: {app, env, ref},
    });

    const result = await deployResp.json();

    if (deployResp.ok) {
      const {app: nextApp, environment, number} = result;
      navigate(`/deploys/${nextApp.name}/${environment}/${number}`);
    } else {
      setSubmitError(result.error);
      setSubmitInProgress(false);
    }
  }, [api, app, env, ref, navigate]);

  /**
   * Handles creating a deploy
   */
  const handleSubmit = React.useCallback(
    e => {
      e.preventDefault();

      if (submitInProgress) {
        return;
      }

      setSubmitInProgress(true);
      startDeploy();
    },
    [startDeploy, submitInProgress]
  );

  return (
    <div className="create-deploy">
      <div className="section">
        <div className="section-header">
          <h2>Create Deploy</h2>
        </div>
        {submitError && (
          <div className="alert alert-block alert-danger">
            <strong>Unable to create deploy: </strong>
            <span>{submitError}</span>
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Application</label>
            <select
              className="form-control"
              value={app}
              onChange={e => {
                setApp(e.target.value);
                setLastApp(e.target.value);
              }}
            >
              {appList.map(a => (
                <option key={a.name}>{a.name}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Environment</label>
            <select
              className="form-control"
              value={env}
              onChange={e => setEnv(e.target.value)}
            >
              {Object.keys(envMap).map(e => (
                <option key={e}>{e}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Ref</label>
            <input
              type="text"
              className="form-control"
              onChange={e => setRef(e.target.value)}
              placeholder="e.g. master"
              value={ref}
            />
          </div>

          <div className="form-group">
            <label>Last Deploy</label>
            {lastDeploy === undefined ? (
              <p>Loading previous deploy details</p>
            ) : lastDeploy === null ? (
              <p>
                This will be the first deploy of {app}/{env}
              </p>
            ) : (
              <TaskSummary task={lastDeploy} />
            )}
          </div>

          <div className="form-group">
            <label>Changes Since</label>
            <ExpectedChanges changes={changes} markedLabels={changeLabels} />
          </div>

          <div className="submit-group">
            <button type="submit" className="btn btn-primary" disabled={submitInProgress}>
              Ship It!
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateDeploy;
