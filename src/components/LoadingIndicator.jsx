import classNames from 'classnames';
import PropTypes from 'prop-types';
import React from 'react';

class LoadingIndicator extends React.Component {
  static propTypes = {
    global: PropTypes.bool,
    mini: PropTypes.bool,
  };

  shouldComponentUpdate() {
    return false;
  }

  render() {
    const className = classNames({
      loading: true,
      mini: this.props.mini,
      global: this.props.global,
    });

    return (
      <div className={classNames(this.props.className, className)}>
        <div className="loading-mask" />
        <div className="loading-indicator" />
        <div className="loading-message">{this.props.children}</div>
      </div>
    );
  }
}

export default LoadingIndicator;
