import React from 'react';
import renderer from 'react-test-renderer';
import DeployChart from '../components/DeployChart.jsx';

test('DeployChart Snapshot', () => {
  const params = {
    "app": "freight",
    "env": "production",
    "number": "798"
  }
  const component = renderer.create(
    (<DeployChart params={params} />)
  );
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
})
