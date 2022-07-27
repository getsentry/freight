import React from 'react';
// eslint-disable-next-line no-restricted-imports
import {mount} from 'enzyme';

import DeployChart from '../components/DeployChart.jsx';

describe('DeployChart', () => {
  beforeEach(() => {
    fetch.resetMocks();
  });

  it('renders', () => {
    const stats = [
      [1656288000, 24],
      [1656374400, 35],
      [1656460800, 37],
      [1656547200, 22],
      [1656633600, 5],
      [1656720000, 0],
      [1656806400, 0],
      [1656892800, 9],
      [1656979200, 21],
      [1657065600, 30],
      [1657152000, 21],
      [1657238400, 22],
      [1657324800, 0],
      [1657411200, 0],
      [1657497600, 24],
      [1657584000, 28],
      [1657670400, 41],
      [1657756800, 30],
      [1657843200, 30],
      [1657929600, 2],
      [1658016000, 0],
      [1658102400, 19],
      [1658188800, 20],
      [1658275200, 37],
      [1658361600, 23],
      [1658448000, 24],
      [1658534400, 3],
      [1658620800, 0],
      [1658707200, 21],
      [1658793600, 19],
      [1658880000, 0],
    ];

    fetch.mockResponse(({url}) => {
      let body = {};

      if (url === '/api/0/deploy-stats/') {
        body = stats;
      }

      return Promise.resolve({body: JSON.stringify(body)});
    });

    const params = {
      app: 'freight',
      env: 'production',
      number: '798',
    };
    const wrapper = mount(<DeployChart params={params} />);
    // eslint-disable-next-line sentry/no-to-match-snapshot
    expect(wrapper).toMatchSnapshot();
  });
});
