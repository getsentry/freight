/** @jsx React.DOM */

var React = require('react');

var api = require('../api');

var PollingMixin = require('../mixins/polling');
var TaskSummary = require('./TaskSummary');


var Overview = React.createClass({
  mixins: [PollingMixin],

  getInitialState() {
    return {
      loading: true,
      tasks: []
    };
  },

  componentWillMount() {
    api.request(this.getPollingUrl(), {
      success: (data) => {
        this.setState({
          loading: false,
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
    return task.status == 'in_progress' || task.status == 'pending';
  },

  render() {
    if (this.state.loading) {
      return <div className="loading" />;
    }

    var activeTaskNodes = this.state.tasks.filter((task) => {
      return this.taskInProgress(task);
    }).map((task) => {
      return (
        <li key={task.id}>
          <TaskSummary task={task} />
        </li>
      );
    });

    var previousTaskNodes = this.state.tasks.filter((task) => {
      return !this.taskInProgress(task);
    }).map((task) => {
      return (
        <li key={task.id}>
          <TaskSummary task={task} />
        </li>
      );
    });

    return (
      <div>
        <h2>Active Deploys</h2>
        {activeTaskNodes.length ?
          <ul className="task-list">
            {activeTaskNodes}
          </ul>
        :
          <p>There are no active tasks.</p>
        }

        <h2>Deploy History</h2>
        {previousTaskNodes.length ?
          <ul className="task-list">
            {previousTaskNodes}
          </ul>
        :
          <p>There are no historical tasks.</p>
        }
      </div>
    );
  }
});

module.exports = Overview;
