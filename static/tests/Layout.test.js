import React from 'react';
import renderer from 'react-test-renderer';
import Layout from '../components/Layout.jsx';
import {shallow} from 'enzyme';
import ReactTestUtils from 'react-dom/test-utils';
import TaskDetails from '../components/TaskDetails.jsx'

describe('<Layout />', () => {
  it('should render <Layout />', () => {

  const task = [{
  "task": {
    "status": "finished",
    "app": {
      "id": "1",
      "name": "freight"
    },
    "number": 1108,
    "dateCreated": "2017-07-21T21:40:31.056181Z",
    "duration": 3.19,
    "dateFinished": "2017-07-21T21:40:36.546140Z",
    "id": "1115",
    "estimatedDuration": 3.19,
    "name": "freight/production#1108",
    "environment": "production",
    "sha": "af008c78c235feae22f40bf76ed04747028fac6e",
    "dateStarted": "2017-07-21T21:40:33.358422Z",
    "ref": "master",
    "sha": "af008c78c235feae22f40bf76ed04747028fac6e",
    "status": "finished"
  }
}]
  const shallowRenderer = ReactTestUtils.createRenderer();
  const result = shallowRenderer.render(<TaskDetails task={task} />);
  expect(result).toMatchSnapshot();
  })
})
