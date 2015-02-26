/** @jsx React.DOM */

var React = require('react');

var api = require('../api');

var Overview = React.createClass({
  getInitialState() {
    return {
      loading: true,
      activeTasks: []
    };
  },

  componentWillMount() {
    api.request('/tasks/?status=in_progress&status=pending', {
      success: (data) => {
        this.setState({
          loading: false,
          activeTasks: data
        })
      }
    })
  },

  render() {
    if (this.state.loading) {
      return <div className="loading" />;
    }

    var taskNodes = this.state.activeTasks.map((task) => {
      return (
        <li>
          <h3>{task.app.name}/{task.environment}#{task.number}</h3>
        </li>
      );
    });

    return (
      <div>
        <h2>Active Tasks</h2>
        <ul>
          {taskNodes}
        </ul>
      </div>
    );
  }
});

module.exports = Overview;
