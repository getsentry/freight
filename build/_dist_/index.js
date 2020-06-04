import React from '/web_modules/react.js';
import ReactDOM from '/web_modules/react-dom.js';
import { Router, browserHistory } from '/web_modules/react-router.js';
import routes from './routes.js';
import './less/main.css.proxy.js';
ReactDOM.render( /*#__PURE__*/React.createElement(Router, {
  history: browserHistory
}, routes()), document.getElementById('app'));