/*** @jsx React.DOM */
var React = require("react");

var Duration = React.createClass({
  propTypes: {
    seconds: React.PropTypes.number.isRequired
  },

  getDuration() {
    var result, neg;
    var value = this.props.seconds * 1000;

    neg = value < 0 ? true : false;
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

module.exports = Duration;
