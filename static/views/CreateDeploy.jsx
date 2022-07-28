import * as React from 'react';
import {browserHistory} from 'react-router';

import api from 'app/api';

function gotoDeploy(deploy) {
  const {app, environment, number} = deploy;
  browserHistory.push(`/deploys/${app.name}/${environment}/${number}`);
}

function CreateDeploy({location, appList = []}) {
  const firstApp = appList.length !== 0 ? appList[0] : null;

  const defaultApp = location.query?.app
    ? location.query.app
    : firstApp
    ? firstApp.name
    : null;

  const [app, setApp] = React.useState(defaultApp);

  const envMap = React.useMemo(
    () => appList.find(appObj => appObj.name === app)?.environments ?? {},
    [app, appList]
  );

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

  const [submitError, setSubmitError] = React.useState(false);
  const [submitInProgress, setSubmitInProgress] = React.useState(false);

  const startDeploy = React.useCallback(async () => {
    const deployResp = await api.request('/deploys/', {
      method: 'POST',
      data: {app, env, ref},
    });

    const result = await deployResp.json();

    if (deployResp.ok) {
      gotoDeploy(result);
    } else {
      setSubmitError(result.error);
      setSubmitInProgress(false);
    }
  }, [app, env, ref]);

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
              onChange={e => setApp(e.target.value)}
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
