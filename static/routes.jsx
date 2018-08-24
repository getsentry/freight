import React from "react";
import { Route, IndexRoute } from "react-router";

import AppDetails from "./components/AppDetails";
import AppSettings from "./components/AppSettings";
import CreateBuild from "./components/CreateBuild";
import Layout from "./components/Layout";
import Overview from "./components/Overview";
import RouteNotFound from "./components/RouteNotFound";
import TaskDetails from "./components/TaskDetails";

var routes = () => {
  return (
    <Route exact path="/" component={Layout}>
      <IndexRoute component={Overview} />
      <Route path="/deploy" component={CreateBuild} />
      <Route path="/tasks/:app/:env/:number" component={TaskDetails} />
      <Route path="/deploys/:app/:env/:number" component={TaskDetails} />
      <Route path="/:app/settings" component={AppSettings} />
      <Route path="/:app/:env/:number" component={TaskDetails} />
      <Route path="/:app" component={AppDetails} />
      <Route
        path="*"
        component={RouteNotFound} />
    </Route>
  );
};

export default routes;
