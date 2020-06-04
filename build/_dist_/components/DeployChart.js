import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';
import createReactClass from '/web_modules/create-react-class.js';
import api from '../api.js';
import BarChart from './BarChart.js';
import PollingMixin from '../mixins/polling.js';
const DeployChart = createReactClass({
  displayName: 'DeployChart',
  propTypes: {
    app: PropTypes.string
  },
  mixins: [PollingMixin],

  getInitialState() {
    return {
      loading: true,
      points: []
    };
  },

  componentWillMount() {
    api.request(this.getPollingUrl(), {
      success: data => {
        this.setState({
          points: this.dataToPoints(data),
          loading: false
        });
      }
    });
  },

  getPollingUrl() {
    const {
      app
    } = this.props;
    return `/stats/${app ? `?app=${app}` : ''}`;
  },

  pollingReceiveData(data) {
    this.setState({
      points: this.dataToPoints(data)
    });
  },

  dataToPoints(data) {
    return data.map(point => {
      return {
        x: point[0],
        y: point[1]
      };
    });
  },

  render() {
    return /*#__PURE__*/React.createElement("div", {
      className: "section"
    }, /*#__PURE__*/React.createElement(BarChart, {
      points: this.state.points,
      label: "deploys"
    }));
  }

});
export default DeployChart;