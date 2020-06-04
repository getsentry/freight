function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

import { browserHistory } from '/web_modules/react-router.js';
import jQuery from '/web_modules/jquery.js';
import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';
import api from '../api.js';

class CreateDeploy extends React.Component {
  constructor(props) {
    var _props$location$query;

    super(props);

    _defineProperty(this, "onChangeApplication", e => {
      const val = jQuery(e.target).val();
      const envMap = val ? this.props.appList.filter(app => {
        return app.name === val;
      })[0].environments || {} : {};
      const envList = Object.keys(envMap);
      const env = envList.length ? envList[0] : null;
      this.setState({
        app: val,
        envMap,
        env,
        ref: env ? env.defaultRef : 'master'
      });
    });

    _defineProperty(this, "onChangeEnvironment", e => {
      const val = jQuery(e.target).val();
      const config = val ? this.state.envMap[val] || {} : {};
      this.setState({
        env: val,
        ref: config.defaultRef || 'master'
      });
    });

    _defineProperty(this, "onChangeRef", e => {
      this.setState({
        ref: e.target.value
      });
    });

    _defineProperty(this, "onSubmit", e => {
      e.preventDefault();

      if (this.state.submitInProgress) {
        return;
      }

      this.setState({
        submitInProgress: true
      }, () => {
        api.request('/deploys/', {
          method: 'POST',
          data: {
            app: this.state.app,
            env: this.state.env,
            ref: this.state.ref
          },
          success: data => {
            this.gotoDeploy(data);
          },
          error: response => {
            this.setState({
              submitError: response.responseJSON.error,
              submitInProgress: false
            });
          }
        });
      });
    });

    _defineProperty(this, "gotoDeploy", deploy => {
      const {
        app,
        environment,
        number
      } = deploy;
      browserHistory.push(`/deploys/${app.name}/${environment}/${number}`);
    });

    const appList = props.appList;
    const defaultApp = appList.length !== 0 ? appList[0] : null;

    const _app = ((_props$location$query = props.location.query) === null || _props$location$query === void 0 ? void 0 : _props$location$query.app) ? props.location.query.app : defaultApp ? defaultApp.name : null;

    const _envMap = _app ? appList.filter(appObj => appObj.name === _app)[0].environments || {} : {};

    const _envList = Object.keys(_envMap);

    const _env = _envList.length ? _envList[0] : null;

    const defaultRef = _env ? _envMap[_env].defaultRef : 'master';
    this.state = {
      app: _app,
      env: _env,
      envMap: _envMap,
      ref: defaultRef,
      submitInProgress: false,
      submitError: null
    };
  }

  render() {
    return /*#__PURE__*/React.createElement("div", {
      className: "create-deploy"
    }, /*#__PURE__*/React.createElement("div", {
      className: "section"
    }, /*#__PURE__*/React.createElement("div", {
      className: "section-header"
    }, /*#__PURE__*/React.createElement("h2", null, "Create Deploy")), this.state.submitError && /*#__PURE__*/React.createElement("div", {
      className: "alert alert-block alert-danger"
    }, /*#__PURE__*/React.createElement("strong", null, "Unable to create deploy:"), /*#__PURE__*/React.createElement("span", null, this.state.submitError)), /*#__PURE__*/React.createElement("form", {
      onSubmit: this.onSubmit
    }, /*#__PURE__*/React.createElement("div", {
      className: "form-group"
    }, /*#__PURE__*/React.createElement("label", null, "Application"), /*#__PURE__*/React.createElement("select", {
      className: "form-control",
      value: this.state.app,
      onChange: this.onChangeApplication
    }, this.props.appList.map(app => {
      return /*#__PURE__*/React.createElement("option", {
        key: app.name
      }, app.name);
    }))), /*#__PURE__*/React.createElement("div", {
      className: "form-group"
    }, /*#__PURE__*/React.createElement("label", null, "Environment"), /*#__PURE__*/React.createElement("select", {
      className: "form-control",
      value: this.state.env,
      onChange: this.onChangeEnvironment
    }, Object.keys(this.state.envMap).map(env => {
      return /*#__PURE__*/React.createElement("option", {
        key: env
      }, env);
    }))), /*#__PURE__*/React.createElement("div", {
      className: "form-group"
    }, /*#__PURE__*/React.createElement("label", null, "Ref"), /*#__PURE__*/React.createElement("input", {
      type: "text",
      className: "form-control",
      onChange: this.onChangeRef,
      placeholder: "e.g. master",
      value: this.state.ref
    })), /*#__PURE__*/React.createElement("div", {
      className: "submit-group"
    }, /*#__PURE__*/React.createElement("button", {
      type: "submit",
      className: "btn btn-primary",
      disabled: this.state.submitInProgress
    }, "Ship It!")))));
  }

}

_defineProperty(CreateDeploy, "propTypes", {
  appList: PropTypes.array
});

export default CreateDeploy;