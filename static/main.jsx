/** @jsx React.DOM */

var React = require('react');
var Router = require('react-router');
var {DefaultRoute, Route} = Router;

var App = require('./components/App');
var Overview = require('./components/Overview');
var TaskDetails = require('./components/TaskDetails');

var routes = (
  <Route path="/" name="app" handler={App}>
    <DefaultRoute name="overview" handler={Overview} />
    <Route path="/tasks/:app/:env/:number/" name="taskDetails" handler={TaskDetails} />
  </Route>
);

Router.run(routes, Router.HistoryLocation, (Handler) => {
  React.render(<Handler/>, document.body);
});
