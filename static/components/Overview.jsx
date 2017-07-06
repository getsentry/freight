var React = require('react');

var api = require('../api');

var DeployChart = require("./DeployChart");
import LoadingIndicator from './LoadingIndicator';
var PollingMixin = require('../mixins/polling');
var TaskSummary = require('./TaskSummary');

var Overview = React.createClass({

  contextTypes: {
    router: React.PropTypes.func
  },

  getInitialState() {
    return {
      deploys: null,
    };
  },

  componentWillMount() {
    api.request(this.getPollingUrl(), {
      success: (data) => {
        this.setState({
          deploys: data
        });
      }
    });
  },

  getPollingUrl() {
    return '/deploys/';
  },

  pollingReceiveData(data) {
    this.setState({
      deploys: data
    });
  },

  deployInProgress(deploy) {
    return deploy.status == 'in_progress';
  },

  deployPending(deploy) {
    return deploy.status == 'pending';
  },

  render() {
    if (this.state.deploys === null) {
      return (
        <div className="container" style={{textAlign: "center"}}>
          <LoadingIndicator>
            <p>Loading list of deploys.</p>
          </LoadingIndicator>
        </div>
      );
    }

    var activedeployNodes = [];
    var pendingdeployNodes = [];
    var previousdeployNodes = [];

    this.state.deploys.forEach((deploy) => {
      var node = <TaskSummary key={deploy.id} task={deploy} />;
      if (this.deployInProgress(deploy)) {
        activedeployNodes.unshift(node);
      } else if (this.deployPending(deploy)) {
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
          {(activedeployNodes.length || pendingdeployNodes.length) ?
            <div className="deploy-list">
              {activedeployNodes}
              {pendingdeployNodes}
            </div>
          :
            <p>There are no active deploys.</p>
          }
        </div>

        <div className="section">
          <div className="section-header">
            <h2>Deploy History</h2>
          </div>

          <DeployChart />

          {previousdeployNodes.length ?
            <div className="deploy-list">
              {previousdeployNodes}
            </div>
          :
            <p>There are no historical deploys.</p>
          }
        </div>
      </div>
    );
  }
});

export default Overview;
