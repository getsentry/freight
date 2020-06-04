import { c as createCommonjsModule, u as unwrapExports } from './common/_commonjsHelpers-a1c50d10.js';
import { r as react } from './common/index-657f9102.js';

var ActionMethods = createCommonjsModule(function (module, exports) {

Object.defineProperty(exports, "__esModule", {
  value: true
});
});

unwrapExports(ActionMethods);

var eventemitter3 = createCommonjsModule(function (module) {

var has = Object.prototype.hasOwnProperty;

//
// We store our EE objects in a plain object whose properties are event names.
// If `Object.create(null)` is not supported we prefix the event names with a
// `~` to make sure that the built-in object properties are not overridden or
// used as an attack vector.
// We also assume that `Object.create(null)` is available when the event name
// is an ES6 Symbol.
//
var prefix = typeof Object.create !== 'function' ? '~' : false;

/**
 * Representation of a single EventEmitter function.
 *
 * @param {Function} fn Event handler to be called.
 * @param {Mixed} context Context for function execution.
 * @param {Boolean} [once=false] Only emit once
 * @api private
 */
function EE(fn, context, once) {
  this.fn = fn;
  this.context = context;
  this.once = once || false;
}

/**
 * Minimal EventEmitter interface that is molded against the Node.js
 * EventEmitter interface.
 *
 * @constructor
 * @api public
 */
function EventEmitter() { /* Nothing to set */ }

/**
 * Hold the assigned EventEmitters by name.
 *
 * @type {Object}
 * @private
 */
EventEmitter.prototype._events = undefined;

/**
 * Return an array listing the events for which the emitter has registered
 * listeners.
 *
 * @returns {Array}
 * @api public
 */
EventEmitter.prototype.eventNames = function eventNames() {
  var events = this._events
    , names = []
    , name;

  if (!events) return names;

  for (name in events) {
    if (has.call(events, name)) names.push(prefix ? name.slice(1) : name);
  }

  if (Object.getOwnPropertySymbols) {
    return names.concat(Object.getOwnPropertySymbols(events));
  }

  return names;
};

/**
 * Return a list of assigned event listeners.
 *
 * @param {String} event The events that should be listed.
 * @param {Boolean} exists We only need to know if there are listeners.
 * @returns {Array|Boolean}
 * @api public
 */
EventEmitter.prototype.listeners = function listeners(event, exists) {
  var evt = prefix ? prefix + event : event
    , available = this._events && this._events[evt];

  if (exists) return !!available;
  if (!available) return [];
  if (available.fn) return [available.fn];

  for (var i = 0, l = available.length, ee = new Array(l); i < l; i++) {
    ee[i] = available[i].fn;
  }

  return ee;
};

/**
 * Emit an event to all registered event listeners.
 *
 * @param {String} event The name of the event.
 * @returns {Boolean} Indication if we've emitted an event.
 * @api public
 */
EventEmitter.prototype.emit = function emit(event, a1, a2, a3, a4, a5) {
  var evt = prefix ? prefix + event : event;

  if (!this._events || !this._events[evt]) return false;

  var listeners = this._events[evt]
    , len = arguments.length
    , args
    , i;

  if ('function' === typeof listeners.fn) {
    if (listeners.once) this.removeListener(event, listeners.fn, undefined, true);

    switch (len) {
      case 1: return listeners.fn.call(listeners.context), true;
      case 2: return listeners.fn.call(listeners.context, a1), true;
      case 3: return listeners.fn.call(listeners.context, a1, a2), true;
      case 4: return listeners.fn.call(listeners.context, a1, a2, a3), true;
      case 5: return listeners.fn.call(listeners.context, a1, a2, a3, a4), true;
      case 6: return listeners.fn.call(listeners.context, a1, a2, a3, a4, a5), true;
    }

    for (i = 1, args = new Array(len -1); i < len; i++) {
      args[i - 1] = arguments[i];
    }

    listeners.fn.apply(listeners.context, args);
  } else {
    var length = listeners.length
      , j;

    for (i = 0; i < length; i++) {
      if (listeners[i].once) this.removeListener(event, listeners[i].fn, undefined, true);

      switch (len) {
        case 1: listeners[i].fn.call(listeners[i].context); break;
        case 2: listeners[i].fn.call(listeners[i].context, a1); break;
        case 3: listeners[i].fn.call(listeners[i].context, a1, a2); break;
        default:
          if (!args) for (j = 1, args = new Array(len -1); j < len; j++) {
            args[j - 1] = arguments[j];
          }

          listeners[i].fn.apply(listeners[i].context, args);
      }
    }
  }

  return true;
};

/**
 * Register a new EventListener for the given event.
 *
 * @param {String} event Name of the event.
 * @param {Function} fn Callback function.
 * @param {Mixed} [context=this] The context of the function.
 * @api public
 */
EventEmitter.prototype.on = function on(event, fn, context) {
  var listener = new EE(fn, context || this)
    , evt = prefix ? prefix + event : event;

  if (!this._events) this._events = prefix ? {} : Object.create(null);
  if (!this._events[evt]) this._events[evt] = listener;
  else {
    if (!this._events[evt].fn) this._events[evt].push(listener);
    else this._events[evt] = [
      this._events[evt], listener
    ];
  }

  return this;
};

/**
 * Add an EventListener that's only called once.
 *
 * @param {String} event Name of the event.
 * @param {Function} fn Callback function.
 * @param {Mixed} [context=this] The context of the function.
 * @api public
 */
EventEmitter.prototype.once = function once(event, fn, context) {
  var listener = new EE(fn, context || this, true)
    , evt = prefix ? prefix + event : event;

  if (!this._events) this._events = prefix ? {} : Object.create(null);
  if (!this._events[evt]) this._events[evt] = listener;
  else {
    if (!this._events[evt].fn) this._events[evt].push(listener);
    else this._events[evt] = [
      this._events[evt], listener
    ];
  }

  return this;
};

/**
 * Remove event listeners.
 *
 * @param {String} event The event we want to remove.
 * @param {Function} fn The listener that we need to find.
 * @param {Mixed} context Only remove listeners matching this context.
 * @param {Boolean} once Only remove once listeners.
 * @api public
 */
EventEmitter.prototype.removeListener = function removeListener(event, fn, context, once) {
  var evt = prefix ? prefix + event : event;

  if (!this._events || !this._events[evt]) return this;

  var listeners = this._events[evt]
    , events = [];

  if (fn) {
    if (listeners.fn) {
      if (
           listeners.fn !== fn
        || (once && !listeners.once)
        || (context && listeners.context !== context)
      ) {
        events.push(listeners);
      }
    } else {
      for (var i = 0, length = listeners.length; i < length; i++) {
        if (
             listeners[i].fn !== fn
          || (once && !listeners[i].once)
          || (context && listeners[i].context !== context)
        ) {
          events.push(listeners[i]);
        }
      }
    }
  }

  //
  // Reset the array, or remove it completely if we have no more listeners.
  //
  if (events.length) {
    this._events[evt] = events.length === 1 ? events[0] : events;
  } else {
    delete this._events[evt];
  }

  return this;
};

/**
 * Remove all listeners or only the listeners for the specified event.
 *
 * @param {String} event The event want to remove all listeners for.
 * @api public
 */
EventEmitter.prototype.removeAllListeners = function removeAllListeners(event) {
  if (!this._events) return this;

  if (event) delete this._events[prefix ? prefix + event : event];
  else this._events = prefix ? {} : Object.create(null);

  return this;
};

//
// Alias methods names because people roll like that.
//
EventEmitter.prototype.off = EventEmitter.prototype.removeListener;
EventEmitter.prototype.addListener = EventEmitter.prototype.on;

//
// This function doesn't apply anymore.
//
EventEmitter.prototype.setMaxListeners = function setMaxListeners() {
  return this;
};

//
// Expose the prefix.
//
EventEmitter.prefixed = prefix;

//
// Expose the module.
//
{
  module.exports = EventEmitter;
}
});

