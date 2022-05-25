import React from 'react';
// eslint-disable-next-line no-restricted-imports
import {mount} from 'enzyme';

import Layout from '../components/Layout.jsx';
import TaskDetails from '../components/TaskDetails.jsx';

describe('<Layout />', () => {
  it('should render <Layout />', () => {
    const task = [
      {
        task: {
          status: 'finished',
          app: {
            id: '1',
            name: 'freight',
          },
          number: 1108,
          dateCreated: '2017-07-21T21:40:31.056181Z',
          duration: 3.19,
          dateFinished: '2017-07-21T21:40:36.546140Z',
          id: '1115',
          estimatedDuration: 3.19,
          name: 'freight/production#1108',
          environment: 'production',
          dateStarted: '2017-07-21T21:40:33.358422Z',
          ref: 'master',
          sha: 'af008c78c235feae22f40bf76ed04747028fac6e',
        },
      },
    ];
    const result = mount(
      <Layout params={{}}>
        <TaskDetails params={{}} task={task} />
      </Layout>
    );
    // eslint-disable-next-line sentry/no-to-match-snapshot
    expect(result).toMatchSnapshot();
  });
});
