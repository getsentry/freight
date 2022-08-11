import * as React from 'react';
import {Route, Routes} from 'react-router-dom';

import AppDetails from 'app/views/AppDetails';
import CreateDeploy from 'app/views/CreateDeploy';
import Layout from 'app/views/Layout';
import Overview from 'app/views/Overview';
import RouteNotFound from 'app/views/RouteNotFound';
import TaskDetails from 'app/views/TaskDetails';

const routes = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Overview />} />
        <Route path="deploy" element={<CreateDeploy />} />
        <Route path="tasks/:app/:env/:number" element={<TaskDetails />} />
        <Route path="deploys/:app/:env/:number" element={<TaskDetails />} />
        <Route path=":app/:env/:number" element={<TaskDetails />} />
        <Route path=":app" element={<AppDetails />} />
        <Route path="*" element={<RouteNotFound />} />
      </Route>
    </Routes>
  );
};

export default routes;
