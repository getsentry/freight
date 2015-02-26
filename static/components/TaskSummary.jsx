/** @jsx React.DOM */

var React = require('react');
var {Link} = require('react-router');

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
        {task.dateStarted &&
          <small>Started <TimeSince date={task.dateStarted} /></small>
        }
      </div>
    );
  }
});

module.exports = TaskSummary;
