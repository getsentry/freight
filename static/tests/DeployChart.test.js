import React from 'react';
// eslint-disable-next-line no-restricted-imports
import {mount} from 'enzyme';

import DeployChart from '../components/DeployChart.jsx';

test('DeployChart Snapshot', () => {
  const params = {
    app: 'freight',
    env: 'production',
    number: '798',
  };
  const wrapper = mount(<DeployChart params={params} />);
  // eslint-disable-next-line sentry/no-to-match-snapshot
  expect(wrapper).toMatchSnapshot();
});
