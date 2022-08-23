import {Route, Routes} from 'react-router-dom';

import CreateDeploy from 'app/views/CreateDeploy';
import Layout from 'app/views/Layout';
import LockDeploy from 'app/views/LockDeploy';
import Overview from 'app/views/Overview';
import RouteNotFound from 'app/views/RouteNotFound';
import TaskDetails from 'app/views/TaskDetails';

const routes = () => {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Overview />} />
        <Route path=":app" element={<Overview />} />
        <Route path=":app/:env/:number" element={<TaskDetails />} />
        <Route path="deploy" element={<CreateDeploy />} />
        <Route path="lock" element={<LockDeploy />} />
        <Route path="deploys/:app/:env/:number" element={<TaskDetails />} />
        <Route path="tasks/:app/:env/:number" element={<TaskDetails />} />
        <Route path="*" element={<RouteNotFound />} />
      </Route>
    </Routes>
  );
};

export default routes;
