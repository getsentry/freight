import React from 'react';
import ReactDOM from 'react-dom';

import {Router, browserHistory} from 'react-router';

import routes from './routes';
import './less/main.css';

ReactDOM.render(
  React.createElement(Router, {history: browserHistory}, routes()),
  document.getElementById('app')
);

// Hot Module Replacement (HMR) - Remove this snippet to remove HMR.
// Learn more: https://www.snowpack.dev/#hot-module-replacement
if (import.meta.hot) {
  import.meta.hot.accept();
}
