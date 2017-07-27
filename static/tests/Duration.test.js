import React from 'react';
import renderer from 'react-test-renderer';
import Duration from '../components/Duration.jsx';

test('Duration Snapshot', () => {
  const component = renderer.create(
    (<Duration seconds="13.67" className="duration" />)
  );
  let tree = component.toJSON();
  expect(tree).toMatchSnapshot();
})
