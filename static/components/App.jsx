/** @jsx React.DOM */

var React = require('react');
var Router = require('react-router');

var ListLink = require('./ListLink');

var App = React.createClass({
  render() {
    return (
      <div className="container">
        <div className="page-header">
          <h1>Freight</h1>
        </div>
        <ul className="nav nav-pills">
          <ListLink to="overview">Overview</ListLink>
        </ul>
        <Router.RouteHandler />
      </div>
    );
  }
});

module.exports = App;
