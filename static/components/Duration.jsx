const React = require("react");

const Duration = React.createClass({
  propTypes: {
    seconds: React.PropTypes.number.isRequired
  },

  getDuration() {
    let result, neg;
    let value = this.props.seconds * 1000;

    neg = (value < 0);
    if (neg) {
      value = -value;
    }

    if (value > 7200000) {
      result = Math.round(value / 3600000) + ' hr';
    } else if (value > 120000) {
      result = Math.round(value / 60000) + ' min';
    } else if (value > 10000) {
      result = Math.round(value / 1000) + ' sec';
    } else if (value > 1000) {
      result = Math.round(value / 1000) + ' sec';
    } else {
      result = Math.round(value) + ' ms';
    }

    if (neg) {
      result = '-' + result;
    }

    return result;
  },

  render() {
    return (
      <span className={this.props.className}>{this.getDuration()}</span>
    );
  }
});

export default Duration;