var utils = createCommonjsModule(function (module, exports) {

Object.defineProperty(exports, "__esModule", {
    value: true
});

var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

exports.capitalize = capitalize;
exports.callbackName = callbackName;
exports.isObject = isObject;
exports.extend = extend;
exports.isFunction = isFunction;
exports.nextTick = nextTick;
exports.object = object;
exports.isArguments = isArguments;
exports.throwIf = throwIf;
function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function callbackName(string, prefix) {
    prefix = prefix || "on";
    return prefix + exports.capitalize(string);
}

/*
 * isObject, extend, isFunction, isArguments are taken from underscore/lodash in
 * order to remove the dependency
 */
function isObject(obj) {
    var type = typeof obj === "undefined" ? "undefined" : _typeof(obj);
    return type === "function" || type === "object" && !!obj;
}

function extend(obj) {
    if (!isObject(obj)) {
        return obj;
    }
    var source, keys, prop;
    for (var i = 1, length = arguments.length; i < length; i++) {
        source = arguments[i];
        keys = Object.keys(source);
        for (var j = 0; j < keys.length; j++) {
            prop = keys[j];
            if (Object.getOwnPropertyDescriptor && Object.defineProperty) {
                var propertyDescriptor = Object.getOwnPropertyDescriptor(source, prop);
                Object.defineProperty(obj, prop, propertyDescriptor);
            } else {
                obj[prop] = source[prop];
            }
        }
    }
    return obj;
}

function isFunction(value) {
    return typeof value === "function";
}

exports.EventEmitter = eventemitter3;

function nextTick(callback) {
    setTimeout(callback, 0);
}

function object(keys, vals) {
    var o = {},
        i = 0;
    for (; i < keys.length; i++) {
        o[keys[i]] = vals[i];
    }
    return o;
}

function isArguments(value) {
    return (typeof value === "undefined" ? "undefined" : _typeof(value)) === "object" && "callee" in value && typeof value.length === "number";
}

function throwIf(val, msg) {
    if (val) {
        throw Error(msg || val);
    }
}
});

unwrapExports(utils);
var utils_1 = utils.capitalize;
var utils_2 = utils.callbackName;
var utils_3 = utils.isObject;
var utils_4 = utils.extend;
var utils_5 = utils.isFunction;
var utils_6 = utils.nextTick;
var utils_7 = utils.object;
var utils_8 = utils.isArguments;
var utils_9 = utils.throwIf;
var utils_10 = utils.EventEmitter;

var Keep = createCommonjsModule(function (module, exports) {

Object.defineProperty(exports, "__esModule", {
	value: true
});

// this needs to be set to true before Keep.js starts storing, done via useKeep
var use = false;

var createdStores = [];

var createdActions = [];

function useKeep() {
	var bool = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : true;

	use = bool;
}

function addStore(str) {
	if (use) {
		createdStores.push(str);
	}
}

function addAction(act) {
	if (use) {
		createdActions.push(act);
	}
}

function reset() {
	while (createdStores.length) {
		createdStores.pop();
	}
	while (createdActions.length) {
		createdActions.pop();
	}
}

exports.useKeep = useKeep;
exports.addStore = addStore;
exports.addAction = addAction;
exports.createdStores = createdStores;
exports.createdActions = createdActions;
exports.reset = reset;
});

unwrapExports(Keep);
var Keep_1 = Keep.useKeep;
var Keep_2 = Keep.addStore;
var Keep_3 = Keep.addAction;
var Keep_4 = Keep.createdStores;
var Keep_5 = Keep.createdActions;
var Keep_6 = Keep.reset;

var mixer = createCommonjsModule(function (module, exports) {

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.mix = mix;



var _ = _interopRequireWildcard(utils);

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

function mix(def) {
    var composed = {
        init: [],
        preEmit: [],
        shouldEmit: []
    };

    var updated = function mixDef(mixin) {
        var mixed = {};
        if (mixin.mixins) {
            mixin.mixins.forEach(function (subMixin) {
                _.extend(mixed, mixDef(subMixin));
            });
        }
        _.extend(mixed, mixin);
        Object.keys(composed).forEach(function (composable) {
            if (mixin.hasOwnProperty(composable)) {
                composed[composable].push(mixin[composable]);
            }
        });
        return mixed;
    }(def);

    if (composed.init.length > 1) {
        updated.init = function () {
            var args = arguments;
            composed.init.forEach(function (init) {
                init.apply(this, args);
            }, this);
        };
    }
    if (composed.preEmit.length > 1) {
        updated.preEmit = function () {
            return composed.preEmit.reduce(function (args, preEmit) {
                var newValue = preEmit.apply(this, args);
                return newValue === undefined ? args : [newValue];
            }.bind(this), arguments);
        };
    }
    if (composed.shouldEmit.length > 1) {
        updated.shouldEmit = function () {
            var args = arguments;
            return !composed.shouldEmit.some(function (shouldEmit) {
                return !shouldEmit.apply(this, args);
            }, this);
        };
    }
    Object.keys(composed).forEach(function (composable) {
        if (composed[composable].length === 1) {
            updated[composable] = composed[composable][0];
        }
    });

    return updated;
}
});

unwrapExports(mixer);
var mixer_1 = mixer.mix;

var bindMethods_1 = createCommonjsModule(function (module, exports) {

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.bindMethods = bindMethods;
function bindMethods(store, definition) {
    for (var name in definition) {
        if (Object.getOwnPropertyDescriptor && Object.defineProperty) {
            var propertyDescriptor = Object.getOwnPropertyDescriptor(definition, name);

            if (!propertyDescriptor.value || typeof propertyDescriptor.value !== "function" || !definition.hasOwnProperty(name)) {
                continue;
            }

            store[name] = definition[name].bind(store);
        } else {
            var property = definition[name];

            if (typeof property !== "function" || !definition.hasOwnProperty(name)) {
                continue;
            }

            store[name] = property.bind(store);
        }
    }

    return store;
}
});

unwrapExports(bindMethods_1);
var bindMethods_2 = bindMethods_1.bindMethods;

var StoreMethods = createCommonjsModule(function (module, exports) {

Object.defineProperty(exports, "__esModule", {
  value: true
});
});

unwrapExports(StoreMethods);

