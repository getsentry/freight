var React = require('react');
var Router = require('react-router');
var {DefaultRoute, Route} = Router;

var AppDetails = require('./components/AppDetails');
var Layout = require('./components/Layout');
var Overview = require('./components/Overview');
var RouteNotFound = require('./components/RouteNotFound');
var TaskDetails = require('./components/TaskDetails');

var routes = (
  <Route path="/" name="main" handler={Layout}>
    <DefaultRoute name="overview" handler={Overview} />
    <Route path="/tasks/:app/:env/:number" name="taskDetailsLegacy" handler={TaskDetails} />
    <Route path="/:app/:env/:number" name="taskDetails" handler={TaskDetails} />
    <Route path="/:app" name="appDetails" handler={AppDetails} />
    <Router.NotFoundRoute handler={RouteNotFound} />
  </Route>
);

Router.run(routes, Router.HistoryLocation, (Handler) => {
  React.render(<Handler/>, document.body);
});
