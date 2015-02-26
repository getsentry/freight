/** @jsx React.DOM */

var jQuery = require("jquery");

class Client {
  constructor(options) {
    if (typeof options === 'undefined') {
      options = {};
    }
    this.baseUrl = options.baseUrl || "/api/0";
  }

  request(path, options) {
    var query = jQuery.param(options.query || "", true);
    var method = options.method || (options.data ? "POST" : "GET");
    var data = options.data;
    var contentType;

    if (typeof data !== "undefined") {
      data = JSON.stringify(data);
      contentType = 'application/json';
    } else {
      contentType = undefined;
    }

    var fullUrl = this.baseUrl + path;
    if (query) {
      if (fullUrl.indexOf('?') !== -1) {
        fullUrl += '&' + query;
      } else {
        fullUrl += '?' + query;
      }
    }

    jQuery.ajax({
      url: fullUrl,
      method: method,
      data: data,
      contentType: contentType,
      success: options.success,
      error: options.error,
      complete: options.complete
    });
  }
}

module.exports = new Client();