var PublisherMethods = createCommonjsModule(function (module, exports) {

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.deferWith = exports.triggerAsync = exports.trigger = exports.listen = exports.shouldEmit = exports.preEmit = undefined;



var _ = _interopRequireWildcard(utils);

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

/**
 * A module of methods for object that you want to be able to listen to.
 * This module is consumed by `createStore` and `createAction`
 */

/**
 * Hook used by the publisher that is invoked before emitting
 * and before `shouldEmit`. The arguments are the ones that the action
 * is invoked with. If this function returns something other than
 * undefined, that will be passed on as arguments for shouldEmit and
 * emission.
 */
var preEmit = exports.preEmit = function preEmit() {};

/**
 * Hook used by the publisher after `preEmit` to determine if the
 * event should be emitted with given arguments. This may be overridden
 * in your application, default implementation always returns true.
 *
 * @returns {Boolean} true if event should be emitted
 */
var shouldEmit = exports.shouldEmit = function shouldEmit() {
    return true;
};

/**
 * Subscribes the given callback for action triggered
 *
 * @param {Function} callback The callback to register as event handler
 * @param {Mixed} [optional] bindContext The context to bind the callback with
 * @returns {Function} Callback that unsubscribes the registered event handler
 */
var listen = exports.listen = function listen(callback, bindContext) {
    bindContext = bindContext || this;
    var eventHandler = function eventHandler(args) {
        if (aborted) {
            return;
        }
        callback.apply(bindContext, args);
    },
        me = this,
        aborted = false;
    this.emitter.addListener(this.eventLabel, eventHandler);
    return function () {
        aborted = true;
        me.emitter.removeListener(me.eventLabel, eventHandler);
    };
};

/**
 * Publishes an event using `this.emitter` (if `shouldEmit` agrees)
 */
var trigger = exports.trigger = function trigger() {
    var args = arguments,
        pre = this.preEmit.apply(this, args);
    args = pre === undefined ? args : _.isArguments(pre) ? pre : [].concat(pre);
    if (this.shouldEmit.apply(this, args)) {
        this.emitter.emit(this.eventLabel, args);
    }
};

/**
 * Tries to publish the event on the next tick
 */
var triggerAsync = exports.triggerAsync = function triggerAsync() {
    var args = arguments,
        me = this;
    _.nextTick(function () {
        me.trigger.apply(me, args);
    });
};

/**
 * Wraps the trigger mechanism with a deferral function.
 *
 * @param {Function} callback the deferral function,
 *        first argument is the resolving function and the
 *        rest are the arguments provided from the previous
 *        trigger invocation
 */
var deferWith = exports.deferWith = function deferWith(callback) {
    var oldTrigger = this.trigger,
        ctx = this,
        resolver = function resolver() {
        oldTrigger.apply(ctx, arguments);
    };
    this.trigger = function () {
        callback.apply(ctx, [resolver].concat([].splice.call(arguments, 0)));
    };
};
});

unwrapExports(PublisherMethods);
var PublisherMethods_1 = PublisherMethods.deferWith;
var PublisherMethods_2 = PublisherMethods.triggerAsync;
var PublisherMethods_3 = PublisherMethods.trigger;
var PublisherMethods_4 = PublisherMethods.listen;
var PublisherMethods_5 = PublisherMethods.shouldEmit;
var PublisherMethods_6 = PublisherMethods.preEmit;

var createStore_1 = createCommonjsModule(function (module, exports) {

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.createStore = createStore;



var _ = _interopRequireWildcard(utils);



var Keep$1 = _interopRequireWildcard(Keep);







var StoreMethods$1 = _interopRequireWildcard(StoreMethods);



var PublisherMethods$1 = _interopRequireWildcard(PublisherMethods);



var ListenerMethods$1 = _interopRequireWildcard(ListenerMethods);

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

var allowed = { preEmit: 1, shouldEmit: 1 };

/**
 * Creates an event emitting Data Store. It is mixed in with functions
 * from the `ListenerMethods` and `PublisherMethods` mixins. `preEmit`
 * and `shouldEmit` may be overridden in the definition object.
 *
 * @param {Object} definition The data store object definition
 * @returns {Store} A data store instance
 */
function createStore(definition) {

    definition = definition || {};

    for (var a in StoreMethods$1) {
        if (!allowed[a] && (PublisherMethods$1[a] || ListenerMethods$1[a])) {
            throw new Error("Cannot override API method " + a + " in Reflux.StoreMethods. Use another method name or override it on Reflux.PublisherMethods / Reflux.ListenerMethods instead.");
        }
    }

    for (var d in definition) {
        if (!allowed[d] && (PublisherMethods$1[d] || ListenerMethods$1[d])) {
            throw new Error("Cannot override API method " + d + " in store creation. Use another method name or override it on Reflux.PublisherMethods / Reflux.ListenerMethods instead.");
        }
    }

    definition = (0, mixer.mix)(definition);

    function Store() {
        var i = 0,
            arr;
        this.subscriptions = [];
        this.emitter = new _.EventEmitter();
        this.eventLabel = "change";
        (0, bindMethods_1.bindMethods)(this, definition);
        if (this.init && _.isFunction(this.init)) {
            this.init();
        }
        if (this.listenables) {
            arr = [].concat(this.listenables);
            for (; i < arr.length; i++) {
                this.listenToMany(arr[i]);
            }
        }
    }

    _.extend(Store.prototype, ListenerMethods$1, PublisherMethods$1, StoreMethods$1, definition);

    var store = new Store();
    Keep$1.addStore(store);

    return store;
}
});

unwrapExports(createStore_1);
var createStore_2 = createStore_1.createStore;

var joins = createCommonjsModule(function (module, exports) {

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.staticJoinCreator = staticJoinCreator;
exports.instanceJoinCreator = instanceJoinCreator;





var _ = _interopRequireWildcard(utils);

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

/**
 * Internal module used to create static and instance join methods
 */

var slice = Array.prototype.slice,
    strategyMethodNames = {
    strict: "joinStrict",
    first: "joinLeading",
    last: "joinTrailing",
    all: "joinConcat"
};

/**
 * Used in `index.js` to create the static join methods
 * @param {String} strategy Which strategy to use when tracking listenable trigger arguments
 * @returns {Function} A static function which returns a store with a join listen on the given listenables using the given strategy
 */
function staticJoinCreator(strategy) {
    return function () /* listenables... */{
        var listenables = slice.call(arguments);
        return (0, createStore_1.createStore)({
            init: function init() {
                this[strategyMethodNames[strategy]].apply(this, listenables.concat("triggerAsync"));
            }
        });
    };
}

/**
 * Used in `ListenerMethods.js` to create the instance join methods
 * @param {String} strategy Which strategy to use when tracking listenable trigger arguments
 * @returns {Function} An instance method which sets up a join listen on the given listenables using the given strategy
 */
function instanceJoinCreator(strategy) {
    return function () /* listenables..., callback*/{
        _.throwIf(arguments.length < 2, "Cannot create a join with less than 2 listenables!");
        var listenables = slice.call(arguments),
            callback = listenables.pop(),
            numberOfListenables = listenables.length,
            join = {
            numberOfListenables: numberOfListenables,
            callback: this[callback] || callback,
            listener: this,
            strategy: strategy
        },
            i,
            cancels = [],
            subobj;
        for (i = 0; i < numberOfListenables; i++) {
            _.throwIf(this.validateListening(listenables[i]));
        }
        for (i = 0; i < numberOfListenables; i++) {
            cancels.push(listenables[i].listen(newListener(i, join), this));
        }
        reset(join);
        subobj = { listenable: listenables };
        subobj.stop = makeStopper(subobj, cancels, this);
        this.subscriptions = (this.subscriptions || []).concat(subobj);
        return subobj;
    };
}

// ---- internal join functions ----

function makeStopper(subobj, cancels, context) {
    return function () {
        var i,
            subs = context.subscriptions,
            index = subs ? subs.indexOf(subobj) : -1;
        _.throwIf(index === -1, "Tried to remove join already gone from subscriptions list!");
        for (i = 0; i < cancels.length; i++) {
            cancels[i]();
        }
        subs.splice(index, 1);
    };
}

function reset(join) {
    join.listenablesEmitted = new Array(join.numberOfListenables);
    join.args = new Array(join.numberOfListenables);
}

function newListener(i, join) {
    return function () {
        var callargs = slice.call(arguments);
        if (join.listenablesEmitted[i]) {
            switch (join.strategy) {
                case "strict":
                    throw new Error("Strict join failed because listener triggered twice.");
                case "last":
                    join.args[i] = callargs;break;
                case "all":
                    join.args[i].push(callargs);
            }
        } else {
            join.listenablesEmitted[i] = true;
            join.args[i] = join.strategy === "all" ? [callargs] : callargs;
        }
        emitIfAllListenablesEmitted(join);
    };
}

function emitIfAllListenablesEmitted(join) {
    for (var i = 0; i < join.numberOfListenables; i++) {
        if (!join.listenablesEmitted[i]) {
            return;
        }
    }
    join.callback.apply(join.listener, join.args);
    reset(join);
}
});

