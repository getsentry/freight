/** @jsx React.DOM */

var React = require('react');
var {Link, RouteHandler} = require('react-router');

var ListLink = require('./ListLink');

var App = React.createClass({
  render() {
    return (
      <div>
        <header>
          <div className="container">
            <h1><Link to="overview">Freight</Link></h1>
          </div>
        </header>
        <div className="container">
          <RouteHandler />
        </div>
      </div>
    );
  }
});

module.exports = App;
