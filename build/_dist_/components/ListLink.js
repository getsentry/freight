import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';
import createReactClass from '/web_modules/create-react-class.js';
import * as Router from '/web_modules/react-router.js';
import classSet from '/web_modules/classnames.js';
const ListLink = createReactClass({
  displayName: 'ListLink',
  propTypes: {
    activeClassName: PropTypes.string.isRequired,
    to: PropTypes.string.isRequired,
    params: PropTypes.object,
    query: PropTypes.object,
    onClick: PropTypes.func
  },
  contextTypes: {
    router: PropTypes.object
  },
  mixins: [Router.Navigation],

  getDefaultProps() {
    return {
      activeClassName: 'active'
    };
  },

  getClassName() {
    const classNames = {};

    if (this.props.className) {
      classNames[this.props.className] = true;
    }

    if (this.isActive(this.props.to, this.props.params, this.props.query)) {
      classNames[this.props.activeClassName] = true;
    }

    return classSet(classNames);
  },

  render() {
    return /*#__PURE__*/React.createElement("li", {
      className: this.getClassName()
    }, /*#__PURE__*/React.createElement(Router.Link, this.props, this.props.children));
  }

});
export default ListLink;