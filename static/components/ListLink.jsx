const React = require("react");
const Router = require("react-router");

const classSet = require('react/lib/cx');

const ListLink = React.createClass({
  displayName: 'ListLink',

  contextTypes: {
    router: React.PropTypes.func
  },

  propTypes: {
    activeClassName: React.PropTypes.string.isRequired,
    to: React.PropTypes.string.isRequired,
    params: React.PropTypes.object,
    query: React.PropTypes.object,
    onClick: React.PropTypes.func
  },

  getDefaultProps() {
    return {
      activeClassName: 'active'
    };
  },

  mixins: [
    Router.Navigation,
  ],

  getClassName() {
    var classNames = {};

    if (this.props.className)
      classNames[this.props.className] = true;

    if (this.isActive(this.props.to, this.props.params, this.props.query))
      classNames[this.props.activeClassName] = true;

    return classSet(classNames);
  },

  render() {
    return (
      <li className={this.getClassName()}>
        <Router.Link {...this.props}>
          {this.props.children}
        </Router.Link>
      </li>
    );
  }
});

export default ListLink;
