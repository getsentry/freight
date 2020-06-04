import { c as createCommonjsModule } from './common/_commonjsHelpers-a1c50d10.js';

/**
 * Copyright (c) 2013-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

var ReactPropTypesSecret = 'SECRET_DO_NOT_PASS_THIS_OR_YOU_WILL_BE_FIRED';

var ReactPropTypesSecret_1 = ReactPropTypesSecret;

function emptyFunction() {}
function emptyFunctionWithReset() {}
emptyFunctionWithReset.resetWarningCache = emptyFunction;

var factoryWithThrowingShims = function() {
  function shim(props, propName, componentName, location, propFullName, secret) {
    if (secret === ReactPropTypesSecret_1) {
      // It is still safe when called from React.
      return;
    }
    var err = new Error(
      'Calling PropTypes validators directly is not supported by the `prop-types` package. ' +
      'Use PropTypes.checkPropTypes() to call them. ' +
      'Read more at http://fb.me/use-check-prop-types'
    );
    err.name = 'Invariant Violation';
    throw err;
  }  shim.isRequired = shim;
  function getShim() {
    return shim;
  }  // Important!
  // Keep this list in sync with production version in `./factoryWithTypeCheckers.js`.
  var ReactPropTypes = {
    array: shim,
    bool: shim,
    func: shim,
    number: shim,
    object: shim,
    string: shim,
    symbol: shim,

    any: shim,
    arrayOf: getShim,
    element: shim,
    elementType: shim,
    instanceOf: getShim,
    node: shim,
    objectOf: getShim,
    oneOf: getShim,
    oneOfType: getShim,
    shape: getShim,
    exact: getShim,

    checkPropTypes: emptyFunctionWithReset,
    resetWarningCache: emptyFunction
  };

  ReactPropTypes.PropTypes = ReactPropTypes;

  return ReactPropTypes;
};

var propTypes = createCommonjsModule(function (module) {
/**
 * Copyright (c) 2013-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

{
  // By explicitly using `prop-types` you are opting into new production behavior.
  // http://fb.me/prop-types-in-prod
  module.exports = factoryWithThrowingShims();
}
});
var propTypes_1 = propTypes.array;
var propTypes_2 = propTypes.bool;
var propTypes_3 = propTypes.func;
var propTypes_4 = propTypes.number;
var propTypes_5 = propTypes.object;
var propTypes_6 = propTypes.string;
var propTypes_7 = propTypes.symbol;
var propTypes_8 = propTypes.any;
var propTypes_9 = propTypes.arrayOf;
var propTypes_10 = propTypes.element;
var propTypes_11 = propTypes.elementType;
var propTypes_12 = propTypes.instanceOf;
var propTypes_13 = propTypes.node;
var propTypes_14 = propTypes.objectOf;
var propTypes_15 = propTypes.oneOf;
var propTypes_16 = propTypes.oneOfType;
var propTypes_17 = propTypes.shape;
var propTypes_18 = propTypes.exact;
var propTypes_19 = propTypes.checkPropTypes;
var propTypes_20 = propTypes.resetWarningCache;
var propTypes_21 = propTypes.PropTypes;

export default propTypes;
export { propTypes_21 as PropTypes, propTypes_8 as any, propTypes_1 as array, propTypes_9 as arrayOf, propTypes_2 as bool, propTypes_19 as checkPropTypes, propTypes_10 as element, propTypes_11 as elementType, propTypes_18 as exact, propTypes_3 as func, propTypes_12 as instanceOf, propTypes_13 as node, propTypes_4 as number, propTypes_5 as object, propTypes_14 as objectOf, propTypes_15 as oneOf, propTypes_16 as oneOfType, propTypes_20 as resetWarningCache, propTypes_17 as shape, propTypes_6 as string, propTypes_7 as symbol };
