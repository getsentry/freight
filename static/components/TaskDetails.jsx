import {browserHistory} from 'react-router';
import ansi_up from 'ansi_up';
import createReactClass from 'create-react-class';
import linkifyUrls from 'linkify-urls';
import moment from 'moment';
import PropTypes from 'prop-types';
import React from 'react';

import api from '../api';
import Duration from './Duration';
import LoadingIndicator from './LoadingIndicator';
import PollingMixin from '../mixins/polling';
import TimeSince from './TimeSince';
import pushNotification from '../pushNotification';

class Progress extends React.Component {
  static propTypes = {
    value: PropTypes.number.isRequired,
  };

  render() {
    return <span className="progress" style={{width: this.props.value + '%'}} />;
  }
}

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
      id: 0,
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

    if (
      params.app !== task.app.name ||
      params.env !== task.environment ||
      params.number !== task.number
    ) {
      this.setState(
        {
          loading: true,
          error: false,
          task: null,
        },
        this.fetchData()
      );
    }
  },

  componentDidUpdate(prevProps, prevState) {
    const task = this.state.task;

    if (!task) {
      return;
    }

    if (
      prevState.task !== null &&
      task.status === 'finished' &&
      prevState.task.status === 'in_progress'
    ) {
      const {name} = task.app;
      const {environment, number} = task;
      const path = `/deploys/${name}/${environment}/${number}`;

      pushNotification(task, path);
    }

    const hash = window.location.hash;

    if (
      this.state.liveScroll &&
      hash == '' &&
      prevState.logNextOffset !== this.state.logNextOffset
    ) {
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
          loading: false,
        });

        this.pollLog();
      },
    });
  },

  onScroll(event) {
    const scrollTop = document.body.scrollTop;
    if (scrollTop < this.lastScrollPos) {
      this.setState({liveScroll: false});
    } else if (scrollTop + window.innerHeight == document.body.scrollHeight) {
      this.setState({liveScroll: true});
    }
    this.lastScrollPos = scrollTop;
  },

  getPollingUrl() {
    const {app, env, number} = this.props.params;
    return `/deploys/${app}/${env}/${number}/`;
  },

  pollingReceiveData(data) {
    this.setState({
      task: data,
    });
  },

  splitLogData(data) {
    const text = data.chunks;
    const objLength = data.chunks.length;

    const obj = {
      lines: [],
      timeStamp: [],
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
        const time = document.createElement('a');

        // TODO look into this
        // eslint-disable-next-line
        const idIncrement = this.state.id++;

        div.className = 'line';
        time.className = 'time';
        div.id = 'L' + idIncrement;

        const {environment, number} = this.state.task;
        const {name} = this.state.task.app;

        time.href = `/deploys/${name}/${environment}/${number}#${div.id}`;
        time.id = div.id;

        /***********************************************************************
        This creates an eventlistener for each time element.
        Fine for current average log size(8-15-17), but memory usuage will spike
        for really big logs.
        ***********************************************************************/
        this.highLightDiv(time);

        const timer = new Date(logDataResults.timeStamp[j]);
        const timeMil = timer.getTime();
        //Multiple by 60000 to convert offset to milliseconds
        const offset = timer.getTimezoneOffset() * 60000;
        const timezone = timeMil - offset;
        const newDate = new Date(timezone);

        div.innerHTML = ansi_up.ansi_to_html(
          linkifyUrls(lineItem[j][k], {
            attributes: {
              target: '_blank',
              rel: 'noreferrer noopener',
            },
          })
        );
        time.innerHTML = moment(newDate)
          .parseZone()
          .format('h:mm:ss a');

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
    return parseInt(
      Math.min(((now - started) / 1000 / task.estimatedDuration) * 100, 95),
      10
    );
  },

  pollLog() {
    const task = this.state.task;
    const url =
      '/deploys/' +
      task.app.name +
      '/' +
      task.environment +
      '/' +
      task.number +
      '/log/?offset=' +
      this.state.logNextOffset;

    if (!task) {
      return;
    }

    api.request(url, {
      success: data => {
        if (data.chunks.length > 0) {
          this.setState({
            logLoading: false,
            logNextOffset: data.nextOffset,
          });
          this.updateBuildLog(data);
        }
        if (this.state.logLoading) {
          this.setState({
            logLoading: false,
          });
        }
        if (this.taskInProgress(this.state.task)) {
          this.logTimer = window.setTimeout(this.pollLog, 1000);
        }
      },
      error: () => {
        this.logTimer = window.setTimeout(this.pollLog, 10000);
      },
    });
  },

  cancelTask() {
    const task = this.state.task;

    const url =
      '/deploys/' + task.app.name + '/' + task.environment + '/' + task.number + '/';

    api.request(url, {
      method: 'PUT',
      data: {
        status: 'cancelled',
      },
      success: data => {
        this.setState({
          task: data,
        });
      },
      error: () => {
        // eslint-disable-next-line
        alert('Unable to cancel deploy.');
      },
    });
  },

  toggleLiveScroll() {
    const liveScroll = !this.state.liveScroll;
    this.setState({
      liveScroll,
    });
    if (liveScroll) {
      this.scrollLog();
    }
  },

  reDeploy() {
    if (this.state.submitInProgress) {
      return;
    }

    this.setState(
      {
        submitInProgress: true,
      },
      () => {
        const task = this.state.task;
        api.request('/deploys/', {
          method: 'POST',
          data: {
            app: task.app.name,
            env: task.environment,
            ref: task.sha,
          },
          success: data => {
            //workaround is referenced from here: https://github.com/ReactTraining/react-router/issues/1982
            browserHistory.push('/');
            browserHistory.push(
              `/deploys/${data.app.name}/${data.environment}/${data.number}`
            );
          },
        });
      }
    );
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
      return (
        <div style={{textAlign: 'center'}}>
          <LoadingIndicator style={{marginBottom: 20}}>
            Loading task details.
          </LoadingIndicator>
        </div>
      );
    }

    if (window.Notification && Notification.permission !== 'denied') {
      Notification.requestPermission();
    }

    const task = this.state.task;
    const inProgress = this.taskInProgress(task);

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

    return (
      <div className={className}>
        <div className="deploy-log">
          {this.state.logLoading ? (
            <div style={{textAlign: 'center'}}>
              <div className="loading" />
              <p>Loading log history.</p>
            </div>
          ) : (
            <div ref="log" />
          )}
          {!this.state.logLoading && inProgress && <div className="loading-icon" />}
        </div>

        <div className="deploy-header">
          <div className="container">
            <h3>{task.name}</h3>
            <div className="ref">
              <div className="sha">{task.sha.substr(0, 7)}</div>
              {task.ref}
            </div>
            <div className="meta">
              {task.status == 'pending' && (
                <small>
                  <strong>QUEUED</strong> &mdash;{' '}
                </small>
              )}
              {task.dateFinished ? (
                <small>
                  {this.getStatusLabel(task)} <TimeSince date={task.dateFinished} />{' '}
                  &mdash; <Duration seconds={task.duration} className="duration" />
                </small>
              ) : task.dateStarted ? (
                <small>
                  Started <TimeSince date={task.dateStarted} />
                </small>
              ) : (
                <small>
                  Created <TimeSince date={task.dateCreated} />
                </small>
              )}
              <small> &mdash; by {task.user.name}</small>
            </div>
          </div>
        </div>

        <div className="deploy-footer">
          <div className="container">
            <div className="deploy-actions">
              {inProgress ? (
                <span>
                  <a className="btn btn-danger btn-sm" onClick={this.cancelTask}>
                    Cancel
                  </a>
                  <a className={liveScrollClassName} onClick={this.toggleLiveScroll}>
                    <input type="checkbox" defaultChecked={this.state.liveScroll} />
                    <span>Follow</span>
                  </a>
                </span>
              ) : (
                <a
                  className="btn btn-default btn-sm"
                  disabled={this.state.submitInProgress}
                  onClick={this.reDeploy}
                >
                  Re-deploy
                </a>
              )}
            </div>
            <div className="deploy-progress">
              <Progress value={this.getEstimatedProgress(task)} />
            </div>
          </div>
        </div>
      </div>
    );
  },
});

export default TaskDetails;
