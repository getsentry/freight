import React from "react";
import {Link, RouteHandler} from "react-router";

import api from "../api";
import Indicators from './Indicators';
import LoadingIndicator from './LoadingIndicator';

const Layout = React.createClass({
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
      heading: null,
      appList: null,
      loading: true,
      error: false
    };
  },

  componentWillMount() {
    this.fetchData();
  },

  setHeading(value) {
    this.setState({
      heading: value
    });
  },

  fetchData() {
    api.request("/apps/", {
      success: (data) => {
        this.setState({
          appList: data,
          loading: false,
          error: false
        });
      },
      error: () => {
        this.setState({
          loading: false,
          error: true
        });
      }
    });
  },

  render() {
    if (this.state.loading) {
      return (
        <div>
          <div className="container" style={{textAlign: "center"}}>
            <LoadingIndicator>
              <p>Loading application data. Hold on to your pants!</p>
            </LoadingIndicator>
          </div>
        </div>
      );
    }

    return (
      <div>
        <Indicators />
        <header>
          <div className="container">
            <div className="pull-right">
              <Link to="createDeploy" className="btn btn-sm btn-default">Deploy</Link>
            </div>
            <h1><Link to="overview">Freight</Link></h1>
            {this.state.heading &&
              <h2>{this.state.heading}</h2>
            }
          </div>
        </header>
        <div className="body">
          <div className="container">
            <RouteHandler appList={this.state.appList} />
          </div>
        </div>
      </div>
    );
  }
});

export default Layout;
