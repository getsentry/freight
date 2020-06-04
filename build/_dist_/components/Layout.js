function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';
import { Link } from '/web_modules/react-router.js';
import { init } from '/web_modules/@sentry/browser.js';
import api from '../api.js';
import Indicators from './Indicators.js';
import LoadingIndicator from './LoadingIndicator.js';

class Layout extends React.Component {
  constructor(...args) {
    super(...args);

    _defineProperty(this, "state", {
      appList: null,
      loading: true,
      error: false
    });

    _defineProperty(this, "fetchConfig", () => {
      const error = new Error('Error fetching /config/');
      return new Promise((resolve, reject) => {
        api.request('/config/', {
          success: resolve,
          error: resp => {
            error.resp = resp;
            reject(error);
          }
        });
      });
    });

    _defineProperty(this, "fetchApps", () => {
      const error = new Error('Error fetching /apps/');
      return new Promise((resolve, reject) => {
        api.request('/apps/', {
          success: resolve,
          error: resp => {
            error.resp = resp;
            reject(error);
          }
        });
      });
    });

    _defineProperty(this, "fetchData", async () => {
      // try to fetch config first
      try {
        const config = await this.fetchConfig();

        if (config === null || config === void 0 ? void 0 : config.SENTRY_PUBLIC_DSN) {
          init({
            dsn: config.SENTRY_PUBLIC_DSN
          });
        }
      } catch (err) {
        var _err$resp;

        console.error(err); // eslint-disable-line no-console

        if ((err === null || err === void 0 ? void 0 : (_err$resp = err.resp) === null || _err$resp === void 0 ? void 0 : _err$resp.status) === 401) {
          var _err$resp2, _err$resp2$responseJS, _err$resp2$responseJS2;

          if (err === null || err === void 0 ? void 0 : (_err$resp2 = err.resp) === null || _err$resp2 === void 0 ? void 0 : (_err$resp2$responseJS = _err$resp2.responseJSON) === null || _err$resp2$responseJS === void 0 ? void 0 : (_err$resp2$responseJS2 = _err$resp2$responseJS.data) === null || _err$resp2$responseJS2 === void 0 ? void 0 : _err$resp2$responseJS2.next) {
            window.location.assign(err.resp.responseJSON.data.next);
          }

          this.setState({
            loading: false,
            error: 'Not Authorized'
          });
        }

        return;
      }

      try {
        const appList = await this.fetchApps();
        this.setState({
          appList,
          loading: false,
          error: false
        });
      } catch (err) {
        console.error(err); // eslint-disable-line no-console

        this.setState({
          loading: false,
          error: true
        });
      }
    });
  }

  componentWillMount() {
    this.fetchData();
  }

  render() {
    const {
      app
    } = this.props.params;
    const {
      loading,
      error,
      appList
    } = this.state;
    return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement(Indicators, null), /*#__PURE__*/React.createElement("header", null, /*#__PURE__*/React.createElement("div", {
      className: "container"
    }, /*#__PURE__*/React.createElement("div", {
      className: "pull-right"
    }, /*#__PURE__*/React.createElement(Link, {
      to: {
        pathname: '/deploy',
        query: {
          app
        }
      },
      className: `btn btn-sm btn-default ${(loading || error) && 'btn-disabled'}`
    }, "Deploy")), /*#__PURE__*/React.createElement("h1", null, /*#__PURE__*/React.createElement(Link, {
      to: "/"
    }, "Freight")), app && /*#__PURE__*/React.createElement("h2", null, /*#__PURE__*/React.createElement(Link, {
      to: `/${app}`
    }, app)))), /*#__PURE__*/React.createElement("div", {
      className: "body"
    }, /*#__PURE__*/React.createElement("div", {
      className: "container"
    }, loading && /*#__PURE__*/React.createElement("div", {
      style: {
        textAlign: 'center'
      }
    }, /*#__PURE__*/React.createElement(LoadingIndicator, null, /*#__PURE__*/React.createElement("p", null, "Loading application data. Hold on to your pants!"))), !loading && (error ? error : /*#__PURE__*/React.cloneElement(this.props.children, {
      appList
    })))));
  }

}

export default Layout;