unwrapExports(joins);
var joins_1 = joins.staticJoinCreator;
var joins_2 = joins.instanceJoinCreator;

var ListenerMethods = createCommonjsModule(function (module, exports) {

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.joinStrict = exports.joinConcat = exports.joinLeading = exports.joinTrailing = exports.fetchInitialState = exports.stopListeningToAll = exports.stopListeningTo = exports.listenTo = exports.validateListening = exports.listenToMany = exports.hasListener = undefined;



var _ = _interopRequireWildcard(utils);



function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

/**
 * Extract child listenables from a parent from their
 * children property and return them in a keyed Object
 *
 * @param {Object} listenable The parent listenable
 */
var mapChildListenables = function mapChildListenables(listenable) {
    var i = 0,
        children = {},
        childName;
    for (; i < (listenable.children || []).length; ++i) {
        childName = listenable.children[i];
        if (listenable[childName]) {
            children[childName] = listenable[childName];
        }
    }
    return children;
};

/**
 * Make a flat dictionary of all listenables including their
 * possible children (recursively), concatenating names in camelCase.
 *
 * @param {Object} listenables The top-level listenables
 */
var flattenListenables = function flattenListenables(listenables) {
    var flattened = {};
    for (var key in listenables) {
        var listenable = listenables[key];
        var childMap = mapChildListenables(listenable);

        // recursively flatten children
        var children = flattenListenables(childMap);

        // add the primary listenable and chilren
        flattened[key] = listenable;
        for (var childKey in children) {
            var childListenable = children[childKey];
            flattened[key + _.capitalize(childKey)] = childListenable;
        }
    }

    return flattened;
};

/**
 * An internal utility function used by `validateListening`
 *
 * @param {Action|Store} listenable The listenable we want to search for
 * @returns {Boolean} The result of a recursive search among `this.subscriptions`
 */
var hasListener = exports.hasListener = function hasListener(listenable) {
    var i = 0,
        j,
        listener,
        listenables;
    for (; i < (this.subscriptions || []).length; ++i) {
        listenables = [].concat(this.subscriptions[i].listenable);
        for (j = 0; j < listenables.length; j++) {
            listener = listenables[j];
            if (listener === listenable || listener.hasListener && listener.hasListener(listenable)) {
                return true;
            }
        }
    }
    return false;
};

/**
 * A convenience method that listens to all listenables in the given object.
 *
 * @param {Object} listenables An object of listenables. Keys will be used as callback method names.
 */
var listenToMany = exports.listenToMany = function listenToMany(listenables) {
    var allListenables = flattenListenables(listenables);
    for (var key in allListenables) {
        var cbname = _.callbackName(key),
            localname = this[cbname] ? cbname : this[key] ? key : undefined;
        if (localname) {
            this.listenTo(allListenables[key], localname, this[cbname + "Default"] || this[localname + "Default"] || localname);
        }
    }
};

/**
 * Checks if the current context can listen to the supplied listenable
 *
 * @param {Action|Store} listenable An Action or Store that should be
 *  listened to.
 * @returns {String|Undefined} An error message, or undefined if there was no problem.
 */
var validateListening = exports.validateListening = function validateListening(listenable) {
    if (listenable === this) {
        return "Listener is not able to listen to itself";
    }
    if (!_.isFunction(listenable.listen)) {
        return listenable + " is missing a listen method";
    }
    if (listenable.hasListener && listenable.hasListener(this)) {
        return "Listener cannot listen to this listenable because of circular loop";
    }
};

/**
 * Sets up a subscription to the given listenable for the context object
 *
 * @param {Action|Store} listenable An Action or Store that should be
 *  listened to.
 * @param {Function|String} callback The callback to register as event handler
 * @param {Function|String} defaultCallback The callback to register as default handler
 * @returns {Object} A subscription obj where `stop` is an unsub function and `listenable` is the object being listened to
 */
var listenTo = exports.listenTo = function listenTo(listenable, callback, defaultCallback) {
    var desub,
        unsubscriber,
        subscriptionobj,
        subs = this.subscriptions = this.subscriptions || [];
    _.throwIf(this.validateListening(listenable));
    this.fetchInitialState(listenable, defaultCallback);
    desub = listenable.listen(this[callback] || callback, this);
    unsubscriber = function unsubscriber() {
        var index = subs.indexOf(subscriptionobj);
        _.throwIf(index === -1, "Tried to remove listen already gone from subscriptions list!");
        subs.splice(index, 1);
        desub();
    };
    subscriptionobj = {
        stop: unsubscriber,
        listenable: listenable
    };
    subs.push(subscriptionobj);
    return subscriptionobj;
};

/**
 * Stops listening to a single listenable
 *
 * @param {Action|Store} listenable The action or store we no longer want to listen to
 * @returns {Boolean} True if a subscription was found and removed, otherwise false.
 */
var stopListeningTo = exports.stopListeningTo = function stopListeningTo(listenable) {
    var sub,
        i = 0,
        subs = this.subscriptions || [];
    for (; i < subs.length; i++) {
        sub = subs[i];
        if (sub.listenable === listenable) {
            sub.stop();
            _.throwIf(subs.indexOf(sub) !== -1, "Failed to remove listen from subscriptions list!");
            return true;
        }
    }
    return false;
};

/**
 * Stops all subscriptions and empties subscriptions array
 */
var stopListeningToAll = exports.stopListeningToAll = function stopListeningToAll() {
    var remaining,
        subs = this.subscriptions || [];
    while (remaining = subs.length) {
        subs[0].stop();
        _.throwIf(subs.length !== remaining - 1, "Failed to remove listen from subscriptions list!");
    }
};

/**
 * Used in `listenTo`. Fetches initial data from a publisher if it has a `getInitialState` method.
 * @param {Action|Store} listenable The publisher we want to get initial state from
 * @param {Function|String} defaultCallback The method to receive the data
 */
var fetchInitialState = exports.fetchInitialState = function fetchInitialState(listenable, defaultCallback) {
    defaultCallback = defaultCallback && this[defaultCallback] || defaultCallback;
    var me = this;
    if (_.isFunction(defaultCallback) && _.isFunction(listenable.getInitialState)) {
        var data = listenable.getInitialState();
        if (data && _.isFunction(data.then)) {
            data.then(function () {
                defaultCallback.apply(me, arguments);
            });
        } else {
            defaultCallback.call(this, data);
        }
    }
};

/**
 * The callback will be called once all listenables have triggered at least once.
 * It will be invoked with the last emission from each listenable.
 * @param {...Publishers} publishers Publishers that should be tracked.
 * @param {Function|String} callback The method to call when all publishers have emitted
 * @returns {Object} A subscription obj where `stop` is an unsub function and `listenable` is an array of listenables
 */
var joinTrailing = exports.joinTrailing = (0, joins.instanceJoinCreator)("last");

/**
 * The callback will be called once all listenables have triggered at least once.
 * It will be invoked with the first emission from each listenable.
 * @param {...Publishers} publishers Publishers that should be tracked.
 * @param {Function|String} callback The method to call when all publishers have emitted
 * @returns {Object} A subscription obj where `stop` is an unsub function and `listenable` is an array of listenables
 */
var joinLeading = exports.joinLeading = (0, joins.instanceJoinCreator)("first");

/**
 * The callback will be called once all listenables have triggered at least once.
 * It will be invoked with all emission from each listenable.
 * @param {...Publishers} publishers Publishers that should be tracked.
 * @param {Function|String} callback The method to call when all publishers have emitted
 * @returns {Object} A subscription obj where `stop` is an unsub function and `listenable` is an array of listenables
 */
var joinConcat = exports.joinConcat = (0, joins.instanceJoinCreator)("all");

/**
 * The callback will be called once all listenables have triggered.
 * If a callback triggers twice before that happens, an error is thrown.
 * @param {...Publishers} publishers Publishers that should be tracked.
 * @param {Function|String} callback The method to call when all publishers have emitted
 * @returns {Object} A subscription obj where `stop` is an unsub function and `listenable` is an array of listenables
 */
var joinStrict = exports.joinStrict = (0, joins.instanceJoinCreator)("strict");
});

