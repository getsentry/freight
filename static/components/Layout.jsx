import React from 'react';
import {Link} from 'react-router';
// eslint-disable-next-line no-restricted-imports
import {init} from '@sentry/browser';

import api from 'app/api';
import LoadingIndicator from 'app/components/LoadingIndicator';

function Layout({params, children}) {
  const {app} = params;

  const [appList, setAppList] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState(false);

  const fetchData = React.useCallback(async () => {
    // try to fetch config first
    const configResp = await api.request('/config/');
    const config = await configResp.json();

    if (configResp.ok) {
      if (config?.SENTRY_PUBLIC_DSN) {
        init({dsn: config.SENTRY_PUBLIC_DSN});
      }
    } else {
      // eslint-disable-next-line no-console
      console.error('Error fetching /config/');

      if (configResp?.status !== 401) {
        return;
      }

      // 401 requires authorization
      if (config?.data?.next) {
        window.location.assign(config.data.next);
      }

      setLoading(false);
      setError('Not Authorized');

      return;
    }

    // Fetch apps
    const appsResp = await api.request('/apps/');

    if (appsResp.ok) {
      setAppList(await appsResp.json());
      setError(false);
    } else {
      // eslint-disable-next-line no-console
      console.error('Error fetching /apps/');
      setError(true);
    }

    setLoading(false);
  }, []);

  React.useEffect(() => void fetchData(), [fetchData]);

  return (
    <div>
      <header>
        <div className="container">
          <div className="pull-right">
            <Link
              to={{
                pathname: '/deploy',
                query: {app},
              }}
              className={`btn btn-sm btn-default ${(loading || error) && 'btn-disabled'}`}
            >
              Deploy
            </Link>
          </div>
          <h1>
            <Link to="/">Freight</Link>
          </h1>
          {app && (
            <h2>
              <Link to={`/${app}`}>{app}</Link>
            </h2>
          )}
        </div>
      </header>

      <div className="body">
        <div className="container">
          {loading && (
            <div style={{textAlign: 'center'}}>
              <LoadingIndicator>
                <p>Loading application data. Hold on to your pants!</p>
              </LoadingIndicator>
            </div>
          )}
          {!loading && (error ? error : React.cloneElement(children, {appList}))}
        </div>
      </div>
    </div>
  );
}

export default Layout;
