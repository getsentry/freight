import React from 'react';
import ReactDOM from 'react-dom';
import {browserHistory, Router} from 'react-router';

import routes from './routes';

ReactDOM.render(
  React.createElement(Router, {history: browserHistory}, routes()),
  document.getElementById('app')
);
