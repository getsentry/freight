import jQuery from "jquery";
import React from "react";
import Router from "react-router";

import api from "../api";

var CreateDeploy = React.createClass({
  mixins: [Router.Navigation],

  contextTypes: {
    router: React.PropTypes.func
  },

  getInitialState() {
    let appList = this.props.appList;
    let defaultApp = appList.length !== 0 ? appList[0] : null;
    let defaultEnv = defaultApp ? defaultApp.environments[0] : null;
    let defaultRef = defaultEnv ? defaultEnv.defaultRef : 'master';

    return {
      app: defaultApp ? defaultApp.name : null,
      env: defaultEnv ? defaultEnv.name : null,
      envList: defaultApp ? defaultApp.environments : [],
      ref: defaultRef,
      submitInProgress: false
    };
  },

  onChangeApplication(e) {
    let val = jQuery(e.target).val();
    this.setState({
      app: val,
      envList: val ? this.props.appList.filter((app) => {
        return app.name === val;
      })[0].environments || [] : []
    });
  },

  onChangeEnvironment(e) {
    let val = jQuery(e.target).val();
    this.setState({
      env: val,
      ref: val ? this.state.envList.filter((env) => {
        return env.name === val;
      })[0].defaultRef || 'master' : 'master'
    });
  },

  onChangeRef(e) {
    this.setState({
      ref: jQuery(e.target).val()
    });
  },

  onSubmit(e) {
    e.preventDefault();

    if (this.state.submitInProgress) {
      return false;
    }

    this.setState({
      submitInProgress: true,
    });

    api.request('/tasks/', {
      method: 'POST',
      data: {
        app: this.state.app,
        env: this.state.env,
        ref: this.state.ref
      },
      success: (data) => {
        this.gotoTask(data);
      }
    });
  },


  gotoTask(task) {
    this.transitionTo('taskDetails', {
      app: task.app.name,
      env: task.environment,
      number: task.number
    });
  },

  render() {
    return (
      <div className="create-deploy">
        <div className="section">
          <div className="section-header">
            <h2>Create Deploy</h2>
          </div>
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
                {this.state.envList.map((env) => {
                  return <option key={env.name}>{env.name}</option>
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
