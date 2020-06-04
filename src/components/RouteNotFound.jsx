import React from 'react';

class RouteNotFound extends React.Component {
  render() {
    return (
      <div>
        <h1>Page Not Found</h1>
        <p className="alert-message notice">
          The page you are looking for was not found.
        </p>
      </div>
    );
  }
}

export default RouteNotFound;
