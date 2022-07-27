import React from 'react';
import createReactClass from 'create-react-class';
import PropTypes from 'prop-types';

import api from 'app/api';
import BarChart from 'app/components/BarChart';
import PollingMixin from 'app/mixins/polling';

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

  async componentWillMount() {
    const resp = await api.request(this.getPollingUrl());
    const points = this.dataToPoints(await resp.json());
    this.setState({loading: false, points});
  },

  getPollingUrl() {
    const {app} = this.props;
    return `/deploy-stats/${app ? `?app=${app}` : ''}`;
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
