import api from 'app/api';

const PollingMixin = {
  getInitialState() {
    return {
      pollingActive: true,
    };
  },
  componentWillMount() {
    this._timeoutId = window.setTimeout(this.pollForChanges, 3000);
  },

  componentWillUnmount() {
    if (this._timeoutId) {
      window.clearTimeout(this._timeoutId);
    }
  },

  async pollForChanges() {
    const url = this.getPollingUrl();

    if (!this.state.pollingActive) {
      this._timeoutId = window.setTimeout(this.pollForChanges, 3000);
    }

    const pollResp = await api.request(url);

    if (pollResp.ok) {
      const data = await pollResp.json();

      this.pollingReceiveData(data);
      this._timeoutId = window.setTimeout(this.pollForChanges, 3000);
    } else {
      // Try polling again a bit later
      this._timeoutId = window.setTimeout(this.pollForChanges, 10000);
    }
  },
};

export default PollingMixin;
