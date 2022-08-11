import * as React from 'react';
import {useNavigate} from 'react-router-dom';
import classnames from 'classnames';
import PropTypes from 'prop-types';

import Duration from 'app/components/Duration';
import ShaLink from 'app/components/ShaLink';
import TimeSince from 'app/components/TimeSince';

function Progress({value}) {
  return <span className="progress" style={{width: value + '%'}} />;
}

Progress.propTypes = {
  value: PropTypes.number.isRequired,
};

function getStatusLabel(task) {
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
}

function getEstimatedProgress(task) {
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
}

function TaskSummary({task, className}) {
  const navigate = useNavigate();

  const taskInProgress = task.status === 'in_progress' || task.status === 'pending';

  const gotoTask = React.useCallback(
    e => {
      if (e.target.hasAttribute('href')) {
        return;
      }

      e.preventDefault();

      const {app, environment, number} = task;

      navigate(`/deploys/${app.name}/${environment}/${number}`);
    },
    [task, navigate]
  );

  let classes = 'deploy';

  if (taskInProgress) {
    classes += ' active';
  } else {
    classes += ' finished';
  }

  if (task.status === 'failed') {
    classes += ' failed';
  } else if (task.status === 'cancelled') {
    classes += ' cancelled';
  }

  return (
    <div className={classnames(className, classes)} onClick={gotoTask}>
      <Progress value={getEstimatedProgress(task)} />
      <h3>{task.name}</h3>
      <div className="ref">
        <ShaLink sha={task.sha} url={task.sha_url} remote={task.remote} />
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
            {getStatusLabel(task)} <TimeSince date={task.dateFinished} /> &mdash;{' '}
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

TaskSummary.propTypes = {
  task: PropTypes.shape({
    app: PropTypes.shape({
      name: PropTypes.string,
    }),
    environment: PropTypes.string,
    number: PropTypes.number,
  }),
};

export default TaskSummary;
