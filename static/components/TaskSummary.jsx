var React = require('react');
var Router = require('react-router');
var Link = Router.Link;
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
  mixins: [Router.Navigation],

  taskInProgress(task) {
    return task.status == 'in_progress' || task.status == 'pending';
  },

  getEstimatedProgress(task) {
    if (task.dateFinished) {
      return 100;
    }

    var started = new Date(task.dateStarted).getTime();
    if (!started) {
      return 0;
    }

    var now = Math.max(new Date().getTime(), started);
    return parseInt(Math.min((now - started) / 1000 / task.estimatedDuration * 100, 95), 10);
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
    }
  },

  gotoTask(e) {
    if (e) {
      e.preventDefault();
    }

    this.transitionTo('deployDetails', {
      app: this.props.task.app.name,
      env: this.props.task.environment,
      number: this.props.task.number
    });
  },

  render() {
    var task = this.props.task;
    var className = 'deploy';
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
      <div className={joinClasses(this.props.className, className)}
           onClick={this.gotoTask}>
        <Progress value={this.getEstimatedProgress(task)} />
        <h3>
          {task.name}
        </h3>
        <div className="ref">
          <div className="sha">{task.sha.substr(0, 7)}</div>
          {task.ref}
        </div>
        <div className="meta">
          {task.status == 'pending' &&
            <small><strong>QUEUED</strong> &mdash; </small>
          }
          {task.dateFinished ?
            <small>{this.getStatusLabel(task)} <TimeSince date={task.dateFinished} /> &mdash; <Duration seconds={task.duration} className="duration" /></small>
          : (task.dateStarted ?
            <small>Started <TimeSince date={task.dateStarted} /></small>
          :
            <small>Created <TimeSince date={task.dateCreated} /></small>
          )}
          <small> &mdash; by {task.user.name}</small>
        </div>
      </div>
    );
  }
});

export default TaskSummary;
