import React from 'react';
import createReactClass from 'create-react-class';
import PropTypes from 'prop-types';

import api from 'app/api';
import DeployChart from 'app/components/DeployChart';
import LoadingIndicator from 'app/components/LoadingIndicator';
import TaskSummary from 'app/components/TaskSummary';
import PollingMixin from 'app/mixins/polling';
import pushNotification from 'app/pushNotification';

const Overview = createReactClass({
  displayName: 'Overview',

  contextTypes: {
    router: PropTypes.object,
  },

  mixins: [PollingMixin],

  getInitialState() {
    return {
      deploys: [],
    };
  },

  async componentWillMount() {
    const deploysResp = await api.request(this.getPollingUrl());
    const deploys = await deploysResp.json();

    this.setState({deploys});
  },

  componentDidUpdate(_prevProps, prevState) {
    const previousTasks = {};

    prevState.deploys.forEach(task => {
      previousTasks[task.id] = task;
    });

    this.state.deploys.forEach(task => {
      if (
        task.status === 'finished' &&
        previousTasks[task.id] &&
        previousTasks[task.id].status === 'in_progress'
      ) {
        const {name} = task.app;
        const {environment, number} = task;
        const path = `/deploys/${name}/${environment}/${number}`;
        pushNotification(task, path);
      }
    });
  },

  getPollingUrl() {
    return '/deploys/';
  },

  pollingReceiveData(data) {
    this.setState({
      deploys: data,
    });
  },

  deployInProgress(deploy) {
    return deploy.status === 'in_progress';
  },

  deployPending(deploy) {
    return deploy.status === 'pending';
  },

  render() {
    if (this.state.deploys === null) {
      return (
        <div className="container" style={{textAlign: 'center'}}>
          <LoadingIndicator>
            <p>Loading list of deploys.</p>
          </LoadingIndicator>
        </div>
      );
    }

    if (window.Notification && Notification.permission !== 'denied') {
      Notification.requestPermission();
    }

    const activedeployNodes = [];
    const pendingdeployNodes = [];
    const previousdeployNodes = [];

    this.state.deploys.forEach(deploy => {
      const node = <TaskSummary key={deploy.id} task={deploy} />;
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
          {activedeployNodes.length || pendingdeployNodes.length ? (
            <div className="deploy-list">
              {activedeployNodes}
              {pendingdeployNodes}
            </div>
          ) : (
            <p>There are no active deploys.</p>
          )}
        </div>

        <div className="section">
          <div className="section-header">
            <h2>Deploy History</h2>
          </div>

          <DeployChart />

          {previousdeployNodes.length ? (
            <div className="deploy-list">{previousdeployNodes}</div>
          ) : (
            <p>There are no historical deploys.</p>
          )}
        </div>
      </div>
    );
  },
});

export default Overview;
