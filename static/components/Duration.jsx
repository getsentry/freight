import PropTypes from 'prop-types';

function Duration({className, seconds}) {
  let duration;
  let ms = seconds * 1000;
  const neg = ms < 0 ? true : false;

  if (neg) {
    ms = ms * -1;
  }

  if (ms > 7200000) {
    duration = Math.round(ms / 3600000) + ' hr';
  } else if (ms > 120000) {
    duration = Math.round(ms / 60000) + ' min';
  } else if (ms > 10000) {
    duration = Math.round(ms / 1000) + ' sec';
  } else if (ms > 1000) {
    duration = Math.round(ms / 1000) + ' sec';
  } else {
    duration = Math.round(ms) + ' ms';
  }

  if (neg) {
    duration = `-${duration}`;
  }

  return <span className={className}>{duration}</span>;
}

Duration.propTypes = {
  seconds: PropTypes.number.isRequired,
};

export default Duration;
