import React from 'react';
import {formatDistanceToNowStrict} from 'date-fns';
import PropTypes from 'prop-types';

class TimeSince extends React.Component {
  static propTypes = {
    date: PropTypes.any.isRequired,
  };

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

  ensureValidity = () => {
    // TODO(dcramer): this should ensure we actually *need* to update the value
    this.forceUpdate();
  };

  render() {
    const date = new Date(this.props.date);

    return (
      <time dateTime={date.toISOString()}>
        {formatDistanceToNowStrict(date, {addSuffix: true})}
      </time>
    );
  }
}

export default TimeSince;
