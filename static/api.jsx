import * as qs from 'query-string';

/**
 * API client to make async fetch requests
 */
class Client {
  constructor(options = {}) {
    this.baseUrl = options.baseUrl ?? '/api/0';
  }

  async request(path, options = {}) {
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

    try {
      const result = await fetch(url, {method, body, headers});
      const resultJson = await result.json();

      options.success?.(resultJson);
    } catch (error) {
      options.error?.(error);
    } finally {
      options.complete?.();
    }
  }
}

const api = new Client();

export default api;
