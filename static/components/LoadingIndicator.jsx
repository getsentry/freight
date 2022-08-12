import classNames from 'classnames';
import PropTypes from 'prop-types';

function LoadingIndicator({className, children, global, mini}) {
  const classes = classNames({
    loading: true,
    mini,
    global,
  });

  return (
    <div className={classNames(className, classes)}>
      <div className="loading-mask" />
      <div className="loading-indicator" />
      <div className="loading-message">{children}</div>
    </div>
  );
}

LoadingIndicator.propTypes = {
  global: PropTypes.bool,
  mini: PropTypes.bool,
};

export default LoadingIndicator;
