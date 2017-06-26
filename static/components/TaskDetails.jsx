import ansi_up from "ansi_up";
import React from "react";

import api from "../api";
import Duration from "./Duration";
import LoadingIndicator from "./LoadingIndicator";
import PollingMixin from "../mixins/polling";
import TaskSummary from "./TaskSummary";
import TimeSince from "./TimeSince";
import { browserHistory } from 'react-router';

var moment = require('moment');

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
  mixins: [PollingMixin],

  getInitialState() {
    return {
      loading: true,
      logLoading: true,
      task: null,
      logNextOffset: 0,
      liveScroll: true,
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
    var params = this.props.params;
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
      this.refs.log.innerHTML = '';
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
    var {app, env, number} = this.props.params;
    return '/deploys/' + app + '/' + env + '/' + number + '/';
  },

  pollingReceiveData(data) {
    this.setState({
      task: data
    });
  },

  updateBuildLog(data) {
    // add each additional new line
    var frag       = document.getElementsByClassName('frag')[0] || document.createDocumentFragment();
    frag.className = 'frag';

    var text       = data.chunks
    var objLength  = data.chunks.length


    for(var i = 0; i < objLength; i++){
      var timer    = new Date(data.chunks[i].date)
      var timeMil  = timer.getTime()
      //Multiple by 60000 to convert offset to milliseconds
      var offset   = timer.getTimezoneOffset() * 60000
      var timezone = timeMil - offset
      var newDate  = new Date(timezone)

      var div  = document.createElement('div');
      var time = document.createElement('div');

      div.className  = 'line';
      time.className = 'time';

=======

      div.innerHTML  = ansi_up.ansi_to_html(data.chunks[i].text)
      time.innerHTML = moment(newDate).parseZone().format("h:mm a")

      frag.appendChild(time)
      frag.appendChild(div)
    }


      div.innerHTML  = ansi_up.ansi_to_html(data.chunks[i].text)
      time.innerHTML = moment(newDate).parseZone().format("h:mm a")

      frag.appendChild(time)
      frag.appendChild(div)
    }

    this.refs.log.appendChild(frag);

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
    var url = '/deploys/' + task.app.name + '/' + task.environment + '/' + task.number + '/log/?offset=' + this.state.logNextOffset;

    api.request(url, {
      success: (data) => {
        if (data.chunks.length > 0) {
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

    var url = '/deploys/' + task.app.name + '/' + task.environment + '/' + task.number + '/';

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
        alert("Unable to cancel deploy.");
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

      api.request('/deploys/', {
        method: 'POST',
        data: {
          app: task.app.name,
          env: task.environment,
          ref: task.sha,
        },
        success: (data) => {
          let {app, environment, number} = this.props.task;
          browserHistory.push(`/deploys/${app.name}/${environment}/${number}`);
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
          <LoadingIndicator style={{marginBottom: 20}}>Loading task details.</LoadingIndicator>
        </div>
      );
    }

    let task = this.state.task;
    let inProgress = this.taskInProgress(task);

    let liveScrollClassName = "btn btn-default btn-sm";
    if (this.state.liveScroll) {
      liveScrollClassName += " btn-active";
    }

    let className = 'deploy-details';
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
        <div className="deploy-log">
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

        <div className="deploy-header">
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

        <div className="deploy-footer">
          <div className="container">
            <div className="deploy-actions">
              {inProgress ?
                <span>
                  <a className="btn btn-danger btn-sm"
                     onClick={this.cancelTask}>Cancel</a>
                  <a className={liveScrollClassName}
                     onClick={this.toggleLiveScroll}>
                    <input type="checkbox"
                           defaultChecked={this.state.liveScroll} />
                    <span>Follow</span>
                  </a>
                </span>
              :
                <a className="btn btn-default btn-sm"
                   disabled={this.state.submitInProgress}
                   onClick={this.reDeploy}>Re-deploy</a>
              }
            </div>
            <div className="deploy-progress">
              <Progress value={this.getEstimatedProgress(task)} />
            </div>
          </div>
        </div>

      </div>
    );
  }
});

export default TaskDetails;
