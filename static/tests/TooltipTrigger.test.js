import React from 'react';
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
    expect(result).toMatchSnapshot();
  });
});
