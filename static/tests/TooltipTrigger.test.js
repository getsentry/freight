import React from 'react';
import renderer from 'react-test-renderer';
import TooltipTrigger from '../components/TooltipTrigger.jsx';
import {shallow} from 'enzyme';
import ReactTestUtils from 'react-dom/test-utils';

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


    const shallowRenderer = ReactTestUtils.createRenderer();
    const result = shallowRenderer.render(<TooltipTrigger {...props} children={props.title} />);
    expect(result).toMatchSnapshot();
  })
})
