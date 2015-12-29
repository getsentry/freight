var React = require('react');

var api = require('../api');

var DeployChart = require("./DeployChart");
import LoadingIndicator from './LoadingIndicator';
var PollingMixin = require('../mixins/polling');
var TaskSummary = require('./TaskSummary');

var Overview = React.createClass({
  mixins: [PollingMixin],

  contextTypes: {
    router: React.PropTypes.func
  },

  getInitialState() {
    return {
      tasks: null,
    };
  },

  componentWillMount() {
    api.request(this.getPollingUrl(), {
      success: (data) => {
        this.setState({
          tasks: data
        });
      }
    });
  },

  getPollingUrl() {
    return '/tasks/';
  },

  pollingReceiveData(data) {
    this.setState({
      tasks: data
    });
  },

  taskInProgress(task) {
    return task.status == 'in_progress';
  },

  taskPending(task) {
    return task.status == 'pending';
  },

  render() {
    if (this.state.tasks === null) {
      return (
        <div className="container" style={{textAlign: "center"}}>
          <LoadingIndicator>
            <p>Loading list of tasks.</p>
          </LoadingIndicator>
        </div>
      );
    }

    var activeTaskNodes = [];
    var pendingTaskNodes = [];
    var previousTaskNodes = [];

    this.state.tasks.forEach((task) => {
      var node = <TaskSummary key={task.id} task={task} />;
      if (this.taskInProgress(task)) {
        activeTaskNodes.unshift(node);
      } else if (this.taskPending(task)) {
        pendingTaskNodes.unshift(node);
      } else {
        previousTaskNodes.push(node);
      }
    });

    return (
      <div>
        <div className="section">
          <div className="section-header">
            <h2>Active Deploys</h2>
          </div>
          {(activeTaskNodes.length || pendingTaskNodes.length) ?
            <div className="task-list">
              {activeTaskNodes}
              {pendingTaskNodes}
            </div>
          :
            <p>There are no active tasks.</p>
          }
        </div>

        <div className="section">
          <div className="section-header">
            <h2>Deploy History</h2>
          </div>

          <DeployChart />

          {previousTaskNodes.length ?
            <div className="task-list">
              {previousTaskNodes}
            </div>
          :
            <p>There are no historical tasks.</p>
          }
        </div>
      </div>
    );
  }
});

export default Overview;
