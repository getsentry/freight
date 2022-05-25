import React from 'react';
// eslint-disable-next-line no-restricted-imports
import {mount} from 'enzyme';

import Duration from '../components/Duration.jsx';

test('Duration Snapshot', () => {
  const wrapper = mount(<Duration seconds={13.67} className="duration" />);
  // eslint-disable-next-line sentry/no-to-match-snapshot
  expect(wrapper).toMatchSnapshot();
});
