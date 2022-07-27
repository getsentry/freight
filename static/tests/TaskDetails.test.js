import React from 'react';
// eslint-disable-next-line no-restricted-imports
import {mount} from 'enzyme';

import TaskDetails from 'app/components/TaskDetails.jsx';

describe('TaskDetails', () => {
  beforeEach(() => {
    fetch.resetMocks();
  });

  it('renders', () => {
    const task = {
      id: '798',
      name: 'freight/production',
      app: {id: '1', name: 'freight'},
      remote: {name: 'github.com', url: 'https://github.com/getsentry/snuba'},
      user: {
        id: '377',
        name: 'rick@sentry.io',
        dateCreated: '2021-05-26T21:41:05.543205Z',
      },
      environment: 'production',
      sha: '6a553f3737c7e8899e4ae74bb9e233582e284c35',
      sha_url:
        'https://github.com/getsentry/snuba/freight/6a553f3737c7e8899e4ae74bb9e233582e284c35',
      ref: 'master',
      number: 1793,
      status: 'finished',
      duration: 110.24,
      estimatedDuration: 110.24,
      dateCreated: '2022-07-26T22:25:43.742910Z',
      dateStarted: '2022-07-26T22:25:45.520023Z',
      dateFinished: '2022-07-26T22:27:35.756332Z',
    };

    const logChunk = {
      nextOffset: 317,
      chunks: [
        {
          text: ">> Running ['git', 'fetch', '--all', '-p']\n",
          date: '2022-07-27T00:10:59.762610Z',
        },
        {
          text: ">> Running ['git', 'clone', '/tmp/freight-repo-2', '/tmp/freight-workspace-97fc0ea80d4011ed943bee12063bee96']\n>> Running ['git', 'reset', '--hard', '40639bb03537fc0e9ddf44967cd62e032967c723']\n>> Running Step 1 (Shell)\n>> Running ['echo', 'hellow']\nhellow\n>> Finished Step 1\n",
          date: '2022-07-27T00:11:02.291133Z',
        },
      ],
    };

    fetch.mockResponse(({url}) => {
      let body = {};

      if (url === '/api/0/deploys/freight/production/798/') {
        body = task;
      }

      if (url === '/api/0/deploys/freight/production/1793/log/?offset=0') {
        body = logChunk;
      }

      return Promise.resolve({body: JSON.stringify(body)});
    });

    const params = {
      app: 'freight',
      env: 'production',
      number: '798',
    };
    const wrapper = mount(<TaskDetails params={params} />);

    // eslint-disable-next-line sentry/no-to-match-snapshot
    expect(wrapper).toMatchSnapshot();
  });
});
