import React from 'react';
import renderer from 'react-test-renderer';
import BarChart from '../components/BarChart.jsx';


test('BarChart Snapshot', () => {
  const component = renderer.create(
    <BarChart />
  );
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
})
