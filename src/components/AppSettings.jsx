import PropTypes from 'prop-types';
import React from 'react';

import api from '../api';
import IndicatorStore from '../stores/indicatorStore';
import LoadingIndicator from './LoadingIndicator';

class AppSettings extends React.Component {
  state = {
    appId: this.props.params.app,
    app: null,
    formData: null,
    submitInProgress: false,
    submitError: false,
  };

  componentWillMount() {
    api.request(this.getAppUrl(), {
      success: data => {
        this.setState({
          app: data,
          formData: this.getFormData(data),
        });
      },
    });
  }

  getAppUrl = () => {
    return '/apps/' + this.state.appId + '/';
  };

  getFormData = app => {
    return {
      name: app.name,
      environments: JSON.stringify(app.environments, null, 2),
    };
  };

  onFieldChange = e => {
    const newData = {};
    newData[e.target.name] = e.target.value;
    const formData = Object.assign({}, this.state.formData, newData);
    this.setState({formData});
  };

  onSubmit = e => {
    e.preventDefault();
    if (this.state.submitInProgress) {
      return;
    }
    const indicator = IndicatorStore.add('Saving changes...');
    this.setState(
      {
        submitInProgress: true,
      },
      () => {
        const formData = this.state.formData;

        api.request(this.getAppUrl(), {
          method: 'PUT',
          data: {
            name: formData.name,
            environments: formData.environments,
          },
          success: data => {
            this.setState({
              app: data,
              formData: this.getFormData(data),
              submitInProgress: false,
            });
            this.context.setHeading(data.name);
          },
          error: response => {
            this.setState({
              submitInProgress: false,
              submitError: response.responseJSON.error,
            });
          },
          complete: () => {
            IndicatorStore.remove(indicator);
          },
        });
      }
    );
  };

  render() {
    if (this.state.app === null) {
      return <LoadingIndicator />;
    }

    const {app, formData, submitInProgress} = this.state;
    return (
      <div>
        <div className="section">
          <div className="section-header">
            <h2>{app.name} Settings</h2>
          </div>
          <form onSubmit={this.onSubmit}>
            {this.state.submitError && (
              <div className="alert alert-block alert-danger">
                <strong>Unable to save changes:</strong>
                <span>{this.state.submitError}</span>
              </div>
            )}
            <div className="control-group">
              <div className="controls">
                <label>Name</label>
                <input
                  type="text"
                  name="name"
                  className="form-control"
                  placeholder="e.g. master"
                  onChange={this.onFieldChange}
                  value={formData.name}
                />
              </div>
            </div>

            <div className="control-group">
              <div className="controls">
                <label>Environments</label>
                <textarea
                  name="environments"
                  className="form-control"
                  onChange={this.onFieldChange}
                  style={{height: 150}}
                  value={formData.environments}
                />
              </div>
            </div>

            <div className="form-actions" style={{marginTop: 25}}>
              <button
                className="btn btn-primary"
                disabled={submitInProgress}
                type="submit"
              >
                Save Changes
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }
}

export default AppSettings;
