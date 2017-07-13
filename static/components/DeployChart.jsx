import React from 'react';

import api from '../api';

import BarChart     from "./BarChart";
import PollingMixin from '../mixins/polling';
import TaskSummary  from './TaskSummary';

var DeployChart = React.createClass({
  mixins: [PollingMixin],

  getInitialState() {
    return {
      loading: true,
      points: [],
    };
  },

  componentWillMount() {
    api.request(this.getPollingUrl(), {
      success: (data) => {
        this.setState({
          points: this.dataToPoints(data),
          loading: false
        });
      }
    });
  },

  getPollingUrl() {
    return '/stats/';
  },

  pollingReceiveData(data) {
    this.setState({
      points: this.dataToPoints(data)
    });
  },

  dataToPoints(data) {
    return data.map((point) => {
      return {x: point[0], y: point[1]};
    });
  },

  render() {
    return (
      <div className="section">
        <BarChart points={this.state.points} label="deploys" />
      </div>
    );
  }
});

export default DeployChart;
