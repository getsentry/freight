import React from 'react';
// eslint-disable-next-line no-restricted-imports
import {shallow} from 'enzyme';

import TimeSince from '../components/TimeSince.jsx';

test('TimeSince Snapshot', () => {
  jest.setSystemTime(new Date('2021-07-05'));
  const date = 1482363367071;
  const wrapper = shallow(<TimeSince date={date} />);
  // eslint-disable-next-line sentry/no-to-match-snapshot
  expect(wrapper).toMatchSnapshot();
});