unwrapExports(ListenerMethods);
var ListenerMethods_1 = ListenerMethods.joinStrict;
var ListenerMethods_2 = ListenerMethods.joinConcat;
var ListenerMethods_3 = ListenerMethods.joinLeading;
var ListenerMethods_4 = ListenerMethods.joinTrailing;
var ListenerMethods_5 = ListenerMethods.fetchInitialState;
var ListenerMethods_6 = ListenerMethods.stopListeningToAll;
var ListenerMethods_7 = ListenerMethods.stopListeningTo;
var ListenerMethods_8 = ListenerMethods.listenTo;
var ListenerMethods_9 = ListenerMethods.validateListening;
var ListenerMethods_10 = ListenerMethods.listenToMany;
var ListenerMethods_11 = ListenerMethods.hasListener;

var createAction_1 = createCommonjsModule(function (module, exports) {

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.createAction = createAction;



var _ = _interopRequireWildcard(utils);



var ActionMethods$1 = _interopRequireWildcard(ActionMethods);



var PublisherMethods$1 = _interopRequireWildcard(PublisherMethods);



var Keep$1 = _interopRequireWildcard(Keep);

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

var allowed = { preEmit: 1, shouldEmit: 1 };

/**
 * Creates an action functor object. It is mixed in with functions
 * from the `PublisherMethods` mixin. `preEmit` and `shouldEmit` may
 * be overridden in the definition object.
 *
 * @param {Object} definition The action object definition
 */
function createAction(definition) {

    definition = definition || {};
    if (!_.isObject(definition)) {
        definition = { actionName: definition };
    }

    for (var a in ActionMethods$1) {
        if (!allowed[a] && PublisherMethods$1[a]) {
            throw new Error("Cannot override API method " + a + " in Reflux.ActionMethods. Use another method name or override it on Reflux.PublisherMethods instead.");
        }
    }

    for (var d in definition) {
        if (!allowed[d] && PublisherMethods$1[d]) {
            throw new Error("Cannot override API method " + d + " in action creation. Use another method name or override it on Reflux.PublisherMethods instead.");
        }
    }

    definition.children = definition.children || [];
    if (definition.asyncResult) {
        definition.children = definition.children.concat(["completed", "failed"]);
    }

    var i = 0,
        childActions = {};
    for (; i < definition.children.length; i++) {
        var chDef = definition.children[i];
        var chName = typeof chDef === "string" ? chDef : chDef.actionName;
        childActions[chName] = createAction(chDef);
    }

    var context = _.extend({
        eventLabel: "action",
        emitter: new _.EventEmitter(),
        _isAction: true
    }, PublisherMethods$1, ActionMethods$1, definition);

    var functor = function functor() {
        var hasChildActions = false;
        /* eslint no-unused-vars:0 */
        for (var ignore in functor.childActions) {
            hasChildActions = true;break;
        }
        var async = !functor.sync && typeof functor.sync !== "undefined" || hasChildActions;
        var triggerType = async ? "triggerAsync" : "trigger";
        return functor[triggerType].apply(functor, arguments);
    };

    _.extend(functor, childActions, context);

    Keep$1.addAction(functor);

    return functor;
}
});

unwrapExports(createAction_1);
var createAction_2 = createAction_1.createAction;

var lib = createCommonjsModule(function (module, exports) {

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.__keep = exports.joinConcat = exports.joinStrict = exports.joinLeading = exports.all = exports.joinTrailing = exports.use = exports.nextTick = exports.setEventEmitter = exports.createActions = exports.createStore = exports.createAction = exports.utils = exports.StoreMethods = exports.PublisherMethods = exports.ListenerMethods = exports.ActionMethods = exports.version = undefined;



var ActionMethods$1 = _interopRequireWildcard(ActionMethods);



var ListenerMethods$1 = _interopRequireWildcard(ListenerMethods);



var PublisherMethods$1 = _interopRequireWildcard(PublisherMethods);



var StoreMethods$1 = _interopRequireWildcard(StoreMethods);





var _ = _interopRequireWildcard(utils);







var __keep = _interopRequireWildcard(Keep);

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

var version = {
    "reflux-core": "1.0.0"
};

var joinTrailing = (0, joins.staticJoinCreator)("last");
var all = joinTrailing; // Reflux.all alias for backward compatibility
var joinLeading = (0, joins.staticJoinCreator)("first");
var joinStrict = (0, joins.staticJoinCreator)("strict");
var joinConcat = (0, joins.staticJoinCreator)("all");

var utils$1 = _;


/**
 * Convenience function for creating a set of actions
 *
 * @param definitions the definitions for the actions to be created
 * @returns an object with actions of corresponding action names
 */
var createActions = function () {
    var reducer = function reducer(definitions, actions) {
        Object.keys(definitions).forEach(function (actionName) {
            var val = definitions[actionName];
            actions[actionName] = (0, createAction_1.createAction)(val);
        });
    };

    return function (definitions) {
        var actions = {};
        if (definitions instanceof Array) {
            definitions.forEach(function (val) {
                if (_.isObject(val)) {
                    reducer(val, actions);
                } else {
                    actions[val] = (0, createAction_1.createAction)(val);
                }
            });
        } else {
            reducer(definitions, actions);
        }
        return actions;
    };
}();

/**
 * Sets the eventmitter that Reflux uses
 */
function setEventEmitter(ctx) {
    _.EventEmitter = ctx;
}

/**
 * Sets the method used for deferring actions and stores
 */
function nextTick(nextTick) {
    _.nextTick = nextTick;
}

function use(pluginCb) {
    pluginCb(this);
}

/**
 * Provides the set of created actions and stores for introspection
 */
/*eslint-disable no-underscore-dangle*/


// export in format that supports syntax: var Reflux = require('reflux-core');
exports.version = version;
exports.ActionMethods = ActionMethods$1;
exports.ListenerMethods = ListenerMethods$1;
exports.PublisherMethods = PublisherMethods$1;
exports.StoreMethods = StoreMethods$1;
exports.utils = utils$1;
exports.createAction = createAction_1.createAction;
exports.createStore = createStore_1.createStore;
exports.createActions = createActions;
exports.setEventEmitter = setEventEmitter;
exports.nextTick = nextTick;
exports.use = use;
exports.joinTrailing = joinTrailing;
exports.all = all;
exports.joinLeading = joinLeading;
exports.joinStrict = joinStrict;
exports.joinConcat = joinConcat;
exports.__keep = __keep;
/*eslint-enable no-underscore-dangle*/

// export in format that supports syntax: import Reflux from 'reflux-core';

Object.defineProperty(exports, "default", {
    get: function get() {
        return exports;
    }
});

/**
 * Warn if Function.prototype.bind not available
 */
if (!Function.prototype.bind) {
    console.error("Function.prototype.bind not available. " + "ES5 shim required. " + "https://github.com/spoike/refluxjs#es5");
}
});

