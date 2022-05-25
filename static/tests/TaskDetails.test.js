import React from 'react';
// eslint-disable-next-line no-restricted-imports
import {mount} from 'enzyme';

import TaskDetails from '../components/TaskDetails.jsx';

test('TaskDetails Snapshot', () => {
  const params = {
    app: 'freight',
    env: 'production',
    number: '798',
  };
  const wrapper = mount(<TaskDetails params={params} />);
  // eslint-disable-next-line sentry/no-to-match-snapshot
  expect(wrapper).toMatchSnapshot();
});
