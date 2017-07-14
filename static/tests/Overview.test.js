import React from 'react';
import renderer from 'react-test-renderer';
import Overview from '../components/Overview.jsx';

test('Overview Snapshot', () => {
  const component = renderer.create(
    <Overview />
  );
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
})
