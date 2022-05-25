// eslint-disable-next-line no-restricted-imports
import Enzyme from 'enzyme';
import Adapter from 'enzyme-adapter-react-16';
import jQuery from 'jquery';

/**
 * Enzyme configuration
 */
Enzyme.configure({adapter: new Adapter()});

window.$ = window.jQuery = jQuery;
