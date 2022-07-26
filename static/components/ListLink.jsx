import React from 'react';
import {Link, Navigation} from 'react-router';
import classSet from 'classnames';
import createReactClass from 'create-react-class';
import PropTypes from 'prop-types';

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

  mixins: [Navigation],

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
        <Link {...this.props}>{this.props.children}</Link>
      </li>
    );
  },
});

export default ListLink;
