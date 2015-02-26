/** @jsx React.DOM */

var React = require('react');

var api = require('../api');

var TaskSummary = require('./TaskSummary');

var Overview = React.createClass({
  getInitialState() {
    return {
      loading: true,
      activeTasks: [],
      previousTasks: []
    };
  },

  componentWillMount() {
    api.request('/tasks/?status=in_progress&status=pending', {
      success: (data) => {
        this.setState({
          loading: false,
          activeTasks: data
        });
      }
    });

    api.request('/tasks/?status=finished&status=failed&status=cancelled', {
      success: (data) => {
        this.setState({
          loading: false,
          previousTasks: data
        });
      }
    });
  },

  render() {
    if (this.state.loading) {
      return <div className="loading" />;
    }

    var activeTaskNodes = this.state.activeTasks.map((task) => {
      return (
        <li key={task.id}>
          <TaskSummary task={task} />
        </li>
      );
    });

    var previousTaskNodes = this.state.previousTasks.map((task) => {
      return (
        <li key={task.id}>
          <TaskSummary task={task} />
        </li>
      );
    });

    return (
      <div>
        <h2>Active Tasks</h2>
        {activeTaskNodes.length ?
          <ul className="task-list">
            {activeTaskNodes}
          </ul>
        :
          <p>There are no active tasks.</p>
        }

        <h2>Task History</h2>
        {previousTaskNodes.length ?
          <ul className="task-list">
            {previousTaskNodes}
          </ul>
        :
          <p>There are no historical tasks.</p>
        }
      </div>
    );
  }
});

module.exports = Overview;
