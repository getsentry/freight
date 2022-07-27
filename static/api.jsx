import * as qs from 'query-string';

/**
 * API client to make async fetch requests
 */
class Client {
  constructor(options = {}) {
    this.baseUrl = options.baseUrl ?? '/api/0';
  }

  request(path, options = {}) {
    const {data} = options;
    const hasData = typeof data !== 'undefined';

    const method = options.method ?? (hasData ? 'POST' : 'GET');
    const contentType = hasData ? 'application/json' : undefined;
    const body = hasData ? JSON.stringify(data) : undefined;

    const query = qs.stringify(options.query);

    let url = `${this.baseUrl}${path}`;
    if (query) {
      url += url.includes('?') ? `&${query}` : `?${query}`;
    }

    const headers = {'Content-Type': contentType};

    return fetch(url, {method, body, headers});
  }
}

const api = new Client();

export default api;
