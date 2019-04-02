import React from 'react';
import {shallow} from 'enzyme';
import TimeSince from '../components/TimeSince.jsx';

test('TimeSince Snapshot', () => {
  const date = 1482363367071;
  const wrapper = shallow(<TimeSince date={date} />);
  expect(wrapper).toMatchSnapshot();
});
