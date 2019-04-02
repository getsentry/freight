import jQuery from 'jquery';
import Adapter from 'enzyme-adapter-react-16';
import Enzyme from 'enzyme';

/**
 * Enzyme configuration
 */
Enzyme.configure({adapter: new Adapter()});

window.$ = window.jQuery = jQuery;
