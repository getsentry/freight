import ansi_up from "ansi_up";
import React from "react";
import Router from "react-router";

import api from "../api";
import Duration from "./Duration";
import PollingMixin from "../mixins/polling";
import TaskSummary from "./TaskSummary";
import TimeSince from "./TimeSince";


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

var TaskDetails = React.createClass({
  mixins: [PollingMixin, Router.Navigation, Router.State],

  getInitialState() {
    return {
      loading: true,
      logLoading: true,
      task: null,
      logNextOffset: 0,
      liveScroll: true
    };
  },

  componentWillUnmount() {
    window.removeEventListener('scroll', this.onScroll, false);

    if (this.logTimer) {
      window.clearTimeout(this.logTimer);
    }
  },

  componentWillMount() {
    this.lastScrollPos = 0;
    this.logTimer = null;
  },

  componentDidMount() {
    window.addEventListener('scroll', this.onScroll, false);
    this.fetchData();
  },

  componentDidUpdate() {
    if (this.state.liveScroll) {
      this.scrollLog();
    }
  },

  componentWillReceiveProps(nextProps) {
    var params = this.getParams();
    var task = this.state.task;
    if (params.app !== task.app.name || params.env !== task.environment || params.number !== task.number) {
      this.setState({
        loading: true,
        error: false,
        task: null
      }, this.fetchData());
    }
  },

  fetchData() {
    if (this.logTimer) {
      window.clearTimeout(this.logTimer);
    }

    if (this.refs.log) {
      this.refs.log.getDOMNode().innerHTML = '';
    }

    api.request(this.getPollingUrl(), {
      success: (data) => {
        this.setState({
          task: data,
          loading: false
        });

        this.pollLog();
      }
    });
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

  pollLog() {
    var task = this.state.task;

    var url = '/tasks/' + task.app.name + '/' + task.environment + '/' + task.number + '/log/?offset=' + this.state.logNextOffset;

    api.request(url, {
      success: (data) => {
        if (data.text !== "") {
          this.setState({
            logLoading: false,
            logNextOffset: data.nextOffset
          });
          this.updateBuildLog(data);
        }
        if (this.state.logLoading) {
          this.setState({
            logLoading: false
          });
        }
        if (this.taskInProgress(this.state.task)) {
          this.logTimer = window.setTimeout(this.pollLog, 1000);
        }
      },
      error: () => {
        this.logTimer = window.setTimeout(this.pollLog, 10000);
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

  reDeploy() {
    if (this.state.submitInProgress) {
      return false;
    }

    this.setState({
      submitInProgress: true,
    }, () => {
      let task = this.state.task;

      api.request('/tasks/', {
        method: 'POST',
        data: {
          app: task.app.name,
          env: task.environment,
          ref: task.ref,
          sha: task.sha,
        },
        success: (data) => {
          this.transitionTo('taskDetails', {
            app: data.app.name,
            env: data.environment,
            number: data.number
          });
        }
      });
    });
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
      return (
        <div style={{textAlign: "center"}}>
          <div className="loading" style={{marginBottom: 20}} />
          <p>Loading task details.</p>
        </div>
      );
    }

    let task = this.state.task;
    let inProgress = this.taskInProgress(task);

    let liveScrollClassName = "btn btn-default btn-sm";
    if (this.state.liveScroll) {
      liveScrollClassName += " btn-active";
    }

    let className = 'task-details';
    if (inProgress) {
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
      <div className={className}>
        <div className="task-log">
          {this.state.logLoading ?
            <div style={{textAlign: "center"}}>
              <div className="loading" />
              <p>Loading log history.</p>
            </div>
          :
            <div ref="log" />
          }
          {!this.state.logLoading && inProgress &&
            <div className="loading-icon" />
          }
        </div>

        <div className="task-header">
          <div className="container">
            <h3>{task.name}</h3>
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
        </div>

        <div className="task-footer">
          <div className="container">
            <div className="task-actions">
              {inProgress ?
                <span>
                  <a className="btn btn-danger btn-sm"
                     onClick={this.cancelTask}>Cancel</a>
                  <a className={liveScrollClassName}
                     onClick={this.toggleLiveScroll}>
                    <input type="checkbox"
                           checked={this.state.liveScroll} />
                    <span>Follow</span>
                  </a>
                </span>
              :
                <a className="btn btn-default btn-sm"
                   disabled={this.state.submitInProgress}
                   onClick={this.reDeploy}>Re-deploy</a>
              }
            </div>
            <div className="task-progress">
              <Progress value={this.getEstimatedProgress(task)} />
            </div>
          </div>
        </div>

      </div>
    );
  }
});

export default TaskDetails;
