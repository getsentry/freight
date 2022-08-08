import * as qs from 'query-string';

const s4 = () =>
  Math.floor((1 + Math.random()) * 0x10000)
    .toString(16)
    .substring(1);

function uniqueId() {
  return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
}

export class Request {
  /**
   * Promise which will be resolved when the request has completed
   */
  requestPromise;
  /**
   * AbortController to cancel the in-flight request. This will not be set in
   * unsupported browsers.
   */
  aborter;

  constructor(requestPromise, aborter) {
    this.requestPromise = requestPromise;
    this.aborter = aborter;
  }

  cancel() {
    this.aborter?.abort();
  }
}

/**
 * API client to make async fetch requests
 */
class Client {
  activeRequests = new Map();

  constructor(options = {}) {
    this.baseUrl = options.baseUrl ?? '/api/0';
  }

  clear() {
    [...this.activeRequests.values()].forEach(r => r.cancel());
  }

  async request(path, options = {}) {
    const requestId = uniqueId();

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

    // AbortController is optional, though most browser should support it.
    const aborter =
      typeof AbortController !== 'undefined' ? new AbortController() : undefined;

    const fetchPromise = fetch(url, {method, body, headers, signal: aborter.signal});
    const request = new Request(fetchPromise, aborter);
    this.activeRequests.set(requestId, request);

    try {
      return await fetchPromise;
    } finally {
      this.activeRequests.delete(requestId);
    }
  }
}

export default Client;
