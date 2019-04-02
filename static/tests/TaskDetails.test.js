import React from 'react';
import {mount} from 'enzyme';
import TaskDetails from '../components/TaskDetails.jsx';

test('TaskDetails Snapshot', () => {
  const params = {
    app: 'freight',
    env: 'production',
    number: '798',
  };
  const wrapper = mount(<TaskDetails params={params} />);
  expect(wrapper).toMatchSnapshot();
});