unwrapExports(lib);
var lib_1 = lib.__keep;
var lib_2 = lib.joinConcat;
var lib_3 = lib.joinStrict;
var lib_4 = lib.joinLeading;
var lib_5 = lib.all;
var lib_6 = lib.joinTrailing;
var lib_7 = lib.use;
var lib_8 = lib.nextTick;
var lib_9 = lib.setEventEmitter;
var lib_10 = lib.createActions;
var lib_11 = lib.createStore;
var lib_12 = lib.createAction;
var lib_13 = lib.utils;
var lib_14 = lib.StoreMethods;
var lib_15 = lib.PublisherMethods;
var lib_16 = lib.ListenerMethods;
var lib_17 = lib.ActionMethods;
var lib_18 = lib.version;

/**
 * A module meant to be consumed as a mixin by a React component. Supplies the methods from
 * `ListenerMethods` mixin and takes care of teardown of subscriptions.
 * Note that if you're using the `connect` mixin you don't need this mixin, as connect will
 * import everything this mixin contains!
 */
var ListenerMixin = utils.extend({

    /**
     * Cleans up all listener previously registered.
     */
    componentWillUnmount: ListenerMethods.stopListeningToAll

}, ListenerMethods);

var connect = function(listenable, key) {

    utils.throwIf(typeof(key) === 'undefined', 'Reflux.connect() requires a key.');

    return {
        getInitialState: function() {
            if (!utils.isFunction(listenable.getInitialState)) {
                return {};
            }

            return utils.object([key],[listenable.getInitialState()]);
        },
        componentDidMount: function() {
            var me = this;

            utils.extend(me, ListenerMethods);

            this.listenTo(listenable, function(v) {
                me.setState(utils.object([key],[v]));
            });
        },
        componentWillUnmount: ListenerMixin.componentWillUnmount
    };
};

var connectFilter = function(listenable, key, filterFunc) {

    utils.throwIf(utils.isFunction(key), 'Reflux.connectFilter() requires a key.');

    return {
        getInitialState: function() {
            if (!utils.isFunction(listenable.getInitialState)) {
                return {};
            }

            // Filter initial payload from store.
            var result = filterFunc.call(this, listenable.getInitialState());
            if (typeof(result) !== 'undefined') {
                return utils.object([key], [result]);
            } else {
                return {};
            }
        },
        componentDidMount: function() {
            var me = this;

            utils.extend(this, ListenerMethods);

            this.listenTo(listenable, function(value) {
                var result = filterFunc.call(me, value);
                me.setState(utils.object([key], [result]));
            });
        },
        componentWillUnmount: ListenerMixin.componentWillUnmount
    };
};

/**
 * A mixin factory for a React component. Meant as a more convenient way of using the `ListenerMixin`,
 * without having to manually set listeners in the `componentDidMount` method.
 *
 * @param {Action|Store} listenable An Action or Store that should be
 *  listened to.
 * @param {Function|String} callback The callback to register as event handler
 * @param {Function|String} defaultCallback The callback to register as default handler
 * @returns {Object} An object to be used as a mixin, which sets up the listener for the given listenable.
 */
var listenTo = function(listenable,callback,initial){
    return {
        /**
         * Set up the mixin before the initial rendering occurs. Import methods from `ListenerMethods`
         * and then make the call to `listenTo` with the arguments provided to the factory function
         */
        componentDidMount: function() {
            for(var m in ListenerMethods){
                if (this[m] !== ListenerMethods[m]){
                    if (this[m]){
                        throw "Can't have other property '"+m+"' when using Reflux.listenTo!";
                    }
                    this[m] = ListenerMethods[m];
                }
            }
            this.listenTo(listenable,callback,initial);
        },
        /**
         * Cleans up all listener previously registered.
         */
        componentWillUnmount: ListenerMethods.stopListeningToAll
    };
};

/**
 * A mixin factory for a React component. Meant as a more convenient way of using the `listenerMixin`,
 * without having to manually set listeners in the `componentDidMount` method. This version is used
 * to automatically set up a `listenToMany` call.
 *
 * @param {Object} listenables An object of listenables
 * @returns {Object} An object to be used as a mixin, which sets up the listeners for the given listenables.
 */
var listenToMany = function(listenables){
    return {
        /**
         * Set up the mixin before the initial rendering occurs. Import methods from `ListenerMethods`
         * and then make the call to `listenTo` with the arguments provided to the factory function
         */
        componentDidMount: function() {
            for(var m in ListenerMethods){
                if (this[m] !== ListenerMethods[m]){
                    if (this[m]){
                        throw "Can't have other property '"+m+"' when using Reflux.listenToMany!";
                    }
                    this[m] = ListenerMethods[m];
                }
            }
            this.listenToMany(listenables);
        },
        /**
         * Cleans up all listener previously registered.
         */
        componentWillUnmount: ListenerMethods.stopListeningToAll
    };
};

/* globals React: false */



/**
 * Reflux.defineReact function where you can manually supply
 * the React object in order to create in case Reflux needs to load before
 * React or there is a modular environment where there won't be a global
 * React variable.
 * @note The third param is for internal usage only.
 */
