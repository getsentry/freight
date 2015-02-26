/** @jsx React.DOM */

var React = require('react');
var Router = require('react-router');

var api = require('../api');
var TimeSince = require('./TimeSince');

var TaskDetails = React.createClass({
  mixins: [Router.State],

  getInitialState() {
    return {
      loading: true,
      task: null,
      logNextOffset: 0,
      liveScroll: false
    };
  },

  componentWillMount() {
    api.request('/tasks/' + this.getParams().taskId + '/', {
      success: (data) => {
        this.setState({
          loading: false,
          task: data
        });
      }
    });

    this.pollLog();
  },

  updateBuildLog(data) {
    var frag = document.createDocumentFragment();

    // add each additional new line
    data.text.split('\n').forEach((line) => {
      var div = document.createElement('div');
      div.className = 'line';
      div.innerHTML = line;
      frag.appendChild(div);
    });

    this.refs.log.getDOMNode().appendChild(frag);

    if (this.state.liveScroll) {
      window.scrollTo(0, document.body.scrollHeight);
    }
  },

  taskInProgress() {
    var status = this.state.task.status;
    switch(status) {
      case 'pending':
      case 'in_progress':
        return true;
    }
    return false;
  },

  pollLog() {
    var url = '/tasks/' + this.getParams().taskId + '/log/?offset=' + this.state.logNextOffset;

    api.request(url, {
      success: (data) => {
        if (data.text !== "") {
          this.updateBuildLog(data);
          this.setState({
            logNextOffset: data.nextOffset
          });
        }
        if (this.taskInProgress()) {
          window.setTimeout(this.pollLog, 1000);
        }
      },
      error: () => {
        window.setTimeout(this.pollLog, 10000);
      }
    });
  },

  render() {
    if (this.state.loading) {
      return <div className="loading" />;
    }

    var task = this.state.task;

    return (
      <div>
        <div className="page-header">
          <h2>{task.app.name}/{task.environment} #{task.number}</h2>
        </div>

        <dl className="flat">
          <dt>Status:</dt>
          <dd>{task.status}</dd>
          <dt>Created:</dt>
          <dd><TimeSince date={task.dateCreated} /></dd>
          <dt>Started:</dt>
          <dd>{task.dateStarted ?
            <TimeSince date={task.dateStarted} />
          :
            <span>&mdash;</span>
          }</dd>
          <dt>Finished:</dt>
          <dd>{task.dateFinished ?
            <span><TimeSince date={task.dateFinished} /> ({task.duration}s)</span>
          :
            <span>&mdash;</span>
          }</dd>
        </dl>

        <h3>Log</h3>

        <div className="log" ref="log" />
      </div>
    );
  }
});

module.exports = TaskDetails;
