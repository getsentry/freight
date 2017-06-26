import React from "react";
import ReactDOM from "react-dom";

import {Router, browserHistory} from "react-router";

import routes from "./routes";


ReactDOM.render(
      React.createElement(Router, {history: browserHistory}, routes()),
      document.getElementById("app")
    );
