import React from 'react';
import {IndexRoute, Route} from 'react-router';

import AppDetails from './components/AppDetails';
import AppSettings from './components/AppSettings';
import CreateDeploy from './components/CreateDeploy';
import Layout from './components/Layout';
import Overview from './components/Overview';
import RouteNotFound from './components/RouteNotFound';
import TaskDetails from './components/TaskDetails';

const routes = () => {
  return (
    <Route exact path="/" component={Layout}>
      <IndexRoute component={Overview} />
      <Route path="/deploy" component={CreateDeploy} />
      <Route path="/tasks/:app/:env/:number" component={TaskDetails} />
      <Route path="/deploys/:app/:env/:number" component={TaskDetails} />
      <Route path="/:app/settings" component={AppSettings} />
      <Route path="/:app/:env/:number" component={TaskDetails} />
      <Route path="/:app" component={AppDetails} />
      <Route path="*" component={RouteNotFound} />
    </Route>
  );
};

export default routes;
