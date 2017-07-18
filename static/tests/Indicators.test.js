import React from 'react';
import renderer from 'react-test-renderer';
import Indicators from '../components/Indicators.jsx';


test('Indicators Snapshot', () => {
  const component = renderer.create(
    <Indicators />
  );
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
})
