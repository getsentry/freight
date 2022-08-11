import * as React from 'react';
import {browserHistory} from 'react-router';
import Ansi from 'ansi-to-react';
import classnames from 'classnames';
import createReactClass from 'create-react-class';
import {format} from 'date-fns';
import PropTypes from 'prop-types';

import Client from 'app/api';
import FaviconStatus from 'app/components/FaviconStatus';
import LoadingIndicator from 'app/components/LoadingIndicator';
import TaskSummary from 'app/components/TaskSummary';
import PollingMixin from 'app/mixins/polling';
import pushNotification from 'app/utils/pushNotification';

function Progress({value}) {
  return <span className="progress" style={{width: value + '%'}} />;
}

Progress.propTypes = {
  value: PropTypes.number.isRequired,
};

// XXX(epurkhiser): Until this component is functional, we can't use the useApi
// hook that will smartly cancel API requets, so we'll instantiate a module
// local api client for now.
const api = new Client();

const LogLineItem = React.memo(({index, item, highlighted, setHighlightedLine}) => {
  return (
    <div className={classnames('line', {highlighted})}>
      <Ansi>{item.text}</Ansi>
      <time
        dateTime={item.date}
        onClick={() => {
          const newLineNumber = highlighted ? null : index;

          if (newLineNumber !== null) {
            history.replaceState(null, null, `${window.location.pathname}#L${index}`);
          } else {
            history.replaceState(null, null, window.location.pathname);
          }

          setHighlightedLine(newLineNumber);
        }}
      >
        {format(new Date(item.date), 'h:mm:ss aa')}
      </time>
    </div>
  );
});

LogLineItem.displayName = 'LogLineItem';

const TaskDetails = createReactClass({
  displayName: 'TaskDetails',
  mixins: [PollingMixin],

  getInitialState() {
    const highlightedLineMatch = window.location.hash.match(/L(?<lineno>[0-9]+)/);
    const lineNumber = Number(highlightedLineMatch?.groups.lineno);
    const highlightedLine = !isNaN(lineNumber) ? lineNumber : null;

    return {
      loading: true,
      logLoading: true,
      task: null,
      logItems: [],
      highlightedLine,
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

    if (window.Notification && Notification.permission !== 'denied') {
      Notification.requestPermission();
    }
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
        this.fetchData
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
    this.setState({task: data});
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
    const {task} = this.state;

    if (!task) {
      return;
    }

    const url = `/deploys/${task.app.name}/${task.environment}/${task.number}/log/?offset=${this.state.logNextOffset}`;

    const logResp = await api.request(url);

    // Try again a little later if we don't have a 200
    if (!logResp.ok) {
      this.logTimer = window.setTimeout(this.pollLog, 10000);
      return;
    }

    const log = await logResp.json();

    if (log.chunks.length > 0) {
      const newLogItems = log.chunks.flatMap(chunk =>
        chunk.text
          .split('\n')
          .filter(line => line !== '')
          .map(text => ({text, date: chunk.date}))
      );

      this.setState(lastState => ({
        logNextOffset: log.nextOffset,
        logItems: [...lastState.logItems, ...newLogItems],
      }));
    }

    this.setState({logLoading: false});

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
    this.setState({liveScroll});
    if (liveScroll) {
      this.scrollLog();
    }
  },

  reDeploy() {
    if (this.state.submitInProgress) {
      return;
    }

    const triggerRedploy = async () => {
      const {task} = this.state;

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

  setHighlightedLine: number => {
    this.setState({highlightedLine: number});
  },

  render() {
    const {
      task,
      loading,
      liveScroll,
      logLoading,
      logItems,
      highlightedLine,
      submitInProgress,
    } = this.state;

    if (loading) {
      return (
        <div style={{textAlign: 'center'}}>
          <LoadingIndicator style={{marginBottom: 20}}>
            Loading task details.
          </LoadingIndicator>
        </div>
      );
    }

    const inProgress = this.taskInProgress(task);
    const estimatedProgress = this.getEstimatedProgress(task);

    const liveScrollClassName = classnames('btn btn-default btn-sm', {
      'btn-active': liveScroll,
    });

    const className = classnames('deploy-details', {
      active: inProgress,
      finished: !inProgress,
      failed: task.status === 'failed',
      cancelled: task.status === 'cancelled',
    });

    const logLines = logItems.map((item, i) => (
      <LogLineItem
        key={i}
        index={i}
        item={item}
        highlighted={highlightedLine === i}
        setHighlightedLine={this.setHighlightedLine}
      />
    ));

    return (
      <div className={className}>
        <div className="deploy-log">
          {logLoading ? (
            <div style={{textAlign: 'center'}}>
              <div className="loading" />
              <p>Loading log history.</p>
            </div>
          ) : (
            <div>{logLines}</div>
          )}
          {!logLoading && inProgress && <div className="loading-icon" />}
        </div>

        <div className="deploy-header">
          <div className="container">
            <TaskSummary task={task} />
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
                    <input type="checkbox" defaultChecked={liveScroll} />
                    <span>Follow</span>
                  </a>
                </span>
              ) : (
                <a
                  className="btn btn-default btn-sm"
                  disabled={submitInProgress}
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
