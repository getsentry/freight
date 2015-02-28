/** @jsx React.DOM */

var React = require('react');
var Router = require('react-router');

var api = require('../api');
var PollingMixin = require('../mixins/polling');
var TimeSince = require('./TimeSince');

var TaskDetails = React.createClass({
  mixins: [PollingMixin, Router.State],

  getInitialState() {
    return {
      loading: true,
      task: null,
      logNextOffset: 0,
      liveScroll: false
    };
  },

  componentWillMount() {
    api.request(this.getPollingUrl(), {
      success: (data) => {
        this.setState({
          loading: false,
          task: data,
          liveScroll: this.taskInProgress(data)
        });
        this.pollLog();
      }
    });
  },

  getPollingUrl() {
    return '/tasks/' + this.getParams().taskId + '/';
  },

  pollingReceiveData(data) {
    this.setState({
      task: data
    });
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

  taskInProgress(task) {
    var status = task.status;
    switch(status) {
      case 'pending':
      case 'in_progress':
        return true;
    }
    return false;
  },

  pollLog() {
    var url = '/tasks/' + this.state.task.id + '/log/?offset=' + this.state.logNextOffset;

    api.request(url, {
      success: (data) => {
        if (data.text !== "") {
          this.updateBuildLog(data);
          this.setState({
            logNextOffset: data.nextOffset
          });
        }
        if (this.taskInProgress(this.state.task)) {
          window.setTimeout(this.pollLog, 1000);
        }
      },
      error: () => {
        window.setTimeout(this.pollLog, 10000);
      }
    });
  },

  toggleLiveScroll() {
    this.setState({
      liveScroll: !this.state.liveScroll
    });
  },

  render() {
    if (this.state.loading) {
      return <div className="loading" />;
    }

    var task = this.state.task;

    var liveScrollClassName = "btn btn-default";
    if (this.state.liveScroll) {
      liveScrollClassName += " btn-active";
    }

    return (
      <div className="task-details">
        <div className="task-log" ref="log" />

        <div className="task-footer">
          <div className="container">
            <h2>{task.app.name}/{task.environment} #{task.number}</h2>

            <div className="pull-right">
              <a className={liveScrollClassName}
                 onClick={this.toggleLiveScroll}>
                <input type="checkbox"
                       checked={this.state.liveScroll} /> <span>Follow Log</span>
              </a>
            </div>
          </div>
        </div>

      </div>
    );
  }
});

module.exports = TaskDetails;
