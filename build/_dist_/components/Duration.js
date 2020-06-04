function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';

class Duration extends React.Component {
  constructor(...args) {
    super(...args);

    _defineProperty(this, "getDuration", () => {
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
    });
  }

  render() {
    return /*#__PURE__*/React.createElement("span", {
      className: this.props.className
    }, this.getDuration());
  }

}

_defineProperty(Duration, "propTypes", {
  seconds: PropTypes.number.isRequired
});

export default Duration;