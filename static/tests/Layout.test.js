import * as React from 'react';
// eslint-disable-next-line no-restricted-imports
import {mount} from 'enzyme';

import Layout from 'app/components/Layout.jsx';

function Content({appList}) {
  return <div>app count: {appList.length}</div>;
}

describe('Layout', () => {
  beforeEach(() => {
    fetch.resetMocks();
  });

  it('should render <Layout />', () => {
    fetch.mockResponse(({url}) => {
      let body = {};

      if (url === '/api/0/config/') {
        body = {};
      }

      if (url === '/api/0/config/') {
        body = [];
      }

      return Promise.resolve({body: JSON.stringify(body)});
    });

    const params = {
      app: 'freight',
      env: 'production',
      number: '1115',
    };

    const result = mount(
      <Layout params={params}>
        <Content />
      </Layout>
    );

    // eslint-disable-next-line sentry/no-to-match-snapshot
    expect(result).toMatchSnapshot();
  });
});
