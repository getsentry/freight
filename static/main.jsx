/** @jsx React.DOM */

var React = require('react');
var {DefaultRoute, Route, Routes} = require('react-router');

var App = require('./App');
var Overview = require('./Overview');

React.renderComponent((
  <Routes>
    <Route path="/" handler={App}>
      <DefaultRoute name="overview" handler={Overview} />
    </Route>
  </Routes>
), document.body);
