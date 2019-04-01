import React from 'react';
import {mount} from 'enzyme';
import Duration from '../components/Duration.jsx';

test('Duration Snapshot', () => {
  const wrapper = mount(<Duration seconds="13.67" className="duration" />);
  expect(wrapper).toMatchSnapshot();
});
