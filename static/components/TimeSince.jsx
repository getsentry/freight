const React = require("react");
const moment = require("moment");

const TimeSince = React.createClass({
  propTypes: {
    date: React.PropTypes.any.isRequired
  },

  componentDidMount: function() {
    var delay = 2600;

    this.ticker = setInterval(this.ensureValidity, delay);
  },

  componentWillUnmount: function() {
    if (this.ticker) {
      clearInterval(this.ticker);
      this.ticker = null;
    }
  },

  ensureValidity: function() {
    // TODO(dcramer): this should ensure we actually *need* to update the value
    this.forceUpdate();
  },

  render: function() {
    var date = this.props.date;

    if (typeof date === "string" || typeof date === "number") {
      date = new Date(date);
    }

    return (
      <time>{moment.utc(date).fromNow()}</time>
    );
  }
});

export default TimeSince;
