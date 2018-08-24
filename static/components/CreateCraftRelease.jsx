import React from "react";

var CreateCraftRelease = React.createClass({

  getInitialState() {
    let app = this.props.app || null;

    return {
      app,
      env: 'production',
      ref: 'master',
      noStatusCheck: false,
      noMerge: false,
    };
  },

  getBuildData() {
    return {
      app: this.state.app.name,
      params: JSON.stringify({
        newVersion: this.state.newVersion,
        noStatusCheck: this.state.noStatusCheck,
        noMerge: this.state.noMerge,
      }),
    }
  },

  render() {
    return (
      <div>
        <div className="form-group">
          <label>New version</label>
          <input type="text" className="form-control"
            pattern="^\s*\d+\.[\d.]+\d(-\w+)?\s*$"
            onChange={this.onChangeNewVersion}
            placeholder="e.g. 2.3.4"
            required />
        </div>
        <div className="checkbox">
          <label>
            <input type="checkbox"
              onChange={this.onChangeNoStatusCheck} />
            Do not check build status
          </label>
        </div>
        <div className="checkbox">
          <label>
            <input type="checkbox"
              onChange={this.onChangeNoMergeBranch} />
            Do not merge release branch after publishing
        </label>
        </div>
      </div>
    );
  },

  onChangeNewVersion(e) {
    this.setState({
      newVersion: e.target.value,
    });
  },

  onChangeNoStatusCheck(e) {
    this.setState({
      noStatusCheck: e.target.checked,
    });
  },

  onChangeNoMergeBranch(e) {
    this.setState({
      noMerge: e.target.checked,
    });
  },
});

export default CreateCraftRelease;
