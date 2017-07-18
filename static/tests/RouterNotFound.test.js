import React from 'react';
import renderer from 'react-test-renderer';
import RouteNotFound from '../components/RouteNotFound.jsx';


test('RouteNotFound Snapshot', () => {
  const component = renderer.create(
    <RouteNotFound />
  );
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
})
