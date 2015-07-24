/** @jsx React.DOM */

var ansi_up = require('ansi_up');
var React = require('react');
var Router = require('react-router');

var api = require('../api');
var Duration = require('./Duration');
var PollingMixin = require('../mixins/polling');
var TimeSince = require('./TimeSince');

var TaskDetails = React.createClass({
  mixins: [PollingMixin, Router.State],

  contextTypes: {
    setHeading: React.PropTypes.func,
  },

  getInitialState() {
    return {
      loading: true,
      task: null,
      logNextOffset: 0,
      liveScroll: true
    };
  },

  componentWillUnmount() {
    window.removeEventListener('scroll', this.onScroll, false);
    this.context.setHeading(null);
  },

  componentWillMount() {
    api.request(this.getPollingUrl(), {
      success: (data) => {
        this.context.setHeading(data.name);
        this.setState({
          task: data,
        });
        this.pollLog();
      }
    });
    this.lastScrollPos = 0;
  },

  componentDidMount() {
    window.addEventListener('scroll', this.onScroll, false);
  },

  componentDidUpdate() {
    if (this.state.liveScroll) {
      this.scrollLog();
    }
  },

  onScroll(event) {
    var scrollTop = document.body.scrollTop;
    if (scrollTop < this.lastScrollPos) {
      this.setState({liveScroll: false});
    } else if (scrollTop + window.innerHeight == document.body.scrollHeight) {
      this.setState({liveScroll: true});
    }
    this.lastScrollPos = scrollTop;
  },

  getPollingUrl() {
    var params = this.getParams();
    return '/tasks/' + params.app + '/' + params.env + '/' + params.number + '/';
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
      div.innerHTML = ansi_up.ansi_to_html(line);
      frag.appendChild(div);
    });

    this.refs.log.getDOMNode().appendChild(frag);

    if (this.state.liveScroll) {
      this.scrollLog();
    }
  },

  scrollLog() {
    window.scrollTo(0, document.body.scrollHeight);
  },

  taskInProgress(task) {
    return task.status == 'in_progress' || task.status == 'pending';
  },

  pollLog() {
    var task = this.state.task;

    var url = '/tasks/' + task.app.name + '/' + task.environment + '/' + task.number + '/log/?offset=' + this.state.logNextOffset;

    api.request(url, {
      success: (data) => {
        if (data.text !== "") {
          this.setState({
            loading: false,
            logNextOffset: data.nextOffset
          });
          this.updateBuildLog(data);
        }
        if (this.state.loading) {
          this.setState({
            loading: false
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

  cancelTask() {
    var task = this.state.task;

    var url = '/tasks/' + task.app.name + '/' + task.environment + '/' + task.number + '/';

    api.request(url, {
      method: "PUT",
      data: {
        "status": "cancelled"
      },
      success: (data) => {
        this.setState({
          task: data,
        });
      },
      error: () => {
        alert("Unable to cancel task.");
      }
    });
  },

  toggleLiveScroll() {
    var liveScroll = !this.state.liveScroll;
    this.setState({
      liveScroll: liveScroll
    });
    if (liveScroll) {
      this.scrollLog();
    }
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

  render() {
    if (this.state.loading) {
      return <div className="loading" />;
    }

    var task = this.state.task;
    var inProgress = this.taskInProgress(task);

    var liveScrollClassName = "btn btn-default btn-sm";
    if (this.state.liveScroll) {
      liveScrollClassName += " btn-active";
    }

    return (
      <div className="task-details">
        <div className="task-log">
          <div ref="log" />
          {inProgress &&
            <div className="loading-icon" />
          }
        </div>

        <div className="task-footer">
          <div className="container">
            <span className="task-status">
              {task.dateFinished ?
                <small>{this.getStatusLabel(task)} <TimeSince date={task.dateFinished} /> &mdash; <Duration seconds={task.duration} className="duration" /></small>
              : (task.dateStarted ?
                <small>Started <TimeSince date={task.dateStarted} /></small>
              :
                <small>Created <TimeSince date={task.dateCreated} /></small>
              )}
              <small> &mdash; by {task.user.name}</small>
            </span>
            <div className="pull-right">
              {inProgress &&
                <a className="btn btn-danger btn-sm"
                   onClick={this.cancelTask}>Cancel</a>
              }
              <a className={liveScrollClassName}
                 onClick={this.toggleLiveScroll}>
                <input type="checkbox"
                       checked={this.state.liveScroll} />
                <span>Follow</span>
              </a>
            </div>
          </div>
        </div>

      </div>
    );
  }
});

module.exports = TaskDetails;