var _react, _defined = false;
function defineReact(react, noLongerUsed, extend)
{
	var proto, _extend;
	
	// if no Reflux object is yet available then return and just wait until defineReact is called manually with it
	try {
		_react  = react  || _react  || React;
		_extend = extend || _react.Component;
	} catch (e) {
		return;
	}
	
	// if Reflux and React aren't present then ignore, wait until they are properly present
	// also ignore if it's been called before UNLESS there's manual extending happening
	if (!_react || !_extend || (_defined && !extend)) {
		return;
	}
	
	// ----------- BEGIN Reflux.Component ------------
	/**
	 * Reflux.Component:
	 * An implementation for idiomatic React.js classes that mix with
	 * Reflux stores. To utilize extend Reflux.Component instead of
	 * React.Component. Then you may hook any Reflux store that has a
	 * `this.state` property containing its state values to the component
	 * via `this.store` or an Array of Reflux stores via `this.stores` in
	 * the component's constructor (similar to how you assign initial state
	 * in the constructor in ES6 style React). The default values of the
	 * stores will automatically reflect in the component's state, and any
	 * further `trigger` calls from that store will update properties passed
	 * in the trigger into the component automatically.
	 */
	var RefluxComponent = function(props, context, updater) {
		_extend.call(this, props, context, updater);
	};
	
	// equivalent of `extends React.Component` or other class if provided via `extend` param
	lib.utils.inherits(RefluxComponent, _extend);
	
	proto = RefluxComponent.prototype;
	
	/**
	 * this.storeKeys
	 * When this is a falsey value (null by default) the component mixes in
	 * all properties from the stores attached to it and updates on changes
	 * from all of them. When set to an array of string keys it will only
	 * utilized state property names of those keys in any store attached. This
	 * lets you choose which parts of stores update the component on a component-
	 * by-component basis. If using this it is best set in the constructor.
	 */
	proto.storeKeys = null;
	
	// on the mounting of the component that is where the store/stores are attached and initialized if needed
	proto.componentWillMount = function () {
		// if there is a this.store then simply push it onto the this.stores array or make one if needed
		if (this.store) {
			if (Array.isArray(this.stores)) {
				this.stores.unshift(this.store);
			} else {
				this.stores = [this.store];
			}
		}
		
		if (this.stores) {
			this.__storeunsubscribes__ = this.__storeunsubscribes__ || [];
			var sS = this.setState.bind(this);
			// this handles the triggering of a store, checking what's updated if proto.storeKeys is utilized
			var onStoreTrigger = function(obj){
				var updateObj = filterByStoreKeys(this.storeKeys, obj);
				if (updateObj) {
					sS(updateObj);
				}
			}.bind(this);
			// for each store in this.stores...
			for (var i = 0, ii = this.stores.length; i < ii; i++) {
				var str = this.stores[i];
				// if's a function then we know it's a class getting passed, not an instance
				if (typeof str === 'function') {
					var storeId = str.id;
					// if there is NOT a .singleton property on the store then this store has not been initialized yet, so do so
					if (!str.singleton) {
						str.singleton = new str();
						if (storeId) {
							lib.stores[storeId] = str.singleton;
						}
					}
					// before we weren't sure if we were working with an instance or class, so now we know an instance is created set it
					// to the variables we were using so that we can just continue on knowing it's the instance we're working with
					this.stores[i] = str = str.singleton;
					// the instance should have an .id property as well if the class does, so set that here
					str.id = storeId;
					// if there is an id and there is a global state property for this store then merge
					// the properties from that global state into the default state of the store AND then
					// set the global state to that new state (since it may have previously been partial)
					if (storeId && lib.GlobalState[storeId]) {
						for (var key in lib.GlobalState[storeId]) {
							str.state[key] = lib.GlobalState[storeId][key];
						}
						lib.GlobalState[storeId] = str.state;
					// otherwise (if it has an id) set the global state to the default state of the store
					} else if (storeId) {
						lib.GlobalState[storeId] = str.state;
					}
					// if no id, then no messing with global state
				}
				// listen/subscribe for the ".trigger()" in the store, and track the unsubscribes so that we can unsubscribe on unmount
				if (!lib.serverMode) {
					this.__storeunsubscribes__.push(str.listen(onStoreTrigger));
				}
				// run set state so that it mixes in the props from the store with the component
				var updateObj = filterByStoreKeys(this.storeKeys, str.state);
				if (updateObj) {
					this.setState(updateObj);
				}
			}
		}
		
		// mapStoreToState needs to know if is ready to map or must wait
		this.__readytomap__ = true;
		// if there are mappings that were delayed, do them now
		var dmaps = this.__delayedmaps__;
		if (dmaps) {
			for (var j=0,jj=dmaps.length; j<jj; j++) {
				dmaps[j].func( dmaps[j].state );
			}
		}
		this.__delayedmaps__ = null;
	};
	
	// on the unmount phase of the component unsubscribe that which we subscribed earlier to keep our garbage trail clean
	proto.componentWillUnmount = function () {
		if (this.__storeunsubscribes__) {
			for (var i = 0, ii = this.__storeunsubscribes__.length; i < ii; i++) {
				this.__storeunsubscribes__[i]();
			}
		}
		this.__readytomap__ = false;
	};
	
	/**
	 * this.mapStoreToState
	 * This function allow you to supply map the state of a store to the
	 * state of this component manually via your own logic. This method
	 * is completely separate from this.store/this.stores and/or this.storeKeys.
	 * Call this function with an ES6 store (class or singleton instance) as the
	 * first argument and your filter function as the second. Your filter function
	 * will receive an object of the parts of the ES6 store being updated every
	 * time its setState is called. Your filter function then returns an object
	 * which will be merged with the component state (IF it has any properties at all,
	 * should you return a blank object the component will not rerender).
	 */
	proto.mapStoreToState = function(store, filterFunc)
	{
		// make sure we have a proper singleton instance to work with
		if (typeof store === 'function') {
			if (store.singleton) {
				store = store.singleton;
			} else {
				store = lib.initStore(store);
			}
		}
		
		// we need a closure so that the called function can remember the proper filter function to use, so function gets defined here
		var self = this;
		function onMapStoreTrigger(obj) {
			// get an object 
			var update = filterFunc.call(self, obj);
			// if no object returned from filter functions do nothing
			if (!update) {
				return;
			}
			// check if the update actually has any mapped props
			/*jshint unused: false */
			var hasProps = false;
			for (var check in update) {
				hasProps = true;
				break;
			}
			// if there were props mapped, then update via setState
			if (hasProps) {
				self.setState(update);
			}
		}
		
		// add the listener to know when the store is triggered
		this.__storeunsubscribes__ = this.__storeunsubscribes__ || [];
		this.__storeunsubscribes__.push(store.listen(onMapStoreTrigger));
		
		// now actually run onMapStoreTrigger with the full store state so that we immediately have all store state mapped to component state
		if (this.__readytomap__) {
			onMapStoreTrigger(store.state);
		} else {
			this.__delayedmaps__ = this.__delayedmaps__ || [];
			this.__delayedmaps__.push({func:onMapStoreTrigger, state:store.state});
		}
	};
	
	/**
	 * Reflux.Component.extend(OtherClass)
	 * This allows you to get classes that extend off of another React.Component
	 * inheriting class. For example if you're using a third party that uses
	 * components that allow `class MyComponent extends LibComponent` (where LibComponent
	 * itself extends React.Component) and you want to use that component with ES6 then
	 * you can make a class `var MyDualComponent = Reflux.Component.extend(LibComponent);`
	 * then you can use `class MyComponent extends MyDualComponent` to get the benefits
	 * of both libraries.
	 */
	RefluxComponent.extend = function(clss) {
		return defineReact(null, null, clss);
	};
	
	// if is being manually called with an `extend` argument present then just return the created class
	if (extend) {
		return RefluxComponent;
	}
	
	// otherwise set as Reflux.Component and continue with other normal definitions
	lib.Component = RefluxComponent;
	
	// also set Reflux.PureComponent (if it exists) using the .extend feature
	if (_react.PureComponent) {
		lib.PureComponent = RefluxComponent.extend(_react.PureComponent);
	}
	
	// ------------ END Reflux.Component ------------
	
	// --------- BEGIN Reflux.Store ------------
	/**
	 * Reflux.Store:
	 * Also implements optional Reflux.Store class that is idiomatic with
	 * the React ES6 style. You extend Reflux.Store and then the rest works
	 * the same as createStore, except the constructor instead of init, and
	 * it holds state in a state property, and a .setState method is available
	 * which automatically updates state and does a trigger. Then when using
	 * with this.store or this.stores in an ES6 component just plass the class,
	 * it will deal with a singleton instantiation of the class automatically.
	 */
	var RefluxStore = function() {
		// extending doesn't really work well here, so instead we create an internal instance
		// and just loop through its properties/methods and make a getter/setter for each
		// that will actually be getting and setting on that internal instance.
		this.__store__ = lib.createStore();
		this.state = {};
		var self = this;
		for (var key in this.__store__) {
			/*jshint loopfunc: true */
			(function (prop) {
				Object.defineProperty(self, prop, {
					get: function () { return self.__store__[prop]; },
					set: function (v) { self.__store__[prop] = v; }
				});
			})(key);
		}
	};
	
	proto = RefluxStore.prototype;
	
	// this defines the listenables property, mostly intended to be set as `this.listenables` in the constructor of the store
	// it is essentially a shortcut to the `listenToMany` method
	Object.defineProperty(proto, "listenables", {
		get: function () {
			return this.__listenables__;
		},
		set: function (v) {
			var Combined = {};
			if (Array.isArray(v)){
				v.forEach(function(obj) {
					for (var key in obj) {
						Combined[key] = obj[key];
					}
				});
			} else {
				Combined = v;
			}
			this.__listenables__ = Combined;
			this.listenToMany(Combined);
		},
		enumerable: true,
		configurable: true
	});
	
	// allows simple usage of `this.setState(obj)` within the store to both update the state and trigger the store to update
	// components that it is attached to in a simple way that is idiomatic with React
	proto.setState = function (obj) {
		// Object.assign(this.state, obj); // later turn this to Object.assign and remove loop once support is good enough
		for (var key in obj) {
			this.state[key] = obj[key];
		}
		// if there's an id (i.e. it's being tracked by the global state) then make sure to update the global state
		if (this.id) {
			lib.GlobalState[this.id] = this.state;
		}
		// trigger, because any component it's attached to is listening and will merge the store state into its own on a store trigger
		this.trigger(obj);
	};
	
	// this is a static property so that other code can identify that this is a Reflux.Store class
	// has issues specifically when using babel to transpile your ES6 stores for IE10 and below, not documented and shouldn't use yet
	Object.defineProperty(RefluxStore, "isES6Store", {
		get: function () {
			return true;
		},
		enumerable: true,
		configurable: true
	});
	
	// allows a shortcut for accessing MyStore.singleton.state as MyStore.state (since common usage makes a singleton)
	Object.defineProperty(RefluxStore, "state", {
		get: function () {
			if (!this.singleton) {
				throw new Error('Reflux.Store.state is inaccessible before the store has been initialized.');
			}
			return this.singleton.state;
		},
		enumerable: true,
		configurable: true
	});
	
	/* NOTE:
	If a Reflux.Store definition is given a static id property and used
	properly within a Reflux.Component or with Reflux.initStore then
	it will be added to the Reflux.GlobalState object which automatically tracks the
	current state of all such defined stores in the program. */
	
	lib.Store = RefluxStore;
	// ----------- END Reflux.Store -------------
	
	// --------- BEGIN Reflux Static Props/Methods ------------
	/**
	 * Reflux.GlobalState is where data is stored for any Reflux.Store that has a static id property. Each store's
	 * state will be on the Reflux.GlobalState object with the id as the key. So a store with the id "MyStore" and
	 * a state {"color":"red"} will end up with a Reflux.GlobalState of {"MyStore":{"color":"red"}}
	 * Reflux.GlobalState is an accessible part of the API. However, keep in mind that non-primitive properties you
	 * read off of it will continue to mutate and you can only manually mutate Reflux.GlobalState BEFORE any component
	 * mounting of components with ES6 stores. For more functionality look to Reflux.setGlobalState to change the global
	 * state at any point, and Reflux.getGlobalState to return a deep clone of the Reflux.GlobalState object which will
	 * not continue to mutate as Reflux.GlobalState continues to mutate.
	 */
	lib.GlobalState = lib.GlobalState || {};
	
	/**
	 * Reflux.stores
	 * All initialized stores that have an id will have a reference to their singleton stored here with the key being the id.
	 */
	lib.stores = {};
	
	/**
	 * Reflux.getGlobalState takes no arguments, and returns a deep clone of Reflux.GlobalState 
	 * which will not continue to mutate as Reflux.GlobalState does. It can essentially store
	 * snapshots of the global state as the program goes for saving or for in-app time travel.
	 */
	lib.getGlobalState = function() {
		return clone(lib.GlobalState);
	};
	
	/**
	 * Reflux.setGlobalState takes one argument that is a representation of the a possible
	 * global state. It updates all stores in the program to represent data in that given state.
	 * This includes triggering those stores so that that state is represented in any Reflux.Component
	 * instances they are attached to. Partial states may be given to it, and only the represented
	 * stores/state values will be updated.
	 */
	lib.setGlobalState = function(obj) {
		for (var storeID in obj) {
			if (lib.stores[storeID]) {
				lib.stores[storeID].setState(obj[storeID]);
			} else {
				lib.GlobalState[storeID] = obj[storeID];
			}
		}
	};
	
	/**
	 * Reflux.initStore takes one argument (a class that extends Reflux.Store) and returns a singleton
	 * intance of that class. Its main functionality is to be able to mimic what happens to stores attached to
	 * this.store or this.stores during the mounting phase of a component without having to actually attach the
	 * store to a component in order to work properly with the global state.
	 */
	// Reflux.initializeGlobalStore is kept for backwards compatibility, but deprecated since the function is
	// now for more broad instantiation of globally stored AND non-globally stored classes
	lib.initializeGlobalStore = lib.initStore = function(str) {
		var storeId = str.id;
		// if they're initializing something twice then we're done already, return it
		if (str.singleton) {
			return str.singleton;
		}
		// if no id then it's easy: just make new instance and set to singleton
		if (!storeId) {
			str.singleton = new str();
			return str.singleton;
		}
		// create the singleton and assign it to the class's singleton static property
		var inst = str.singleton = new str();
		// store it on the Reflux.stores array to be accessible later
		lib.stores[storeId] = inst;
		// the singleton instance itself should also have the id property of the class
		inst.id = storeId;
		// if the global state has something set for this id, copy it to the state and then
		// make sure to set the global state to the end result, since it may have only been partial
		if (lib.GlobalState[storeId]) {
			for (var key in lib.GlobalState[storeId]) {
				inst.state[key] = lib.GlobalState[storeId][key];
			}
			lib.GlobalState[storeId] = inst.state;
		// otherwise just set the global state to the default state of the class
		} else {
			lib.GlobalState[storeId] = inst.state;
		}
		// returns the singleton itself, though it will also be accessible as as `MyClass.singleton`
		return inst;
	};
	// --------- END Reflux Static Props/Methods ------------
	
	// so it knows not to redefine Reflux static stuff and stores if called again
	_defined = true;
}

