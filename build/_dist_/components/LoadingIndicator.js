function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

import classNames from '/web_modules/classnames.js';
import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';

class LoadingIndicator extends React.Component {
  shouldComponentUpdate() {
    return false;
  }

  render() {
    const className = classNames({
      loading: true,
      mini: this.props.mini,
      global: this.props.global
    });
    return /*#__PURE__*/React.createElement("div", {
      className: classNames(this.props.className, className)
    }, /*#__PURE__*/React.createElement("div", {
      className: "loading-mask"
    }), /*#__PURE__*/React.createElement("div", {
      className: "loading-indicator"
    }), /*#__PURE__*/React.createElement("div", {
      className: "loading-message"
    }, this.props.children));
  }

}

_defineProperty(LoadingIndicator, "propTypes", {
  global: PropTypes.bool,
  mini: PropTypes.bool
});

export default LoadingIndicator;