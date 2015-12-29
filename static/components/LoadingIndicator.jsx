import classNames from 'classnames';
import React from 'react';

const LoadingIndicator = React.createClass({
  propTypes: {
    global: React.PropTypes.bool,
    mini:  React.PropTypes.bool,
  },

  shouldComponentUpdate() {
    return false;
  },

  render() {
    let className = classNames({
      'loading': true,
      'mini': this.props.mini,
      'global': this.props.global,
    });

    return (
      <div className={classNames(this.props.className, className)}>
        <div className="loading-mask"></div>
        <div className="loading-indicator"></div>
        <div className="loading-message">{this.props.children}</div>
      </div>
    );
  }
});

export default LoadingIndicator;

