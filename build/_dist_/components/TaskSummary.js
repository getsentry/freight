function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

import { browserHistory } from '/web_modules/react-router.js';
import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';
import classnames from '/web_modules/classnames.js';
import Duration from './Duration.js';
import TimeSince from './TimeSince.js';

class Progress extends React.Component {
  render() {
    return /*#__PURE__*/React.createElement("span", {
      className: "progress",
      style: {
        width: this.props.value + '%'
      }
    });
  }

}

_defineProperty(Progress, "propTypes", {
  value: PropTypes.number.isRequired
});

class TaskSummary extends React.Component {
  constructor(...args) {
    super(...args);

    _defineProperty(this, "taskInProgress", task => {
      return task.status == 'in_progress' || task.status == 'pending';
    });

    _defineProperty(this, "getEstimatedProgress", task => {
      if (task.dateFinished) {
        return 100;
      }

      const started = new Date(task.dateStarted).getTime();

      if (!started) {
        return 0;
      }

      const now = Math.max(new Date().getTime(), started);
      return parseInt(Math.min((now - started) / 1000 / task.estimatedDuration * 100, 95), 10);
    });

    _defineProperty(this, "getStatusLabel", task => {
      switch (task.status) {
        case 'cancelled':
          return 'Cancelled';

        case 'failed':
          return 'Failed';

        case 'finished':
          return 'Finished';

        case 'pending':
          return 'Pending';

        case 'in_progress':
          return 'In progress';

        default:
          return 'Unknown';
      }
    });

    _defineProperty(this, "gotoTask", e => {
      if (e) {
        e.preventDefault();
      }

      const {
        app,
        environment,
        number
      } = this.props.task;
      browserHistory.push(`/deploys/${app.name}/${environment}/${number}`);
    });
  }

  render() {
    const task = this.props.task;
    let className = 'deploy';

    if (this.taskInProgress(task)) {
      className += ' active';
    } else {
      className += ' finished';
    }

    if (task.status === 'failed') {
      className += ' failed';
    } else if (task.status === 'cancelled') {
      className += ' cancelled';
    }

    return /*#__PURE__*/React.createElement("div", {
      className: classnames(this.props.className, className),
      onClick: this.gotoTask
    }, /*#__PURE__*/React.createElement(Progress, {
      value: this.getEstimatedProgress(task)
    }), /*#__PURE__*/React.createElement("h3", null, task.name), /*#__PURE__*/React.createElement("div", {
      className: "ref"
    }, /*#__PURE__*/React.createElement("div", {
      className: "sha"
    }, task.sha.substr(0, 7)), task.ref), /*#__PURE__*/React.createElement("div", {
      className: "meta"
    }, task.status == 'pending' && /*#__PURE__*/React.createElement("small", null, /*#__PURE__*/React.createElement("strong", null, "QUEUED"), " \u2014", ' '), task.dateFinished ? /*#__PURE__*/React.createElement("small", null, this.getStatusLabel(task), " ", /*#__PURE__*/React.createElement(TimeSince, {
      date: task.dateFinished
    }), " \u2014", ' ', /*#__PURE__*/React.createElement(Duration, {
      seconds: task.duration,
      className: "duration"
    })) : task.dateStarted ? /*#__PURE__*/React.createElement("small", null, "Started ", /*#__PURE__*/React.createElement(TimeSince, {
      date: task.dateStarted
    })) : /*#__PURE__*/React.createElement("small", null, "Created ", /*#__PURE__*/React.createElement(TimeSince, {
      date: task.dateCreated
    })), /*#__PURE__*/React.createElement("small", null, " \u2014 by ", task.user.name)));
  }

}

_defineProperty(TaskSummary, "propTypes", {
  task: PropTypes.shape({
    app: PropTypes.shape({
      name: PropTypes.string
    }),
    environment: PropTypes.string,
    number: PropTypes.number
  })
});

_defineProperty(TaskSummary, "contextTypes", {
  router: PropTypes.object.isRequired
});

export default TaskSummary;