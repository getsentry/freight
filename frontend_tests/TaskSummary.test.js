import React from 'react';
import PropTypes from 'prop-types';
import {mount} from 'enzyme';

import TaskSummary from '../components/TaskSummary.jsx';

//TODO: figure out why snapshots are rendering null.
test('TaskSummary Snapshot', () => {
  const task = {
    app: {
      id: '1',
      name: 'freight',
    },
    dateCreated: '2017-07-13T18:30:29.941695Z',
    dateFinished: '2017-07-13T18:30:45.484661Z',
    dateStarted: '2017-07-13T18:30:33.481500Z',
    duration: 12,
    environment: 'production',
    estimatedDuration: 12,
    id: '797',
    name: 'freight/production',
    number: 791,
    ref: 'master',
    sha: 'af56f6bc9843956c3ce92f9e7f9abb8c196340ee',
    status: 'finished',
    user: {
      dateCreated: '2017-06-21T17:39:22.706427Z',
      id: '3',
      name: 'james.andrews@sentry.io',
    },
  };
  const context = {
    context: {
      router: {},
    },
    contextTypes: {
      router: PropTypes.object.isRequired,
    },
  };

  const wrapper = mount(<TaskSummary task={task} />, context);
  expect(wrapper).toMatchSnapshot();
});
