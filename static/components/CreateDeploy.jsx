import jQuery from "jquery";
import React from "react";
import Router from "react-router";

import api from "../api";

import { browserHistory } from 'react-router';

var CreateDeploy = React.createClass({

  contextTypes: {
    router: React.PropTypes.func
  },

  getInitialState() {
    let appList    = this.props.appList;
    let defaultApp = appList.length !== 0 ? appList[0] : null;
    let defaultEnv = defaultApp ? Object.keys(defaultApp.environments)[0] : null;
    let envMap     = defaultApp ? defaultApp.environments : {};
    let defaultRef = defaultEnv ? envMap[defaultEnv].defaultRef : 'master';

    return {
      app: defaultApp ? defaultApp.name : null,
      env: defaultEnv ? defaultEnv.name : null,
      envMap: envMap,
      ref: defaultRef,
      submitInProgress: false,
      submitError: null,
    };
  },

  onChangeApplication(e) {
    let val    = jQuery(e.target).val();
    let envMap = val ? this.props.appList.filter((app) => {
      return app.name === val;
    })[0].environments || {} : {};
    let envList = Object.keys(envMap);
    let env     = envList.length ? envList[0] : null;
    this.setState({
      app: val,
      envMap: envMap,
      env: env,
      ref: env ? env.defaultRef : 'master',
    });
  },

  onChangeEnvironment(e) {
    let val = jQuery(e.target).val();
    let config = val ? this.state.envMap[val] || {} : {};
    this.setState({
      env: val,
      ref: config.defaultRef || 'master',
    });
  },

  onChangeRef(e) {
    this.setState({
      ref: e.target.value,
    });
  },

  onSubmit(e) {
    e.preventDefault();

    if (this.state.submitInProgress) {
      return false;
    }

    this.setState({
      submitInProgress: true,
    }, () => {
      api.request('/deploys/', {
        method: 'POST',
        data: {
          app: this.state.app,
          env: this.state.env,
          ref: this.state.ref
        },
        success: (data) => {
          this.gotoDeploy(data);
        },
        error: (response) => {
          this.setState({
            submitError: response.responseJSON['error'],
            submitInProgress: false,
          });
        },
      });
    });
  },

  gotoDeploy(deploy) {
    let {app, environment, number} = deploy;
    browserHistory.push(`/deploys/${app.name}/${environment}/${number}`);
  },

  render() {
    return (
      <div className="create-deploy">
        <div className="section">
          <div className="section-header">
            <h2>Create Deploy</h2>
          </div>
          {this.state.submitError &&
            <div className="alert alert-block alert-danger">
              <strong>Unable to create deploy:</strong>
              <span>{this.state.submitError}</span>
            </div>
          }
          <form onSubmit={this.onSubmit}>
            <div className="form-group">
              <label>Application</label>
              <select className="form-control"
                      value={this.state.app}
                      onChange={this.onChangeApplication}>
                {this.props.appList.map((app) => {
                  return <option key={app.name}>{app.name}</option>
                })}
              </select>
            </div>
            <div className="form-group">
              <label>Environment</label>
              <select className="form-control"
                      value={this.state.env}
                      onChange={this.onChangeEnvironment}>
                {Object.keys(this.state.envMap).map((env) => {
                  return <option key={env}>{env}</option>
                })}
              </select>
            </div>
            <div className="form-group">
              <label>Ref</label>
              <input type="text" className="form-control"
                     onChange={this.onChangeRef}
                     placeholder="e.g. master" value={this.state.ref} />
            </div>
            <div className="submit-group">
              <button type="submit" className="btn btn-primary"
                      disabled={this.state.submitInProgress}>Ship It!</button>
            </div>
          </form>
        </div>
      </div>
    );
  }
});

export default CreateDeploy;
