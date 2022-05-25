import React from 'react';
import createReactClass from 'create-react-class';

import api from '../api';
import PollingMixin from '../mixins/polling';

import DeployChart from './DeployChart';
import LoadingIndicator from './LoadingIndicator';
import TaskSummary from './TaskSummary';

const AppDetails = createReactClass({
  displayName: 'AppDetails',

  mixins: [PollingMixin],

  getInitialState() {
    return {
      appId: this.props.params.app,
      app: null,
      tasks: null,
    };
  },

  componentWillMount() {
    api.request(this.getAppUrl(), {
      success: data => {
        this.setState({
          app: data,
        });
      },
      error: err => {
        const error =
          err && err.status === 404
            ? `Invalid application: ${this.props.params.app}`
            : 'Error fetching data';
        this.setState({error});
      },
    });
    api.request(this.getPollingUrl(), {
      success: data => {
        this.setState({
          tasks: data,
        });
      },
    });
  },

  getAppUrl() {
    return '/apps/' + this.state.appId + '/';
  },

  getPollingUrl() {
    return '/tasks/?app=' + this.state.appId;
  },

  pollingReceiveData(data) {
    this.setState({
      tasks: data,
    });
  },

  taskInProgress(task) {
    return task.status === 'in_progress';
  },

  taskPending(task) {
    return task.status === 'pending';
  },

  render() {
    if (this.state.error) {
      return <h2>{this.state.error}</h2>;
    }

    if (this.state.tasks === null || this.state.app === null) {
      return <LoadingIndicator />;
    }

    const {app, tasks} = this.state;
    const activeTaskNodes = [];
    const pendingTaskNodes = [];
    const previousTaskNodes = [];

    tasks.forEach(task => {
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
            <h2>{app.name} - Active Deploys</h2>
          </div>

          {activeTaskNodes.length || pendingTaskNodes.length ? (
            <div className="deploy-list">
              {activeTaskNodes}
              {pendingTaskNodes}
            </div>
          ) : (
            <p>There are no active deploys.</p>
          )}
        </div>

        <div className="section">
          <div className="section-header">
            <h2>{app.name} - Deploy History</h2>
          </div>

          <DeployChart app={app.name} />

          {previousTaskNodes.length ? (
            <div className="deploy-list">{previousTaskNodes}</div>
          ) : (
            <p>There are no historical deploys.</p>
          )}
        </div>
      </div>
    );
  },
});

export default AppDetails;
