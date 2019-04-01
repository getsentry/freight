import React from 'react';
import {mount} from 'enzyme';

import TooltipTrigger from '../components/TooltipTrigger.jsx';

describe('<TooltipTrigger />', () => {
  it('should render a snapshot of <TooltipTrigger />', () => {
    const props = {
    "placement": "bottom",
    "title": <div>foo</div>,
    "viewport": {
      "selector": "body",
      "padding": 5
    }
    }

    const appList = [{
      "environments": {
        "production": {
          "defaultRef": "master"
        },
        "staging": {
          "defaultRef": "HEAD"
        },
      },
      "id": "1",
      "name": "freight",
      "repository": "https://github.com/getsentry/freight.git"
    }]


    const result = mount(<TooltipTrigger {...props} children={props.title} />);
    expect(result).toMatchSnapshot();
  })
})
