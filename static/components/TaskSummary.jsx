/** @jsx React.DOM */

var React = require('react');

var TaskSummary = React.createClass({
  render() {
    var task = this.props.task;

    return (
      <h3>{task.app.name}/{task.environment} #{task.number}</h3>
    );
  }
});

module.exports = TaskSummary;
