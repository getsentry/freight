import {createElement} from 'react';
import ReactDOM from 'react-dom';
import {BrowserRouter} from 'react-router-dom';

import routes from 'app/routes';

ReactDOM.render(
  createElement(BrowserRouter, {}, routes()),
  document.getElementById('app')
);
