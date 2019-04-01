const PropTypes = require('prop-types');
const React = require('react');
const moment = require('moment');

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
    let date = this.props.date;

    if (typeof date === 'string' || typeof date === 'number') {
      date = new Date(date);
    }

    return <time>{moment.utc(date).fromNow()}</time>;
  }
}

export default TimeSince;
