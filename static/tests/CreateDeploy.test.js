import React from 'react';
// eslint-disable-next-line no-restricted-imports
import {mount} from 'enzyme';

import CreateDeploy from '../components/CreateDeploy.jsx';

test('CreateDeploy Snapshot', () => {
  const appList = [
    {
      environments: {
        production: {
          defaultRef: 'master',
        },
        staging: {
          defaultRef: 'HEAD',
        },
      },
      id: '1',
      name: 'freight',
      repository: 'https://github.com/getsentry/freight.git',
    },
  ];
  const wrapper = mount(<CreateDeploy appList={appList} location={{}} />);
  // eslint-disable-next-line sentry/no-to-match-snapshot
  expect(wrapper).toMatchSnapshot();
});
