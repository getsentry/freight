import ReactDOM from 'react-dom';
import PropTypes from 'prop-types';
import ReactDOMServer from 'react-dom/server';
import React from 'react';
import $ from 'jquery';

// window.jQuery = $;
// import 'bootstrap/js/tooltip';

class TooltipTrigger extends React.Component {
  static propTypes = {
    title: PropTypes.node.isRequired,
    placement: PropTypes.string,
    viewport: PropTypes.shape({
      selector: PropTypes.string,
      padding: PropTypes.number,
    }),
  };

  static defaultProps = {
    placement: 'left',
    viewport: {
      selector: 'body',
      padding: 5,
    },
  };

  componentDidMount() {
    // These can be configured via options; this is just a demo
    // $(ReactDOM.findDOMNode(this)).tooltip({
    //   // eslint-disable-line
    //   html: true,
    //   placement: this.props.placement,
    //   title: ReactDOMServer.renderToString(this.props.title),
    //   viewport: this.props.viewport,
    // });
  }

  componentWillUnmount() {
    // const node = $(ReactDOM.findDOMNode(this)); // eslint-disable-line
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

export default TooltipTrigger;
