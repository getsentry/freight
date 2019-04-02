const PropTypes = require('prop-types');
const React = require('react');
const createReactClass = require('create-react-class');
const Router = require('react-router');

const classSet = require('classnames');

const ListLink = createReactClass({
  displayName: 'ListLink',

  propTypes: {
    activeClassName: PropTypes.string.isRequired,
    to: PropTypes.string.isRequired,
    params: PropTypes.object,
    query: PropTypes.object,
    onClick: PropTypes.func,
  },

  contextTypes: {
    router: PropTypes.object,
  },

  mixins: [Router.Navigation],

  getDefaultProps() {
    return {
      activeClassName: 'active',
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
    return (
      <li className={this.getClassName()}>
        <Router.Link {...this.props}>{this.props.children}</Router.Link>
      </li>
    );
  },
});

export default ListLink;