// filters a state object by storeKeys array (if it exists)
// if filtering and obj contains no properties to use, returns false to let the component know not to update
function filterByStoreKeys(storeKeys, obj)
{
	// if there are not storeKeys defined then simply return the whole original object
	if (!storeKeys) {
		return obj;
	}
	// otherwise go through and only update properties that are in the storeKeys array, and return straight false if there are none
	var doUpdate = false;
	var updateObj = {};
	for (var i = 0, ii = storeKeys.length; i < ii; i++) {
		var prop = storeKeys[i];
		if (obj.hasOwnProperty(prop)) {
			doUpdate = true;
			updateObj[prop] = obj[prop];
		}
	}
	return doUpdate ? updateObj : false;
}

// this is utilized by some of the global state functionality in order to get a clone that will
// not continue to be modified as the GlobalState mutates
function clone(frm, to) {
	if (frm === null || typeof frm !== "object") {
		return frm;
	}
	if (frm.constructor !== Object && frm.constructor !== Array) {
		return frm;
	}
	if (frm.constructor === Date || frm.constructor === RegExp || frm.constructor === Function ||
		frm.constructor === String || frm.constructor === Number || frm.constructor === Boolean) {
		return new frm.constructor(frm);
	}
	to = to || new frm.constructor();
	for (var name in frm) {
		to[name] = typeof to[name] === "undefined" ? clone(frm[name], null) : to[name];
	}
	return to;
}

var defineReact_1 = defineReact;

/* globals React: false */


lib.defineReact = defineReact_1;

// useful utility for ES6 work, mimics the ability to extend
lib.utils.inherits = function(subClass, superClass) {
	if (typeof superClass !== "function" && superClass !== null) {
		throw new TypeError("Super expression must either be null or a function, not " + typeof superClass);
	}
	subClass.prototype = Object.create(superClass && superClass.prototype, {
		constructor: {
			value: subClass,
			enumerable: false,
			writable: true,
			configurable: true
		}
	});
	if (superClass) {
		if (Object.setPrototypeOf) {
			Object.setPrototypeOf(subClass, superClass);
		} else {
			/* jshint proto: true */
			subClass.__proto__ = superClass;
		}
	}
};

// first try to see if there's a global React var and use it
if (typeof React !== 'undefined' && React) {
	lib.defineReact(React);
// otherwise we're gonna resort to 'try' stuff in case of other environments
} else {
	try {
		var R = react; // we ignore this in browserify manually (see grunt file), so it's more of a doublecheck for in node
		lib.defineReact(R);
	} catch (e) {}
}

lib.serverMode = typeof window !== 'object';

lib.connect = connect;

lib.connectFilter = connectFilter;

lib.ListenerMixin = ListenerMixin;

lib.listenTo = listenTo;

lib.listenToMany = listenToMany;



var src = lib;

export default src;
