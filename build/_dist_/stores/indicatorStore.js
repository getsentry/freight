import React from '/web_modules/react.js';
import Reflux from '/web_modules/reflux.js';
import LoadingIndicator from '../components/LoadingIndicator.js';
const IndicatorStore = Reflux.createStore({
  init() {
    this.items = [];
  },

  add(node) {
    if (! /*#__PURE__*/React.isValidElement(node)) {
      node = /*#__PURE__*/React.createElement(LoadingIndicator, {
        global: true
      }, node);
    }

    this.items.push(node);
    this.trigger(this.items);
    return node;
  },

  remove(indicator) {
    this.items = this.items.filter(item => {
      return item !== indicator;
    });
    this.trigger(this.items);
  }

});
export default IndicatorStore;