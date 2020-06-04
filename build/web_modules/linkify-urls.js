import { c as createCommonjsModule, g as getCjsExportFromNamespace } from './common/_commonjsHelpers-a1c50d10.js';

var escapeGoat = createCommonjsModule(function (module, exports) {

exports.escape = input => input
	.replace(/&/g, '&amp;')
	.replace(/"/g, '&quot;')
	.replace(/'/g, '&#39;')
	.replace(/</g, '&lt;')
	.replace(/>/g, '&gt;');

exports.unescape = input => input
	.replace(/&gt;/g, '>')
	.replace(/&lt;/g, '<')
	.replace(/&#39;/g, '\'')
	.replace(/&quot;/g, '"')
	.replace(/&amp;/g, '&');

exports.escapeTag = function (input) {
	let output = input[0];
	for (let i = 1; i < arguments.length; i++) {
		output = output + exports.escape(arguments[i]) + input[i];
	}
	return output;
};

exports.unescapeTag = function (input) {
	let output = input[0];
	for (let i = 1; i < arguments.length; i++) {
		output = output + exports.unescape(arguments[i]) + input[i];
	}
	return output;
};
});
var escapeGoat_1 = escapeGoat.escape;
var escapeGoat_2 = escapeGoat.unescape;
var escapeGoat_3 = escapeGoat.escapeTag;
var escapeGoat_4 = escapeGoat.unescapeTag;

var stringifyAttributes = input => {
	const attributes = [];

	for (const key of Object.keys(input)) {
		let value = input[key];

		if (value === false) {
			continue;
		}

		if (Array.isArray(value)) {
			value = value.join(' ');
		}

		let attribute = escapeGoat.escape(key);

		if (value !== true) {
			attribute += `="${escapeGoat.escape(String(value))}"`;
		}

		attributes.push(attribute);
	}

	return attributes.length > 0 ? ' ' + attributes.join(' ') : '';
};

var htmlTagsVoid = [
  "area",
  "base",
  "br",
  "col",
  "embed",
  "hr",
  "img",
  "input",
  "link",
  "menuitem",
  "meta",
  "param",
  "source",
  "track",
  "wbr"
];

var htmlTagsVoid$1 = /*#__PURE__*/Object.freeze({
	__proto__: null,
	'default': htmlTagsVoid
});

var require$$0 = getCjsExportFromNamespace(htmlTagsVoid$1);

var _void = require$$0;

const voidHtmlTags = new Set(_void);

var createHtmlElement = options => {
	options = Object.assign({
		name: 'div',
		attributes: {},
		html: ''
	}, options);

	if (options.html && options.text) {
		throw new Error('The `html` and `text` options are mutually exclusive');
	}

	const content = options.text ? escapeGoat.escape(options.text) : options.html;
	let result = `<${options.name}${stringifyAttributes(options.attributes)}>`;

	if (!voidHtmlTags.has(options.name)) {
		result += `${content}</${options.name}>`;
	}

	return result;
};

// Capture the whole URL in group 1 to keep string.split() support
const urlRegex = () => (/((?:https?(?::\/\/))(?:www\.)?(?:[a-zA-Z\d-_.]+(?:(?:\.|@)[a-zA-Z\d]{2,})|localhost)(?:(?:[-a-zA-Z\d:%_+.~#!?&//=@]*)(?:[,](?![\s]))*)*)/g);

// Get <a> element as string
const linkify = (href, options) => createHtmlElement({
	name: 'a',
	attributes: Object.assign({href: ''}, options.attributes, {href}),
	text: typeof options.value === 'undefined' ? href : undefined,
	html: typeof options.value === 'undefined' ? undefined :
		(typeof options.value === 'function' ? options.value(href) : options.value)
});

// Get DOM node from HTML
const domify = html => document.createRange().createContextualFragment(html);

const getAsString = (input, options) => {
	return input.replace(urlRegex(), match => linkify(match, options));
};

const getAsDocumentFragment = (input, options) => {
	return input.split(urlRegex()).reduce((frag, text, index) => {
		if (index % 2) { // URLs are always in odd positions
			frag.appendChild(domify(linkify(text, options)));
		} else if (text.length > 0) {
			frag.appendChild(document.createTextNode(text));
		}

		return frag;
	}, document.createDocumentFragment());
};

var linkifyUrls = (input, options) => {
	options = Object.assign({
		attributes: {},
		type: 'string'
	}, options);

	if (options.type === 'string') {
		return getAsString(input, options);
	}

	if (options.type === 'dom') {
		return getAsDocumentFragment(input, options);
	}

	throw new Error('The type option must be either `dom` or `string`');
};

export default linkifyUrls;
