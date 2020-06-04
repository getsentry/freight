function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

import { browserHistory } from '/web_modules/react-router.js';
import ansi_up from '/web_modules/ansi_up.js';
import createReactClass from '/web_modules/create-react-class.js';
import linkifyUrls from '/web_modules/linkify-urls.js';
import moment from '/web_modules/moment.js';
import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';
import api from '../api.js';
import Duration from './Duration.js';
import LoadingIndicator from './LoadingIndicator.js';
import PollingMixin from '../mixins/polling.js';
import TimeSince from './TimeSince.js';
import pushNotification from '../pushNotification.js';
import FaviconStatus from './FaviconStatus.js';

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

const TaskDetails = createReactClass({
  displayName: 'TaskDetails',
  mixins: [PollingMixin],

  getInitialState() {
    return {
      loading: true,
      logLoading: true,
      task: null,
      logNextOffset: 0,
      liveScroll: true,
      id: 0
    };
  },

  componentDidMount() {
    this.lastScrollPos = 0;
    this.logTimer = null;
    window.addEventListener('scroll', this.onScroll, false);
    this.fetchData();
  },

  componentWillReceiveProps(nextProps) {
    const params = this.props.params;
    const task = this.state.task;

    if (!task) {
      return;
    }

    if (params.app !== task.app.name || params.env !== task.environment || params.number !== task.number) {
      this.setState({
        loading: true,
        error: false,
        task: null
      }, this.fetchData());
    }
  },

  componentDidUpdate(prevProps, prevState) {
    const task = this.state.task;

    if (!task) {
      return;
    }

    if (prevState.task !== null && task.status === 'finished' && prevState.task.status === 'in_progress') {
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

    const hash = window.location.hash;

    if (this.state.liveScroll && hash == '' && prevState.logNextOffset !== this.state.logNextOffset) {
      this.scrollLog();
    }
  },

  componentWillUnmount() {
    window.removeEventListener('scroll', this.onScroll, false);

    if (this.logTimer) {
      window.clearTimeout(this.logTimer);
    }
  },

  fetchData() {
    if (this.logTimer) {
      window.clearTimeout(this.logTimer);
    }

    if (this.refs.log) {
      this.refs.log.innerHTML = '';
    }

    api.request(this.getPollingUrl(), {
      success: data => {
        this.setState({
          task: data,
          loading: false
        });
        this.pollLog();
      }
    });
  },

  onScroll(event) {
    const scrollTop = document.body.scrollTop;

    if (scrollTop < this.lastScrollPos) {
      this.setState({
        liveScroll: false
      });
    } else if (scrollTop + window.innerHeight == document.body.scrollHeight) {
      this.setState({
        liveScroll: true
      });
    }

    this.lastScrollPos = scrollTop;
  },

  getPollingUrl() {
    const {
      app,
      env,
      number
    } = this.props.params;
    return `/deploys/${app}/${env}/${number}/`;
  },

  pollingReceiveData(data) {
    this.setState({
      task: data
    });
  },

  splitLogData(data) {
    const text = data.chunks;
    const objLength = data.chunks.length;
    const obj = {
      lines: [],
      timeStamp: []
    };

    for (let i = 0; i < objLength; i++) {
      if (data.chunks[i] !== undefined) {
        obj.lines = [...obj.lines, text[i].text.split(/\n/)];
        obj.timeStamp = [...obj.timeStamp, data.chunks[i].date];
      }
    }

    return obj;
  },

  highLightDiv(el) {
    el.addEventListener('click', e => {
      const div = document.getElementById(e.target.id);
      const highlightedlines = document.getElementsByClassName('line highLighted');
      this.stopRefresh(e, e.target.href);

      if (div.className === 'line') {
        div.className = 'line highLighted';
      } else if (div.className === 'line highLighted') {
        div.className = 'line';
        this.stopRefresh(e, e.target.href);
      }

      for (let l = 0; l < highlightedlines.length; l++) {
        if (highlightedlines[l].className === 'line highLighted') {
          highlightedlines[l].className = 'line';
          div.className = 'line highLighted';
        } else {
          div.className = 'line';
        }
      }
    });
  },

  updateBuildLog(data) {
    // add each additional new line
    const logDataResults = this.splitLogData(data);
    const frag = document.createDocumentFragment();
    const lineItem = logDataResults.lines;
    const hash = window.location.hash;

    for (let j = 0; j < lineItem.length; j++) {
      for (let k = 0; k < lineItem[j].length; k++) {
        const div = document.createElement('div');
        const time = document.createElement('a'); // TODO look into this
        // eslint-disable-next-line

        const idIncrement = this.state.id++;
        div.className = 'line';
        time.className = 'time';
        div.id = 'L' + idIncrement;
        const {
          environment,
          number
        } = this.state.task;
        const {
          name
        } = this.state.task.app;
        time.href = `/deploys/${name}/${environment}/${number}#${div.id}`;
        time.id = div.id;
        /***********************************************************************
        This creates an eventlistener for each time element.
        Fine for current average log size(8-15-17), but memory usuage will spike
        for really big logs.
        ***********************************************************************/

        this.highLightDiv(time);
        const timer = new Date(logDataResults.timeStamp[j]);
        const timeMil = timer.getTime(); //Multiple by 60000 to convert offset to milliseconds

        const offset = timer.getTimezoneOffset() * 60000;
        const timezone = timeMil - offset;
        const newDate = new Date(timezone);
        div.innerHTML = ansi_up.ansi_to_html(linkifyUrls(lineItem[j][k], {
          attributes: {
            target: '_blank',
            rel: 'noreferrer noopener'
          }
        }));
        time.innerHTML = moment(newDate).parseZone().format('h:mm:ss a');
        div.appendChild(time);
        frag.appendChild(div);
      }
    }

    this.refs.log.appendChild(frag);
    this.centerHighlightedDiv();

    if (this.state.liveScroll && hash === '') {
      this.scrollLog();
    }
  },

  centerHighlightedDiv() {
    const hash = window.location.hash;

    if (hash !== '') {
      const divID = hash.replace(/[^\w\s]/g, '');
      const div = document.getElementById(divID);

      if (div) {
        const top = div.offsetTop - window.innerHeight / 4;
        div.scrollIntoView();
        window.scrollTo(0, top);
      }

      div.className = 'line highLighted';
    }
  },

  stopRefresh(event, timeId) {
    event.preventDefault();
    window.history.replaceState(null, null, `${timeId}`);
  },

  scrollLog() {
    window.scrollTo(0, document.body.scrollHeight);
  },

  taskInProgress(task) {
    return task.status === 'in_progress' || task.status === 'pending';
  },

  getEstimatedProgress(task) {
    if (task.dateFinished) {
      return 100;
    }

    const started = new Date(task.dateStarted).getTime();

    if (!started) {
      return 0;
    }

    const now = Math.max(new Date().getTime(), started);
    return parseInt(Math.min((now - started) / 1000 / task.estimatedDuration * 100, 95), 10);
  },

  pollLog() {
    const task = this.state.task;
    const url = '/deploys/' + task.app.name + '/' + task.environment + '/' + task.number + '/log/?offset=' + this.state.logNextOffset;

    if (!task) {
      return;
    }

    api.request(url, {
      success: data => {
        if (data.chunks.length > 0) {
          this.setState({
            logLoading: false,
            logNextOffset: data.nextOffset
          });
          this.updateBuildLog(data);
        }

        if (this.state.logLoading) {
          this.setState({
            logLoading: false
          });
        }

        if (this.taskInProgress(this.state.task)) {
          this.logTimer = window.setTimeout(this.pollLog, 1000);
        }
      },
      error: () => {
        this.logTimer = window.setTimeout(this.pollLog, 10000);
      }
    });
  },

  cancelTask() {
    const task = this.state.task;
    const url = '/deploys/' + task.app.name + '/' + task.environment + '/' + task.number + '/';
    api.request(url, {
      method: 'PUT',
      data: {
        status: 'cancelled'
      },
      success: data => {
        this.setState({
          task: data
        });
      },
      error: () => {
        // eslint-disable-next-line
        alert('Unable to cancel deploy.');
      }
    });
  },

  toggleLiveScroll() {
    const liveScroll = !this.state.liveScroll;
    this.setState({
      liveScroll
    });

    if (liveScroll) {
      this.scrollLog();
    }
  },

  reDeploy() {
    if (this.state.submitInProgress) {
      return;
    }

    this.setState({
      submitInProgress: true
    }, () => {
      const task = this.state.task;
      api.request('/deploys/', {
        method: 'POST',
        data: {
          app: task.app.name,
          env: task.environment,
          ref: task.sha
        },
        success: data => {
          //workaround is referenced from here: https://github.com/ReactTraining/react-router/issues/1982
          browserHistory.push('/');
          browserHistory.push(`/deploys/${data.app.name}/${data.environment}/${data.number}`);
        }
      });
    });
  },

  getStatusLabel(task) {
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
  },

  render() {
    if (this.state.loading) {
      return /*#__PURE__*/React.createElement("div", {
        style: {
          textAlign: 'center'
        }
      }, /*#__PURE__*/React.createElement(LoadingIndicator, {
        style: {
          marginBottom: 20
        }
      }, "Loading task details."));
    }

    if (window.Notification && Notification.permission !== 'denied') {
      Notification.requestPermission();
    }

    const task = this.state.task;
    const inProgress = this.taskInProgress(task);
    const estimatedProgress = this.getEstimatedProgress(task);
    let liveScrollClassName = 'btn btn-default btn-sm';

    if (this.state.liveScroll) {
      liveScrollClassName += ' btn-active';
    }

    let className = 'deploy-details';

    if (inProgress) {
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
      className: className
    }, /*#__PURE__*/React.createElement("div", {
      className: "deploy-log"
    }, this.state.logLoading ? /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: 'center'
      }
    }, /*#__PURE__*/React.createElement("div", {
      className: "loading"
    }), /*#__PURE__*/React.createElement("p", null, "Loading log history.")) : /*#__PURE__*/React.createElement("div", {
      ref: "log"
    }), !this.state.logLoading && inProgress && /*#__PURE__*/React.createElement("div", {
      className: "loading-icon"
    })), /*#__PURE__*/React.createElement("div", {
      className: "deploy-header"
    }, /*#__PURE__*/React.createElement("div", {
      className: "container"
    }, /*#__PURE__*/React.createElement("h3", null, task.name), /*#__PURE__*/React.createElement("div", {
      className: "ref"
    }, /*#__PURE__*/React.createElement("div", {
      className: "sha"
    }, task.sha.substr(0, 7)), task.ref), /*#__PURE__*/React.createElement("div", {
      className: "meta"
    }, task.status == 'pending' && /*#__PURE__*/React.createElement("small", null, /*#__PURE__*/React.createElement("strong", null, "QUEUED"), " \u2014", ' '), task.dateFinished ? /*#__PURE__*/React.createElement("small", null, this.getStatusLabel(task), " ", /*#__PURE__*/React.createElement(TimeSince, {
      date: task.dateFinished
    }), ' ', "\u2014 ", /*#__PURE__*/React.createElement(Duration, {
      seconds: task.duration,
      className: "duration"
    })) : task.dateStarted ? /*#__PURE__*/React.createElement("small", null, "Started ", /*#__PURE__*/React.createElement(TimeSince, {
      date: task.dateStarted
    })) : /*#__PURE__*/React.createElement("small", null, "Created ", /*#__PURE__*/React.createElement(TimeSince, {
      date: task.dateCreated
    })), /*#__PURE__*/React.createElement("small", null, " \u2014 by ", task.user.name)))), /*#__PURE__*/React.createElement("div", {
      className: "deploy-footer"
    }, /*#__PURE__*/React.createElement("div", {
      className: "container"
    }, /*#__PURE__*/React.createElement("div", {
      className: "deploy-actions"
    }, inProgress ? /*#__PURE__*/React.createElement("span", null, /*#__PURE__*/React.createElement("a", {
      className: "btn btn-danger btn-sm",
      onClick: this.cancelTask
    }, "Cancel"), /*#__PURE__*/React.createElement("a", {
      className: liveScrollClassName,
      onClick: this.toggleLiveScroll
    }, /*#__PURE__*/React.createElement("input", {
      type: "checkbox",
      defaultChecked: this.state.liveScroll
    }), /*#__PURE__*/React.createElement("span", null, "Follow"))) : /*#__PURE__*/React.createElement("a", {
      className: "btn btn-default btn-sm",
      disabled: this.state.submitInProgress,
      onClick: this.reDeploy
    }, "Re-deploy")), /*#__PURE__*/React.createElement("div", {
      className: "deploy-progress"
    }, /*#__PURE__*/React.createElement(FaviconStatus, {
      status: task.status,
      progress: estimatedProgress
    }), /*#__PURE__*/React.createElement(Progress, {
      value: estimatedProgress
    })))));
  }

});
export default TaskDetails;