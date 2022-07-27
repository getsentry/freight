import * as React from 'react';
import {browserHistory} from 'react-router';
import PropTypes from 'prop-types';

import api from 'app/api';

class CreateDeploy extends React.Component {
  static propTypes = {
    appList: PropTypes.array,
  };

  constructor(props) {
    super(props);
    const appList = props.appList;
    const defaultApp = appList.length !== 0 ? appList[0] : null;
    const app = props.location.query?.app
      ? props.location.query.app
      : defaultApp
      ? defaultApp.name
      : null;
    const envMap = app
      ? appList.filter(appObj => appObj.name === app)[0].environments || {}
      : {};
    const envList = Object.keys(envMap);
    const env = envList.length ? envList[0] : null;
    const defaultRef = env ? envMap[env].defaultRef : 'master';

    this.state = {
      app,
      env,
      envMap,
      ref: defaultRef,
      submitInProgress: false,
      submitError: null,
    };
  }

  onChangeApplication = e => {
    const val = e.target.value;
    const envMap = val
      ? this.props.appList.filter(app => {
          return app.name === val;
        })[0].environments || {}
      : {};
    const envList = Object.keys(envMap);
    const env = envList.length ? envList[0] : null;
    this.setState({
      app: val,
      envMap,
      env,
      ref: env ? env.defaultRef : 'master',
    });
  };

  onChangeEnvironment = e => {
    const val = e.target.value;
    const config = val ? this.state.envMap[val] || {} : {};
    this.setState({
      env: val,
      ref: config.defaultRef || 'master',
    });
  };

  onChangeRef = e => {
    this.setState({
      ref: e.target.value,
    });
  };

  onSubmit = e => {
    e.preventDefault();

    if (this.state.submitInProgress) {
      return;
    }

    const startDeploy = async () => {
      const deployResp = await api.request('/deploys/', {
        method: 'POST',
        data: {
          app: this.state.app,
          env: this.state.env,
          ref: this.state.ref,
        },
      });

      const result = await deployResp.json();

      if (deployResp.ok) {
        this.gotoDeploy(result);
      } else {
        this.setState({
          submitError: result.error,
          submitInProgress: false,
        });
      }
    };

    // Ensure we don't double trigger a deploy by using the setState callback
    this.setState({submitInProgress: true}, startDeploy);
  };

  gotoDeploy = deploy => {
    const {app, environment, number} = deploy;
    browserHistory.push(`/deploys/${app.name}/${environment}/${number}`);
  };

  render() {
    return (
      <div className="create-deploy">
        <div className="section">
          <div className="section-header">
            <h2>Create Deploy</h2>
          </div>
          {this.state.submitError && (
            <div className="alert alert-block alert-danger">
              <strong>Unable to create deploy:</strong>
              <span>{this.state.submitError}</span>
            </div>
          )}
          <form onSubmit={this.onSubmit}>
            <div className="form-group">
              <label>Application</label>
              <select
                className="form-control"
                value={this.state.app}
                onChange={this.onChangeApplication}
              >
                {this.props.appList.map(app => {
                  return <option key={app.name}>{app.name}</option>;
                })}
              </select>
            </div>
            <div className="form-group">
              <label>Environment</label>
              <select
                className="form-control"
                value={this.state.env}
                onChange={this.onChangeEnvironment}
              >
                {Object.keys(this.state.envMap).map(env => {
                  return <option key={env}>{env}</option>;
                })}
              </select>
            </div>
            <div className="form-group">
              <label>Ref</label>
              <input
                type="text"
                className="form-control"
                onChange={this.onChangeRef}
                placeholder="e.g. master"
                value={this.state.ref}
              />
            </div>
            <div className="submit-group">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={this.state.submitInProgress}
              >
                Ship It!
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }
}

export default CreateDeploy;
