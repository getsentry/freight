import * as React from 'react';
import {browserHistory} from 'react-router';
import ansi_up from 'ansi_up';
import createReactClass from 'create-react-class';
import {format} from 'date-fns';
import linkifyUrls from 'linkify-urls';
import PropTypes from 'prop-types';

import api from 'app/api';
import Duration from 'app/components/Duration';
import FaviconStatus from 'app/components/FaviconStatus';
import LoadingIndicator from 'app/components/LoadingIndicator';
import TimeSince from 'app/components/TimeSince';
import PollingMixin from 'app/mixins/polling';
import pushNotification from 'app/pushNotification';

function Progress({value}) {
  return <span className="progress" style={{width: value + '%'}} />;
}

Progress.propTypes = {
  value: PropTypes.number.isRequired,
};

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

  componentWillReceiveProps() {
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

  componentDidUpdate(_prevProps, prevState) {
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
      hash === '' &&
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

  logRef: React.createRef(),

  async fetchData() {
    if (this.logTimer) {
      window.clearTimeout(this.logTimer);
    }

    if (this.logRef.current) {
      this.logRef.current.innerHTML = '';
    }

    const taskResp = await api.request(this.getPollingUrl());
    const task = await taskResp.json();
    this.setState({loading: false, task});

    this.pollLog();
  },

  onScroll() {
    const scrollTop = document.body.scrollTop;
    if (scrollTop < this.lastScrollPos) {
      this.setState({liveScroll: false});
    } else if (scrollTop + window.innerHeight === document.body.scrollHeight) {
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

        div.innerHTML = ansi_up.ansi_to_html(
          linkifyUrls(lineItem[j][k], {
            attributes: {
              target: '_blank',
              rel: 'noreferrer noopener',
            },
          })
        );
        const date = new Date(logDataResults.timeStamp[j]);
        time.innerHTML = format(date, 'h:mm:ss aa');

        div.appendChild(time);
        frag.appendChild(div);
      }
    }
    this.logRef.current.appendChild(frag);

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

  async pollLog() {
    const task = this.state.task;
    const url = `/deploys/${task.app.name}/${task.environment}/${task.number}/log/?offset=${this.state.logNextOffset}`;

    if (!task) {
      return;
    }

    const logResp = await api.request(url);

    // Try again a little later if we don't have a 200
    if (!logResp.ok) {
      this.logTimer = window.setTimeout(this.pollLog, 10000);
      return;
    }

    const log = await logResp.json();

    if (log.chunks.length > 0) {
      this.setState({logLoading: false, logNextOffset: log.nextOffset});
      this.updateBuildLog(log);
    }

    if (this.state.logLoading) {
      this.setState({logLoading: false});
    }

    if (this.taskInProgress(this.state.task)) {
      this.logTimer = window.setTimeout(this.pollLog, 1000);
    }
  },

  async cancelTask() {
    const task = this.state.task;
    const url = `/deploys/${task.app.name}/${task.environment}/${task.number}/`;

    const cancelResp = await api.request(url, {
      method: 'PUT',
      data: {status: 'cancelled'},
    });

    if (cancelResp.ok) {
      this.setState({task: await cancelResp.json()});
    } else {
      // eslint-disable-next-line no-alert
      alert('Unable to cancel deploy.');
    }
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

    const triggerRedploy = async () => {
      const task = this.state.task;

      const deployResp = await api.request('/deploys/', {
        method: 'POST',
        data: {
          app: task.app.name,
          env: task.environment,
          ref: task.sha,
        },
      });

      const data = await deployResp.json();

      // workaround is referenced from here: https://github.com/ReactTraining/react-router/issues/1982
      browserHistory.push('/');
      browserHistory.push(`/deploys/${data.app.name}/${data.environment}/${data.number}`);
    };

    this.setState({submitInProgress: true}, triggerRedploy);
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

    return (
      <div className={className}>
        <div className="deploy-log">
          {this.state.logLoading ? (
            <div style={{textAlign: 'center'}}>
              <div className="loading" />
              <p>Loading log history.</p>
            </div>
          ) : (
            <div ref={this.logRef} />
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
              {task.status === 'pending' && (
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
              <FaviconStatus status={task.status} progress={estimatedProgress} />
              <Progress value={estimatedProgress} />
            </div>
          </div>
        </div>
      </div>
    );
  },
});

export default TaskDetails;
