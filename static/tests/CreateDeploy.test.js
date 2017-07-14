import React from 'react';
import renderer from 'react-test-renderer';
import CreateDeploy from '../components/CreateDeploy.jsx';

jest.mock('../components/CreateDeploy.jsx')
//TODO: figure out why snapshots are rendering null.
test('CreateDeploy Snapshot', () => {
  const component = renderer.create(
    <CreateDeploy />
  );
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
})
