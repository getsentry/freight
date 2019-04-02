import PropTypes from 'prop-types';
import React from 'react';
import {Link} from 'react-router';
import {init} from '@sentry/browser';

import api from '../api';
import Indicators from './Indicators';
import LoadingIndicator from './LoadingIndicator';

class Layout extends React.Component {
  static childContextTypes = {
    setHeading: PropTypes.func,
  };

  state = {
    heading: null,
    appList: null,
    loading: true,
    error: false,
  };

  getChildContext() {
    return {
      setHeading: this.setHeading,
    };
  }

  componentWillMount() {
    this.fetchData();
  }

  setHeading = value => {
    this.setState({
      heading: value,
    });
  };

  fetchConfig = () => {
    const error = new Error('Error fetching /config/');

    return new Promise((resolve, reject) => {
      api.request('/config/', {
        success: resolve,
        error: resp => {
          error.resp = resp;
          reject(error);
        },
      });
    });
  };

  fetchApps = () => {
    const error = new Error('Error fetching /apps/');

    return new Promise((resolve, reject) => {
      api.request('/apps/', {
        success: resolve,
        error: resp => {
          error.resp = resp;
          reject(error);
        },
      });
    });
  };

  fetchData = async () => {
    try {
      const [appList, config] = await Promise.all([this.fetchApps(), this.fetchConfig()]);

      if (config && config.SENTRY_PUBLIC_DSN) {
        init({
          dsn: config.SENTRY_PUBLIC_DSN,
        });
      }

      this.setState({
        appList,
        loading: false,
        error: false,
      });
    } catch (err) {
      console.error(err); // eslint-disable-line no-console
      this.setState({
        loading: false,
        error: true,
      });
    }
  };

  render() {
    if (this.state.loading) {
      return (
        <div>
          <div className="container" style={{textAlign: 'center'}}>
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
              <Link to="/deploy" className="btn btn-sm btn-default">
                Deploy
              </Link>
            </div>
            <h1>
              <Link to="/">Freight</Link>
            </h1>
            {this.state.heading && <h2>{this.state.heading}</h2>}
          </div>
        </header>
        <div className="body">
          <div className="container">
            {React.cloneElement(this.props.children, {
              appList: this.state.appList,
            })}
          </div>
        </div>
      </div>
    );
  }
}

export default Layout;
