/** @jsx React.DOM */

var React = require('react');
var {Link} = require('react-router');

var Duration = require('./Duration');
var TimeSince = require('./TimeSince');

var TaskSummary = React.createClass({
  render() {
    var task = this.props.task;

    return (
      <div>
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
