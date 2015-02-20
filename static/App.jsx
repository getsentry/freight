/** @jsx React.DOM */

var React = require('react');
var {Link} = require('react-router');

var App = React.createClass({
  render: function() {
    return (
      <div className="container">
        <div className="page-header">
          <h1>Freight</h1>
        </div>
        <ul>
          <li><Link to="overview">Overview</Link></li>
        </ul>
        <this.props.activeRouteHandler />
      </div>
    );
  }
});

module.exports = App;
