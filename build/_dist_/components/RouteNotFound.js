import React from '/web_modules/react.js';

class RouteNotFound extends React.Component {
  render() {
    return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("h1", null, "Page Not Found"), /*#__PURE__*/React.createElement("p", {
      className: "alert-message notice"
    }, "The page you are looking for was not found."));
  }

}

export default RouteNotFound;