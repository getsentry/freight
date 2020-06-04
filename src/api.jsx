import axios from 'axios';

class Client {
  constructor(options = {}) {
    this.baseUrl = options.baseUrl || '/api/0';
  }

  request(path, options) {
    const query = options.query || '';
    const method = options.method || (options.data ? 'POST' : 'GET');
    const data = options.data;

    let fullUrl = this.baseUrl + path;
    if (query) {
      if (fullUrl.indexOf('?') !== -1) {
        fullUrl += '&' + query;
      } else {
        fullUrl += '?' + query;
      }
    }

    axios({
      url: fullUrl,
      method,
      data,
    })
      .then(res => options.success(res.data))
      .catch(options.error);
  }
}

export default new Client();
