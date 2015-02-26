/** @jsx React.DOM */

var React = require('react');
var {Link, RouteHandler} = require('react-router');

var ListLink = require('./ListLink');

var App = React.createClass({
  render() {
    return (
      <div>
        <nav className="navbar navbar-default navbar-static-top">
          <div className="container">
            <Link to="overview" className="navbar-brand">Freight</Link>
          </div>
        </nav>
        <div className="container">
          <RouteHandler />
        </div>
      </div>
    );
  }
});

module.exports = App;
