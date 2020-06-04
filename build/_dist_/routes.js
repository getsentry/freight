import React from '/web_modules/react.js';
import { Route, IndexRoute } from '/web_modules/react-router.js';
import AppDetails from './components/AppDetails.js';
import AppSettings from './components/AppSettings.js';
import CreateDeploy from './components/CreateDeploy.js';
import Layout from './components/Layout.js';
import Overview from './components/Overview.js';
import RouteNotFound from './components/RouteNotFound.js';
import TaskDetails from './components/TaskDetails.js';

const routes = () => {
  return /*#__PURE__*/React.createElement(Route, {
    exact: true,
    path: "/",
    component: Layout
  }, /*#__PURE__*/React.createElement(IndexRoute, {
    component: Overview
  }), /*#__PURE__*/React.createElement(Route, {
    path: "/deploy",
    component: CreateDeploy
  }), /*#__PURE__*/React.createElement(Route, {
    path: "/tasks/:app/:env/:number",
    component: TaskDetails
  }), /*#__PURE__*/React.createElement(Route, {
    path: "/deploys/:app/:env/:number",
    component: TaskDetails
  }), /*#__PURE__*/React.createElement(Route, {
    path: "/:app/settings",
    component: AppSettings
  }), /*#__PURE__*/React.createElement(Route, {
    path: "/:app/:env/:number",
    component: TaskDetails
  }), /*#__PURE__*/React.createElement(Route, {
    path: "/:app",
    component: AppDetails
  }), /*#__PURE__*/React.createElement(Route, {
    path: "*",
    component: RouteNotFound
  }));
};

export default routes;