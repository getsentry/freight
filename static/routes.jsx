import * as React from 'react';
import {IndexRoute, Route} from 'react-router';

import Layout from 'app/components/Layout';
import AppDetails from 'app/views/AppDetails';
import CreateDeploy from 'app/views/CreateDeploy';
import Overview from 'app/views/Overview';
import RouteNotFound from 'app/views/RouteNotFound';
import TaskDetails from 'app/views/TaskDetails';

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
