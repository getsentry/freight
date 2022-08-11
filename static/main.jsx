import * as React from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter} from 'react-router-dom';

import routes from 'app/routes';

ReactDOM.render(
  React.createElement(BrowserRouter, {}, routes()),
  document.getElementById('app')
);
