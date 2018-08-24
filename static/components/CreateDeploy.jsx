import jQuery from "jquery";
import React from "react";

var CreateDeploy = React.createClass({

  getInitialState() {
    let app = this.props.app || null;
    let defaultEnv = app ? Object.keys(app.environments)[0] : null;
    let envMap = app ? app.environments : {};
    let defaultRef = defaultEnv ? envMap[defaultEnv].defaultRef : 'master';

    return {
      app,
      env: defaultEnv ? defaultEnv.name : null,
      envMap: envMap,
      ref: defaultRef,
    };
  },

  getBuildData() {
    return {
      app: this.state.app.name,
      env: this.state.env,
      ref: this.state.ref,
      params: this.state.params,
    }
  },

  render() {
    return (
      <div>
        <div className="form-group">
          <label>Environment</label>
          <select className="form-control"
            value={this.state.env}
            onChange={this.onChangeEnvironment}>
            {Object.keys(this.state.envMap).map((env) => {
              return <option key={env}>{env}</option>
            })}
          </select>
        </div>
        <div className="form-group">
          <label>Ref</label>
          <input type="text" className="form-control"
            onChange={this.onChangeRef}
            placeholder="e.g. master" value={this.state.ref} />
        </div>
      </div>
    );
  },

  onChangeEnvironment(e) {
    let val = jQuery(e.target).val();
    let config = val ? this.state.envMap[val] || {} : {};
    this.setState({
      env: val,
      ref: config.defaultRef || 'master',
    });
  },

  onChangeRef(e) {
    this.setState({
      ref: e.target.value,
    });
  },
});

export default CreateDeploy;
