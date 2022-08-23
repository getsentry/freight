import {useCallback, useEffect, useMemo, useState} from 'react';
import {useLocation, useNavigate, useOutletContext} from 'react-router-dom';

import useApi from 'app/hooks/useApi';
import useLocalStorage from 'app/hooks/useLocalStorage';

function LockDeploy() {
  const location = useLocation();
  const navigate = useNavigate();
  const {appList, fetchApps} = useOutletContext();

  const api = useApi();
  const firstApp = appList.length !== 0 ? appList[0] : null;

  const [lastApp, setLastApp] = useLocalStorage('lastApp', null);

  const defaultApp = location.query?.app ?? lastApp ?? firstApp?.name ?? null;

  const [app, setApp] = useState(defaultApp);

  const appObj = useMemo(
    () => appList.find(appEntry => appEntry.name === app),
    [app, appList]
  );

  // XXX: boolean false is used to indicate
  const [reason, setReason] = useState(appObj?.lockedReason);
  const isLocked = !!appObj.lockedReason;

  // update reason when app changes changes
  useEffect(() => void setReason(appObj?.lockedReason ?? null), [appObj]);

  const [submitError, setSubmitError] = useState(false);
  const [submitInProgress, setSubmitInProgress] = useState(false);

  const handleLockUpdate = useCallback(
    async lockedReason => {
      setSubmitInProgress(true);

      const deployResp = await api.request(`/apps/${app}/`, {
        method: 'PUT',
        data: {lockedReason},
      });

      const result = await deployResp.json();

      if (deployResp.ok) {
        await fetchApps();
        navigate(`/${app}`);
      } else {
        setSubmitError(result.error);
        setSubmitInProgress(false);
      }
    },
    [api, app, navigate, fetchApps]
  );

  return (
    <div className="lock-deploy">
      <div className="section">
        <div className="section-header">
          <h2>Lock / Unlock Deploy</h2>
        </div>
        {submitError && (
          <div className="alert alert-block alert-danger">
            <strong>Unable lock deploys: </strong>
            <span>{submitError}</span>
          </div>
        )}
        <form onSubmit={undefined}>
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
            <label>Lock Reason</label>
            <textarea
              rows={5}
              className="form-control"
              value={reason ?? ''}
              onChange={e => setReason(e.target.value)}
            />
          </div>

          <div className="submit-group">
            <button
              type="submit"
              className="btn btn-primary"
              onClick={() => handleLockUpdate(reason)}
              disabled={submitInProgress}
            >
              Update
            </button>
            {isLocked && (
              <button
                type="submit"
                className="btn btn-success"
                onClick={() => handleLockUpdate(false)}
                disabled={submitInProgress}
              >
                Unlock App
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

export default LockDeploy;
