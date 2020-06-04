import React from 'react';
import createReactClass from 'create-react-class';
import Reflux from 'reflux';
import IndicatorStore from '../stores/indicatorStore';

const Indicators = createReactClass({
  displayName: 'Indicators',

  mixins: [Reflux.connect(IndicatorStore, 'items')],

  getInitialState() {
    return {
      items: [],
    };
  },

  render() {
    return (
      <div {...this.props}>
        {this.state.items.map(function(item, key) {
          return <div key={key}>{item}</div>;
        })}
      </div>
    );
  },
});

export default Indicators;
