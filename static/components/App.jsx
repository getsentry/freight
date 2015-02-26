/** @jsx React.DOM */

var React = require('react');
var Router = require('react-router');

var ListLink = require('./ListLink');

var App = React.createClass({
  render() {
    return (
      <div className="container">
        <div className="page-header">
          <ul className="nav nav-pills pull-right">
            <ListLink to="overview">Home</ListLink>
          </ul>
          <h1>Freight</h1>
        </div>
        <Router.RouteHandler />
      </div>
    );
  }
});

module.exports = App;
