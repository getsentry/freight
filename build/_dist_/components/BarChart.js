function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

import moment from '/web_modules/moment.js';
import PropTypes from '/web_modules/prop-types.js';
import React from '/web_modules/react.js';
import TooltipTrigger from './TooltipTrigger.js';

class BarChart extends React.Component {
  constructor(...args) {
    super(...args);

    _defineProperty(this, "floatFormat", (number, places) => {
      const multi = Math.pow(10, places);
      return parseInt(number * multi, 10) / multi;
    });

    _defineProperty(this, "timeLabelAsHour", point => {
      const timeMoment = moment(point.x * 1000);
      const nextMoment = timeMoment.clone().add(59, 'minute');
      return /*#__PURE__*/React.createElement("span", null, timeMoment.format('LL'), /*#__PURE__*/React.createElement("br", null), timeMoment.format('LT'), " \u2014\u203A ", nextMoment.format('LT'));
    });

    _defineProperty(this, "timeLabelAsDay", point => {
      const timeMoment = moment(point.x * 1000);
      return /*#__PURE__*/React.createElement("span", null, timeMoment.format('LL'));
    });

    _defineProperty(this, "timeLabelAsRange", (interval, point) => {
      const timeMoment = moment(point.x * 1000);
      const nextMoment = timeMoment.clone().add(interval - 1, 'second');
      return /*#__PURE__*/React.createElement("span", null, timeMoment.format('lll'), /*#__PURE__*/React.createElement("br", null), "\u2014\u203A ", nextMoment.format('lll'));
    });

    _defineProperty(this, "timeLabelAsFull", point => {
      const timeMoment = moment(point.x * 1000);
      return timeMoment.format('lll');
    });
  }

  render() {
    const points = this.props.points;
    let maxval = 10;
    points.forEach(function (point) {
      if (point.y > maxval) {
        maxval = point.y;
      }
    });
    const pointWidth = this.floatFormat(100.0 / points.length, 2) + '%';
    const interval = points.length > 1 ? points[1].x - points[0].x : null;
    let timeLabelFunc;

    switch (interval) {
      case 3600:
        timeLabelFunc = this.timeLabelAsHour;
        break;

      case 86400:
        timeLabelFunc = this.timeLabelAsDay;
        break;

      case null:
        timeLabelFunc = this.timeLabelAsFull;
        break;

      default:
        timeLabelFunc = this.timeLabelAsRange.bind(this, interval);
    }

    const children = points.map((point, pointIdx) => {
      const pct = this.floatFormat(point.y / maxval * 99, 2) + '%';
      const timeLabel = timeLabelFunc(point);
      let title = /*#__PURE__*/React.createElement("div", {
        style: {
          minWidth: 100
        }
      }, point.y, " ", this.props.label, /*#__PURE__*/React.createElement("br", null), timeLabel);

      if (point.label) {
        title += /*#__PURE__*/React.createElement("div", null, "(", point.label, ")");
      }

      return /*#__PURE__*/React.createElement(TooltipTrigger, {
        placement: this.props.placement,
        key: point.x,
        title: title
      }, /*#__PURE__*/React.createElement("a", {
        style: {
          width: pointWidth
        }
      }, /*#__PURE__*/React.createElement("span", {
        style: {
          height: pct
        }
      }, point.y)));
    });
    return /*#__PURE__*/React.createElement("figure", {
      className: this.props.className || '' + ' barchart',
      height: this.props.height,
      width: this.props.width
    }, /*#__PURE__*/React.createElement("span", {
      className: "max-y",
      key: "max-y"
    }, maxval), /*#__PURE__*/React.createElement("span", {
      className: "min-y",
      key: "min-y"
    }, 0), children);
  }

}

_defineProperty(BarChart, "propTypes", {
  height: PropTypes.string,
  width: PropTypes.string,
  points: PropTypes.arrayOf(PropTypes.shape({
    x: PropTypes.number.isRequired,
    y: PropTypes.number.isRequired,
    label: PropTypes.string
  })),
  placement: PropTypes.string,
  label: PropTypes.string
});

_defineProperty(BarChart, "defaultProps", {
  placement: 'bottom',
  points: [],
  label: ''
});

export default BarChart;