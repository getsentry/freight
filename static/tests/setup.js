import Adapter from '@wojtekmaj/enzyme-adapter-react-17';
// eslint-disable-next-line no-restricted-imports
import Enzyme from 'enzyme';
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
