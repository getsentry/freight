import React from 'react';
import renderer from 'react-test-renderer';
import CreateDeploy from '../components/CreateDeploy.jsx';
import { shallow } from 'enzyme';

test('CreateDeploy Snapshot', () => {
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
  }];
  const component = renderer.create(
    (<CreateDeploy appList={appList} />)
  );
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
})
