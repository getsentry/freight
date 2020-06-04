import React from '/web_modules/react.js';
import createReactClass from '/web_modules/create-react-class.js';
import Reflux from '/web_modules/reflux.js';
import IndicatorStore from '../stores/indicatorStore.js';
const Indicators = createReactClass({
  displayName: 'Indicators',
  mixins: [Reflux.connect(IndicatorStore, 'items')],

  getInitialState() {
    return {
      items: []
    };
  },

  render() {
    return /*#__PURE__*/React.createElement("div", this.props, this.state.items.map(function (item, key) {
      return /*#__PURE__*/React.createElement("div", {
        key: key
      }, item);
    }));
  }

});
export default Indicators;