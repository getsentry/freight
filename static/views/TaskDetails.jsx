import * as React from 'react';
import {browserHistory} from 'react-router';
import Ansi from 'ansi-to-react';
import classnames from 'classnames';
import {format} from 'date-fns';
import PropTypes from 'prop-types';

import LoadingIndicator from 'app/components/LoadingIndicator';
import TaskSummary from 'app/components/TaskSummary';
import useApi from 'app/hooks/useApi';
import useDeployFinishedNotification from 'app/hooks/useDeployFinishedNotification';
import useFaviconStatus from 'app/hooks/useFaviconStatus';
import usePolling from 'app/hooks/usePolling';

function Progress({value}) {
  return <span className="progress" style={{width: value + '%'}} />;
}

Progress.propTypes = {
  value: PropTypes.number.isRequired,
};

/**
 * Retreive the line number that is highlighted from the location hash
 */
function getHighlightedLine() {
  const highlightedLineMatch = window.location.hash.match(/L(?<lineno>[0-9]+)/);
  const lineNumber = Number(highlightedLineMatch?.groups.lineno);

  return !isNaN(lineNumber) ? lineNumber : null;
}

/**
 * Use the estimatedDuration to produce a progress that maxes out at 95%, until
 * the task completes.
 */
function getEstimatedProgress(task) {
  if (!task) {
    return 0;
  }

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

function scrollToEnd() {
  window.scrollTo(0, document.body.scrollHeight);
}

function TaskDetails({params}) {
  const {app, env, number} = params;

  const api = useApi();

  const [isLiveScroll, setIsLiveScroll] = React.useState(true);

  const [taskLoading, setTaskLoading] = React.useState(true);
  const [task, setTask] = React.useState(null);

  const inProgress = ['in_progress', 'pending'].includes(task?.status);
  const estimatedProgress = getEstimatedProgress(task);

  // Notify when the task completes
  useDeployFinishedNotification(task ? [task] : []);

  // Update favicon based on task status
  useFaviconStatus({status: task?.status, progress: estimatedProgress});

  const handleTaskResult = React.useCallback(data => {
    setTask(data);
    setTaskLoading(false);
  }, []);

  // Poll for task changes
  usePolling({
    url: `/deploys/${app}/${env}/${number}/`,
    handleRecieveData: handleTaskResult,
    pollingActive: inProgress,
  });

  const [logLoading, setLogLoading] = React.useState(true);
  const [logItems, setLogItems] = React.useState([]);
  const [logOffset, setLogOffset] = React.useState(0);

  const handleLogResult = React.useCallback(
    data => {
      const newLogItems = data.chunks.flatMap(chunk =>
        chunk.text
          .split('\n')
          .filter(line => line !== '')
          .map(text => ({text, date: chunk.date}))
      );

      setLogItems(prevItems => [...prevItems, ...newLogItems]);
      setLogOffset(data.nextOffset);
      setLogLoading(false);

      if (isLiveScroll) {
        scrollToEnd();
      }
    },
    [isLiveScroll]
  );

  // Poll for log updates
  usePolling({
    url: `/deploys/${app}/${env}/${number}/log/?offset=${logOffset}`,
    timeout: 1000,
    handleRecieveData: handleLogResult,
    pollingActive: inProgress,
  });

  const [highlightedLine, setHighlightedLine] = React.useState(getHighlightedLine());

  const [redeployInProgress, setRedeployInProgress] = React.useState(false);
  const handleRedeploy = React.useCallback(async () => {
    if (redeployInProgress) {
      return;
    }

    setRedeployInProgress(true);

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
  }, [api, task, redeployInProgress]);

  const handleCancelTask = React.useCallback(async () => {
    const url = `/deploys/${app}/${env}/${number}/`;

    const cancelResp = await api.request(url, {
      method: 'PUT',
      data: {status: 'cancelled'},
    });

    if (cancelResp.ok) {
      setTask(await cancelResp.json());
    } else {
      // eslint-disable-next-line no-alert
      alert('Unable to cancel deploy.');
    }
  }, [api, app, env, number]);

  if (taskLoading) {
    return (
      <div style={{textAlign: 'center'}}>
        <LoadingIndicator style={{marginBottom: 20}}>
          Loading task details.
        </LoadingIndicator>
      </div>
    );
  }

  const liveScrollClassName = classnames('btn btn-default btn-sm', {
    'btn-active': isLiveScroll,
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
      setHighlightedLine={setHighlightedLine}
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
                <a className="btn btn-danger btn-sm" onClick={handleCancelTask}>
                  Cancel
                </a>
                <label className={liveScrollClassName}>
                  <input
                    type="checkbox"
                    checked={isLiveScroll}
                    onChange={e => setIsLiveScroll(e.target.checked)}
                  />
                  <span>Follow</span>
                </label>
              </span>
            ) : (
              <a
                className="btn btn-default btn-sm"
                disabled={redeployInProgress}
                onClick={handleRedeploy}
              >
                Re-deploy
              </a>
            )}
          </div>
          <div className="deploy-progress">
            <Progress value={estimatedProgress} />
          </div>
        </div>
      </div>
    </div>
  );
}

// Memoize the LogLineItem since there will be a lot of them, so avoiding
// re-renders will be helpful

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

export default TaskDetails;
