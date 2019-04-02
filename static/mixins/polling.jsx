import api from '../api';

const PollingMixin = {
  getInitialState() {
    return {
      pollingActive: true,
    };
  },
  componentWillMount(prevProps, prevState) {
    this._timeoutId = window.setTimeout(this.pollForChanges, 3000);
  },

  componentWillUnmount() {
    if (this._timeoutId) {
      window.clearTimeout(this._timeoutId);
    }
  },

  pollForChanges() {
    const url = this.getPollingUrl();

    if (!this.state.pollingActive) {
      this._timeoutId = window.setTimeout(this.pollForChanges, 3000);
    }

    api.request(url, {
      success: data => {
        this.pollingReceiveData(data);
        this._timeoutId = window.setTimeout(this.pollForChanges, 3000);
      },
      error: () => {
        this._timeoutId = window.setTimeout(this.pollForChanges, 10000);
      },
    });
  },
};

export default PollingMixin;
