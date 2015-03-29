/** @jsx React.DOM */

var React = require('react');
var {Link, RouteHandler} = require('react-router');

var App = React.createClass({
  childContextTypes: {
    setHeading: React.PropTypes.func
  },

  getChildContext() {
    return {
      setHeading: this.setHeading
    };
  },

  getInitialState() {
    return {
      heading: null
    };
  },

  setHeading(value) {
    this.setState({
      heading: value
    });
  },

  render() {
    return (
      <div>
        <header>
          <div className="container">
            <h1><Link to="overview">Freight</Link></h1>
            {this.state.heading &&
              <h2>{this.state.heading}</h2>
            }
          </div>
        </header>
        <div className="container">
          <RouteHandler />
        </div>
      </div>
    );
  }
});

module.exports = App;
