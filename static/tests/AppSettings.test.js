import React from 'react';
import renderer from 'react-test-renderer';
import AppSettings from '../components/AppSettings.jsx';


test('AppSettings Snapshot', () => {
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
    <AppSettings params={appList} />
  );
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
})
