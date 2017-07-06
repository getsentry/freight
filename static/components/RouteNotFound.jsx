import React from "react";

var RouteNotFound = React.createClass({
  render() {
    return (
      <div>
        <h1>Page Not Found</h1>
        <p className="alert-message notice">The page you are looking for was not found.</p>
      </div>
    );
  }
});

export default RouteNotFound;
