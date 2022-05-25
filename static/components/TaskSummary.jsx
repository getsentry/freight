import React from 'react';
import {browserHistory} from 'react-router';
import classnames from 'classnames';
import PropTypes from 'prop-types';

import Duration from './Duration';
import TimeSince from './TimeSince';

class Progress extends React.Component {
  static propTypes = {
    value: PropTypes.number.isRequired,
  };

  render() {
    return <span className="progress" style={{width: this.props.value + '%'}} />;
  }
}

class TaskSummary extends React.Component {
  static propTypes = {
    task: PropTypes.shape({
      app: PropTypes.shape({
        name: PropTypes.string,
      }),
      environment: PropTypes.string,
      number: PropTypes.number,
    }),
  };

  static contextTypes = {
    router: PropTypes.object.isRequired,
  };

  taskInProgress = task => {
    return task.status === 'in_progress' || task.status === 'pending';
  };

  getEstimatedProgress = task => {
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
  };

  getStatusLabel = task => {
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
  };

  gotoTask = e => {
    if (e) {
      e.preventDefault();
    }

    const {app, environment, number} = this.props.task;

    browserHistory.push(`/deploys/${app.name}/${environment}/${number}`);
  };

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

    return (
      <div
        className={classnames(this.props.className, className)}
        onClick={this.gotoTask}
      >
        <Progress value={this.getEstimatedProgress(task)} />
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
              {this.getStatusLabel(task)} <TimeSince date={task.dateFinished} /> &mdash;{' '}
              <Duration seconds={task.duration} className="duration" />
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
    );
  }
}

export default TaskSummary;
