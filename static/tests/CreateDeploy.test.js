import React from 'react';
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
  const wrapper = mount(<CreateDeploy appList={appList} />);
  expect(wrapper).toMatchSnapshot();
});
