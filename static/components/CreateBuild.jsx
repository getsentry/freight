import jQuery from "jquery";
import React from "react";

import { browserHistory } from 'react-router';

import api from "../api";
import CreateDeploy from "./CreateDeploy";
import CreateCraftRelease from "./CreateCraftRelease";


const TYPE_DEPLOY = 0;
const TYPE_CRAFT_RELEASE = 1;


var CreateBuild = React.createClass({

  contextTypes: {
    router: React.PropTypes.func
  },

  getInitialState() {
    let appList = this.props.appList;
    let defaultApp = appList.length !== 0 ? appList[0] : null;
    return {
      app: defaultApp,
      submitInProgress: false,
      submitError: null,
    };
  },

  CreateBuildType(props) {
    const refFunc = instance => { this.child = instance }
    if (this.state.app.type === TYPE_CRAFT_RELEASE) {
      // TODO pass props properly
      return <CreateCraftRelease {...props} ref={refFunc} />;
    } else {
      return <CreateDeploy {...props} ref={refFunc} />
    }
  },

  onChangeApplication(e) {
    const val = jQuery(e.target).val();
    const app = this.props.appList.find(appObject => appObject.name === val);
    this.setState({
      app,
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
        data: this.child.getBuildData(),
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
    let { app, environment, number } = deploy;
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
                value={this.state.app.name}
                onChange={this.onChangeApplication}>
                {this.props.appList.map((app) => {
                  return <option key={app.name}>{app.name}</option>
                })}
              </select>
            </div>
            <this.CreateBuildType app={this.state.app} />
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

export default CreateBuild;
