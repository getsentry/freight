import React from "react";
import Router from "react-router";

import AppDetails from "./components/AppDetails";
import AppSettings from "./components/AppSettings";
import CreateDeploy from "./components/CreateDeploy";
import Layout from "./components/Layout";
import Overview from "./components/Overview";
import RouteNotFound from "./components/RouteNotFound";
import TaskDetails from "./components/TaskDetails";

const {DefaultRoute, Route} = Router;

var routes = (
  <Route path="/" name="main" handler={Layout}>
    <DefaultRoute name="overview" handler={Overview} />
    <Route path="/deploy" name="createDeploy" handler={CreateDeploy} />
    <Route path="/tasks/:app/:env/:number" name="taskDetailsLegacy" handler={TaskDetails} />
    <Route path="/:app/settings" name="appSettings" handler={AppSettings} />
    <Route path="/:app/:env/:number" name="deployDetailsLegancy" handler={TaskDetails} />
    <Route path="/deploys/:app/:env/:number" name="deployDetails" handler={TaskDetails} />
    <Route path="/:app" name="appDetails" handler={AppDetails} />
    <Router.NotFoundRoute handler={RouteNotFound} />
  </Route>
);

export default routes;
