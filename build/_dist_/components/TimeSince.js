function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';
import moment from '/web_modules/moment.js';

class TimeSince extends React.Component {
  constructor(...args) {
    super(...args);

    _defineProperty(this, "ensureValidity", () => {
      // TODO(dcramer): this should ensure we actually *need* to update the value
      this.forceUpdate();
    });
  }

  componentDidMount() {
    const delay = 2600;
    this.ticker = setInterval(this.ensureValidity, delay);
  }

  componentWillUnmount() {
    if (this.ticker) {
      clearInterval(this.ticker);
      this.ticker = null;
    }
  }

  render() {
    let date = this.props.date;

    if (typeof date === 'string' || typeof date === 'number') {
      date = new Date(date);
    }

    return /*#__PURE__*/React.createElement("time", null, moment.utc(date).fromNow());
  }

}

_defineProperty(TimeSince, "propTypes", {
  date: PropTypes.any.isRequired
});

export default TimeSince;