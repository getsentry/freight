import React from 'react';
import renderer from 'react-test-renderer';
import TaskDetails from '../components/TaskDetails.jsx';

test('TaskDetails Snapshot', () => {
  const params = {
    "app": "freight",
    "env": "production",
    "number": "798"
  }
  const component = renderer.create(
    (<TaskDetails params={params} />)
  );
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
})
