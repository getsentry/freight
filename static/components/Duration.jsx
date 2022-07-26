import React from 'react';
import PropTypes from 'prop-types';

class Duration extends React.Component {
  static propTypes = {
    seconds: PropTypes.number.isRequired,
  };

  getDuration = () => {
    let result;
    let value = this.props.seconds * 1000;
    const neg = value < 0 ? true : false;

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
  };

  render() {
    return <span className={this.props.className}>{this.getDuration()}</span>;
  }
}

export default Duration;
