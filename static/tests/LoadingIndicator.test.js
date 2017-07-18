import React from 'react';
import renderer from 'react-test-renderer';
import LoadingIndicator from '../components/LoadingIndicator.jsx';

test('LoadingIndicator Snapshot', () => {
  const component = renderer.create(
    <LoadingIndicator />
  );
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
})
