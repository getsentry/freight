import React from 'react';
import renderer from 'react-test-renderer';
import AppDetails from '../components/AppDetails.jsx';

jest.mock('../components/AppDetails.jsx')
//TODO: figure out why snapshots are rendering null.
function createNodeMock(element){
  if(element.type === 'p'){
    return {}
  }
  return null
}

it('AppDetails Snapshot', () => {
  const options = {createNodeMock}

  const component = renderer.create(<AppDetails/> , options);
  expect(component).toMatchSnapshot();
})
