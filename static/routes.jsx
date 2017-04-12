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
  <Route path="/" name="main" component={Layout}>
    <IndexRoute name="overview" component={Overview} />
    <Route path="/deploy" name="createDeploy" component={CreateDeploy} />
    <Route path="/tasks/:app/:env/:number" name="taskDetailsLegacy" component={TaskDetails} />
    <Route path="/deploys/:app/:env/:number" name="deployDetails" component={TaskDetails} />
    <Route path="/:app/settings" name="appSettings" component={AppSettings} />
    <Route path="/:app/:env/:number" name="deployDetailsLegancy" component={TaskDetails} />
    <Route path="/:app" name="appDetails" component={AppDetails} />
    <Route path="*" component={RouteNotFound} />
  </Route>
);

export default routes;
