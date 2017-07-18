import React from 'react';
import renderer from 'react-test-renderer';
import Layout from '../components/Layout.jsx';
import {shallow} from 'enzyme';
import ReactTestUtils from 'react-dom/test-utils';

describe('<Layout />', () => {
  it('should render <Layout />', () => {

  const appList = [{
    "environments": {
      "production": {
        "defaultRef": "master"
      },
      "staging": {
        "defaultRef": "HEAD"
      },
    },
    "id": "1",
    "name": "freight",
    "repository": "https://github.com/getsentry/freight.git"
  }]

  const children = {
  "history": {
    "listenBefore": {},
    "listen": {},
    "transitionTo": {},
    "push": {},
    "replace": {},
    "go": {},
    "goBack": {},
    "goForward": {},
    "createKey": {},
    "createPath": {},
    "createHref": {},
    "createLocation": {},
    "setState": {},
    "registerTransitionHook": {},
    "unregisterTransitionHook": {},
    "pushState": {},
    "replaceState": {},
    "isActive": {},
    "match": {},
    "listenBeforeLeavingRoute": {}
  },
  "location": {
    "pathname": "/",
    "search": "",
    "hash": "",
    "state": null,
    "action": "PUSH",
    "key": "m0qx3x",
    "basename": "/",
    "query": {},
    "$searchBase": {}
  },
  "params": {},
  "route": {
    "exact": true,
    "path": "/",
    "component": {},
    "indexRoute": {},
    "childRoutes": {}
  },
  "routeParams": {},
  "routes": [
    {},
    {}
  ]
}

const shallowRenderer = ReactTestUtils.createRenderer();
const result = shallowRenderer.render(<Layout children={children} />);
expect(result).toMatchSnapshot();
  })
})
