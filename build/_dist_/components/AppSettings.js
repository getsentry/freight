function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';
import api from '../api.js';
import IndicatorStore from '../stores/indicatorStore.js';
import LoadingIndicator from './LoadingIndicator.js';

class AppSettings extends React.Component {
  constructor(...args) {
    super(...args);

    _defineProperty(this, "state", {
      appId: this.props.params.app,
      app: null,
      formData: null,
      submitInProgress: false,
      submitError: false
    });

    _defineProperty(this, "getAppUrl", () => {
      return '/apps/' + this.state.appId + '/';
    });

    _defineProperty(this, "getFormData", app => {
      return {
        name: app.name,
        environments: JSON.stringify(app.environments, null, 2)
      };
    });

    _defineProperty(this, "onFieldChange", e => {
      const newData = {};
      newData[e.target.name] = e.target.value;
      const formData = Object.assign({}, this.state.formData, newData);
      this.setState({
        formData
      });
    });

    _defineProperty(this, "onSubmit", e => {
      e.preventDefault();

      if (this.state.submitInProgress) {
        return;
      }

      const indicator = IndicatorStore.add('Saving changes...');
      this.setState({
        submitInProgress: true
      }, () => {
        const formData = this.state.formData;
        api.request(this.getAppUrl(), {
          method: 'PUT',
          data: {
            name: formData.name,
            environments: formData.environments
          },
          success: data => {
            this.setState({
              app: data,
              formData: this.getFormData(data),
              submitInProgress: false
            });
            this.context.setHeading(data.name);
          },
          error: response => {
            this.setState({
              submitInProgress: false,
              submitError: response.responseJSON.error
            });
          },
          complete: () => {
            IndicatorStore.remove(indicator);
          }
        });
      });
    });
  }

  componentWillMount() {
    api.request(this.getAppUrl(), {
      success: data => {
        this.setState({
          app: data,
          formData: this.getFormData(data)
        });
      }
    });
  }

  render() {
    if (this.state.app === null) {
      return /*#__PURE__*/React.createElement(LoadingIndicator, null);
    }

    const {
      app,
      formData,
      submitInProgress
    } = this.state;
    return /*#__PURE__*/React.createElement("div", null, /*#__PURE__*/React.createElement("div", {
      className: "section"
    }, /*#__PURE__*/React.createElement("div", {
      className: "section-header"
    }, /*#__PURE__*/React.createElement("h2", null, app.name, " Settings")), /*#__PURE__*/React.createElement("form", {
      onSubmit: this.onSubmit
    }, this.state.submitError && /*#__PURE__*/React.createElement("div", {
      className: "alert alert-block alert-danger"
    }, /*#__PURE__*/React.createElement("strong", null, "Unable to save changes:"), /*#__PURE__*/React.createElement("span", null, this.state.submitError)), /*#__PURE__*/React.createElement("div", {
      className: "control-group"
    }, /*#__PURE__*/React.createElement("div", {
      className: "controls"
    }, /*#__PURE__*/React.createElement("label", null, "Name"), /*#__PURE__*/React.createElement("input", {
      type: "text",
      name: "name",
      className: "form-control",
      placeholder: "e.g. master",
      onChange: this.onFieldChange,
      value: formData.name
    }))), /*#__PURE__*/React.createElement("div", {
      className: "control-group"
    }, /*#__PURE__*/React.createElement("div", {
      className: "controls"
    }, /*#__PURE__*/React.createElement("label", null, "Environments"), /*#__PURE__*/React.createElement("textarea", {
      name: "environments",
      className: "form-control",
      onChange: this.onFieldChange,
      style: {
        height: 150
      },
      value: formData.environments
    }))), /*#__PURE__*/React.createElement("div", {
      className: "form-actions",
      style: {
        marginTop: 25
      }
    }, /*#__PURE__*/React.createElement("button", {
      className: "btn btn-primary",
      disabled: submitInProgress,
      type: "submit"
    }, "Save Changes")))));
  }

}

export default AppSettings;