import React from 'react';
import {IndexRoute, Route} from 'react-router';

import AppDetails from 'app/components/AppDetails';
import CreateDeploy from 'app/components/CreateDeploy';
import Layout from 'app/components/Layout';
import Overview from 'app/components/Overview';
import RouteNotFound from 'app/components/RouteNotFound';
import TaskDetails from 'app/components/TaskDetails';

const routes = () => {
  return (
    <Route exact path="/" component={Layout}>
      <IndexRoute component={Overview} />
      <Route path="/deploy" component={CreateDeploy} />
      <Route path="/tasks/:app/:env/:number" component={TaskDetails} />
      <Route path="/deploys/:app/:env/:number" component={TaskDetails} />
      <Route path="/:app/:env/:number" component={TaskDetails} />
      <Route path="/:app" component={AppDetails} />
      <Route path="*" component={RouteNotFound} />
    </Route>
  );
};

export default routes;
