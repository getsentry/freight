import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';
import createReactClass from '/web_modules/create-react-class.js';
import api from '../api.js';
import DeployChart from './DeployChart.js';
import LoadingIndicator from './LoadingIndicator.js';
import PollingMixin from '../mixins/polling.js';
import TaskSummary from './TaskSummary.js';
import pushNotification from '../pushNotification.js';
const Overview = createReactClass({
  displayName: 'Overview',
  contextTypes: {
    router: PropTypes.object
  },
  mixins: [PollingMixin],

  getInitialState() {
    return {
      deploys: []
    };
  },

  componentWillMount() {
    api.request(this.getPollingUrl(), {
      success: data => {
        console.log(data);
        this.setState({
          deploys: data
        });
      }
    });
  },

  componentDidUpdate(prevProps, prevState) {
    const previousTasks = {};
    prevState.deploys.forEach(task => {
      previousTasks[task.id] = task;
    });
    this.state.deploys.forEach(task => {
      if (task.status === 'finished' && previousTasks[task.id] && previousTasks[task.id].status === 'in_progress') {
        const {
          name
        } = task.app;
        const {
          environment,
          number
        } = task;
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
      return /*#__PURE__*/React.createElement("div", {
        className: "container",
        style: {
          textAlign: 'center'
        }
      }, /*#__PURE__*/React.createElement(LoadingIndicator, null, /*#__PURE__*/React.createElement("p", null, "Loading list of deploys.")));
    }

    if (window.Notification && Notification.permission !== 'denied') {
      Notification.requestPermission();
    }

    const activedeployNodes = [];
    const pendingdeployNodes = [];
    const previousdeployNodes = [];
    this.state.deploys.forEach(deploy => {
      const node = /*#__PURE__*/React.createElement(TaskSummary, {
        key: deploy.id,
        task: deploy
      });

      if (this.deployInProgress(deploy)) {
        activedeployNodes.unshift(node);
      } else if (this.deployPending(deploy)) {
        pendingdeployNodes.unshift(node);
      } else {
        previousdeployNodes.push(node);
      }
    });
    return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
      className: "section"
    }, /*#__PURE__*/React.createElement("div", {
      className: "section-header"
    }, /*#__PURE__*/React.createElement("h2", null, "Active Deploys")), activedeployNodes.length || pendingdeployNodes.length ? /*#__PURE__*/React.createElement("div", {
      className: "deploy-list"
    }, activedeployNodes, pendingdeployNodes) : /*#__PURE__*/React.createElement("p", null, "There are no active deploys.")), /*#__PURE__*/React.createElement("div", {
      className: "section"
    }, /*#__PURE__*/React.createElement("div", {
      className: "section-header"
    }, /*#__PURE__*/React.createElement("h2", null, "Deploy History")), /*#__PURE__*/React.createElement(DeployChart, null), previousdeployNodes.length ? /*#__PURE__*/React.createElement("div", {
      className: "deploy-list"
    }, previousdeployNodes) : /*#__PURE__*/React.createElement("p", null, "There are no historical deploys.")));
  }

});
export default Overview;