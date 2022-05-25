import React from 'react';
import createReactClass from 'create-react-class';
import PropTypes from 'prop-types';

import api from '../api';
import PollingMixin from '../mixins/polling';

import BarChart from './BarChart';

const DeployChart = createReactClass({
  displayName: 'DeployChart',
  propTypes: {
    app: PropTypes.string,
  },
  mixins: [PollingMixin],

  getInitialState() {
    return {
      loading: true,
      points: [],
    };
  },

  componentWillMount() {
    api.request(this.getPollingUrl(), {
      success: data => {
        this.setState({
          points: this.dataToPoints(data),
          loading: false,
        });
      },
    });
  },

  getPollingUrl() {
    const {app} = this.props;
    return `/stats/${app ? `?app=${app}` : ''}`;
  },

  pollingReceiveData(data) {
    this.setState({
      points: this.dataToPoints(data),
    });
  },

  dataToPoints(data) {
    return data.map(point => {
      return {x: point[0], y: point[1]};
    });
  },

  render() {
    return (
      <div className="section">
        <BarChart points={this.state.points} label="deploys" />
      </div>
    );
  },
});

export default DeployChart;
