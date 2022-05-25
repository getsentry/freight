import React from 'react';
// eslint-disable-next-line no-restricted-imports
import {shallow} from 'enzyme';

import AppSettings from '../components/AppSettings.jsx';

test('AppSettings Snapshot', () => {
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
  const wrapper = shallow(<AppSettings params={appList} />, {context: {}});
  // eslint-disable-next-line sentry/no-to-match-snapshot
  expect(wrapper).toMatchSnapshot();
});
