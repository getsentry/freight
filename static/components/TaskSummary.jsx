/** @jsx React.DOM */

var React = require('react');
var {Link} = require('react-router');
var joinClasses = require("react/lib/joinClasses");

var Duration = require('./Duration');
var TimeSince = require('./TimeSince');

var Progress = React.createClass({
  propTypes: {
    value: React.PropTypes.number.isRequired,
  },

  render() {
    return (
      <span className="progress" style={{width: this.props.value + '%'}} />
    );
  }
});

var TaskSummary = React.createClass({
  taskInProgress(task) {
    return task.status == 'in_progress' || task.status == 'pending';
  },

  getEstimatedProgress(task) {
    var started = new Date(task.dateStarted).getTime();
    if (!started) {
      return 0;
    }

    var now = Math.max(new Date().getTime(), started);
    return parseInt(Math.min((now - started) / 1000 / task.estimatedDuration * 100, 95), 10);
  },

  render() {
    var task = this.props.task;
    var className = 'task';
    if (this.taskInProgress(task)) {
      className += ' active';
    }

    return (
      <div className={joinClasses(this.props.className, className)}>
        <Progress value={this.getEstimatedProgress(task)} />
        <h3>
          <Link to="taskDetails" params={{taskId: task.id}}>
            {task.app.name}/{task.environment} #{task.number}
          </Link>
        </h3>
        <div className="ref">
          <div className="sha">{task.sha.substr(0, 7)}</div>
          {task.ref}
        </div>
        <div className="meta">
          {task.dateFinished ?
            <small>Finished <TimeSince date={task.dateFinished} /> &mdash; <Duration seconds={task.duration} className="duration" /></small>
          : (task.dateStarted ?
            <small>Started <TimeSince date={task.dateStarted} /></small>
          :
            <small>Created <TimeSince date={task.dateCreated} /></small>
          )}
        </div>
      </div>
    );
  }
});

module.exports = TaskSummary;
