import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';
import createReactClass from '/web_modules/create-react-class.js';
import api from '../api.js';
import DeployChart from './DeployChart.js';
import LoadingIndicator from './LoadingIndicator.js';
import PollingMixin from '../mixins/polling.js';
import TaskSummary from './TaskSummary.js';
const AppDetails = createReactClass({
  displayName: 'AppDetails',
  mixins: [PollingMixin],

  getInitialState() {
    return {
      appId: this.props.params.app,
      app: null,
      tasks: null
    };
  },

  componentWillMount() {
    api.request(this.getAppUrl(), {
      success: data => {
        this.setState({
          app: data
        });
      },
      error: err => {
        const error = err && err.status === 404 ? `Invalid application: ${this.props.params.app}` : 'Error fetching data';
        this.setState({
          error
        });
      }
    });
    api.request(this.getPollingUrl(), {
      success: data => {
        this.setState({
          tasks: data
        });
      }
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
    if (this.state.error) {
      return /*#__PURE__*/React.createElement("h2", null, this.state.error);
    }

    if (this.state.tasks === null || this.state.app === null) {
      return /*#__PURE__*/React.createElement(LoadingIndicator, null);
    }

    const {
      app,
      tasks
    } = this.state;
    const activeTaskNodes = [];
    const pendingTaskNodes = [];
    const previousTaskNodes = [];
    tasks.forEach(task => {
      const node = /*#__PURE__*/React.createElement(TaskSummary, {
        key: task.id,
        task: task
      });

      if (this.taskInProgress(task)) {
        activeTaskNodes.unshift(node);
      } else if (this.taskPending(task)) {
        pendingTaskNodes.unshift(node);
      } else {
        previousTaskNodes.push(node);
      }
    });
    return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
      className: "section"
    }, /*#__PURE__*/React.createElement("div", {
      className: "section-header"
    }, /*#__PURE__*/React.createElement("h2", null, app.name, " - Active Deploys")), activeTaskNodes.length || pendingTaskNodes.length ? /*#__PURE__*/React.createElement("div", {
      className: "deploy-list"
    }, activeTaskNodes, pendingTaskNodes) : /*#__PURE__*/React.createElement("p", null, "There are no active deploys.")), /*#__PURE__*/React.createElement("div", {
      className: "section"
    }, /*#__PURE__*/React.createElement("div", {
      className: "section-header"
    }, /*#__PURE__*/React.createElement("h2", null, app.name, " - Deploy History")), /*#__PURE__*/React.createElement(DeployChart, {
      app: app.name
    }), previousTaskNodes.length ? /*#__PURE__*/React.createElement("div", {
      className: "deploy-list"
    }, previousTaskNodes) : /*#__PURE__*/React.createElement("p", null, "There are no historical deploys.")));
  }

});
export default AppDetails;