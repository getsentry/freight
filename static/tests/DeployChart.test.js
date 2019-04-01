import React from 'react';
import {mount} from 'enzyme';

import DeployChart from '../components/DeployChart.jsx';

test('DeployChart Snapshot', () => {
  const params = {
    "app": "freight",
    "env": "production",
    "number": "798"
  }
  const wrapper = mount(
    <DeployChart params={params} />
  );
  expect(wrapper).toMatchSnapshot();
})
