import React from 'react';
// eslint-disable-next-line no-restricted-imports
import {mount} from 'enzyme';

import TooltipTrigger from '../components/TooltipTrigger.jsx';

describe('<TooltipTrigger />', () => {
  it('should render a snapshot of <TooltipTrigger />', () => {
    const props = {
      placement: 'bottom',
      title: <div>foo</div>,
      viewport: {
        selector: 'body',
        padding: 5,
      },
    };

    const result = mount(<TooltipTrigger {...props}>{props.title}</TooltipTrigger>);
    // eslint-disable-next-line sentry/no-to-match-snapshot
    expect(result).toMatchSnapshot();
  });
});
