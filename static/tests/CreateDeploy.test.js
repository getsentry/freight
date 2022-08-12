import ReactRouter from 'react-router-dom';
// eslint-disable-next-line no-restricted-imports
import {mount} from 'enzyme';

import CreateDeploy from 'app/views/CreateDeploy.jsx';

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => null,
  useLocation: () => ({}),
  useOutletContext: jest.fn(),
}));

describe('CreateDeploy Snapshot', () => {
  beforeEach(() => {
    fetch.resetMocks();
  });

  it('should render', () => {
    fetch.mockResponse(({url}) => {
      let body = {};

      if (url === '/deploys/') {
        body = [];
      }

      return Promise.resolve({body: JSON.stringify(body)});
    });
    const appList = [
      {
        environments: {
          production: {
            defaultRef: 'master',
          },
          staging: {
            defaultRef: 'HEAD',
          },
        },
        id: '1',
        name: 'freight',
        repository: 'https://github.com/getsentry/freight.git',
      },
    ];

    jest.spyOn(ReactRouter, 'useOutletContext').mockReturnValue({appList});

    const wrapper = mount(<CreateDeploy appList={appList} />);
    // eslint-disable-next-line sentry/no-to-match-snapshot
    expect(wrapper).toMatchSnapshot();
  });
});
