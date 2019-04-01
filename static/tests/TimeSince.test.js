import React from 'react';
import renderer from 'react-test-renderer';
import TimeSince from '../components/TimeSince.jsx';

test('TimeSince Snapshot', () => {
  const date = 1482363367071;
  const component = renderer.create(<TimeSince date={date} />);
  const tree = component.toJSON();
  expect(tree).toMatchSnapshot();
});
