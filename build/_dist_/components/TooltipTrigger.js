function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

import ReactDOM from '/web_modules/react-dom.js';
import PropTypes from '/web_modules/prop-types.js';
import ReactDOMServer from '/web_modules/react-dom/server.js';
import React from '/web_modules/react.js';
import $ from '/web_modules/jquery.js'; // window.jQuery = $;
// import 'bootstrap/js/tooltip';

class TooltipTrigger extends React.Component {
  componentDidMount() {// These can be configured via options; this is just a demo
    // $(ReactDOM.findDOMNode(this)).tooltip({
    //   // eslint-disable-line
    //   html: true,
    //   placement: this.props.placement,
    //   title: ReactDOMServer.renderToString(this.props.title),
    //   viewport: this.props.viewport,
    // });
  }

  componentWillUnmount() {// const node = $(ReactDOM.findDOMNode(this)); // eslint-disable-line
    // node.tooltip('destroy');
    // node.unbind(
    //   'show.bs.tooltip',
    //   'shown.bs.tooltip',
    //   'hide.bs.tooltip',
    //   'hidden.bs.tooltip'
    // );
  }

  render() {
    return this.props.children;
  }

}

_defineProperty(TooltipTrigger, "propTypes", {
  title: PropTypes.node.isRequired,
  placement: PropTypes.string,
  viewport: PropTypes.shape({
    selector: PropTypes.string,
    padding: PropTypes.number
  })
});

_defineProperty(TooltipTrigger, "defaultProps", {
  placement: 'left',
  viewport: {
    selector: 'body',
    padding: 5
  }
});

export default TooltipTrigger;