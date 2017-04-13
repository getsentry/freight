const React = require('react');
const Router = require('react-router');

const api = require('../api');

import LoadingIndicator from './LoadingIndicator';
const PollingMixin = require('../mixins/polling');
const TaskSummary = require('./TaskSummary');

const AppDetails = React.createClass({
  mixins: [PollingMixin, Router.State],

  contextTypes: {
    setHeading: React.PropTypes.func,
  },

  getInitialState() {
    return {
      appId: this.getParams().app,
      app: null,
      tasks: null,
    };
  },

  componentWillMount() {
    api.request(this.getAppUrl(), {
      success: (data) => {
        this.setState({
          app: data
        });
        this.context.setHeading(data.name);
      }
    });
    api.request(this.getPollingUrl(), {
      success: (data) => {
        this.setState({
          tasks: data
        });
      }
    });
  },

  componentWillUnmount() {
    this.context.setHeading(null);
  },

  getAppUrl() {
    return '/apps/' + this.state.appId + '/';
  },

  getPollingUrl() {
    return '/tasks/?app=' + this.state.appId;
  },

  pollingReceiveData(data) {
    this.setState({
      tasks: data
    });
  },

  taskInProgress(task) {
    return task.status === 'in_progress';
  },

  taskPending(task) {
    return task.status === 'pending';
  },

  render() {
    if (this.state.tasks === null || this.state.app === null) {
      return <LoadingIndicator />;
    }

    const {app, tasks} = this.state;
    const activeTaskNodes = [];
    const pendingTaskNodes = [];
    const previousTaskNodes = [];

    tasks.forEach((task) => {
      const node = <TaskSummary key={task.id} task={task} />;
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
            <h2>{app.name} Deploys</h2>
          </div>
          {tasks.length ?
            <ul className="task-list">
              {activeTaskNodes}
              {pendingTaskNodes}
              {previousTaskNodes}
            </ul>
          :
            <p>There have been no deploys for this app.</p>
          }
        </div>
      </div>
    );
  }
});

export default AppDetails;
