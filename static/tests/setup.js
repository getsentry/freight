// eslint-disable-next-line no-restricted-imports
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';
import jestFetchMock from 'jest-fetch-mock';

/**
 * Enzyme configuration
 */
Enzyme.configure({adapter: new Adapter()});

/**
 * Mock fetches
 */
jestFetchMock.enableMocks();

Object.defineProperty(window, 'scrollTo', {value: () => {}, writable: true});
