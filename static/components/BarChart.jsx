import {format, addMinutes, addSeconds} from 'date-fns';
import PropTypes from 'prop-types';
import React from 'react';

import TooltipTrigger from './TooltipTrigger';

class BarChart extends React.Component {
  static propTypes = {
    height: PropTypes.string,
    width: PropTypes.string,
    points: PropTypes.arrayOf(
      PropTypes.shape({
        x: PropTypes.number.isRequired,
        y: PropTypes.number.isRequired,
        label: PropTypes.string,
      })
    ),
    placement: PropTypes.string,
    label: PropTypes.string,
  };

  static defaultProps = {
    placement: 'bottom',
    points: [],
    label: '',
  };

  floatFormat = (number, places) => {
    const multi = Math.pow(10, places);
    return parseInt(number * multi, 10) / multi;
  };

  timeLabelAsHour = point => {
    const date = new Date(point.x * 1000);
    const nextDate = addMinutes(date, 59);

    return (
      <span>
        {format(date, 'PPP')}
        <br />
        {format(date, 'p')} &mdash;&rsaquo; {format(nextDate, 'p')}
      </span>
    );
  };

  timeLabelAsDay = point => {
    const date = new Date(point.x * 1000);
    return <span>{format(date, 'PPP')}</span>;
  };

  timeLabelAsRange = (interval, point) => {
    const date = new Date(point.x * 1000);
    const nextDate = addSeconds(date, interval - 1);

    return (
      <span>
        {format(date, 'PPp')}
        <br />
        &mdash;&rsaquo; {format(nextDate, 'PPp')}
      </span>
    );
  };

  timeLabelAsFull = point => {
    const date = new Date(point.x * 1000);
    return format(date, 'PPp');
  };

  render() {
    const points = this.props.points;
    let maxval = 10;
    points.forEach(function(point) {
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
      const pct = this.floatFormat((point.y / maxval) * 99, 2) + '%';
      const timeLabel = timeLabelFunc(point);

      let title = (
        <div style={{minWidth: 100}}>
          {point.y} {this.props.label}
          <br />
          {timeLabel}
        </div>
      );
      if (point.label) {
        title += <div>({point.label})</div>;
      }

      return (
        <TooltipTrigger placement={this.props.placement} key={point.x} title={title}>
          <a style={{width: pointWidth}}>
            <span style={{height: pct}}>{point.y}</span>
          </a>
        </TooltipTrigger>
      );
    });

    return (
      <figure
        className={this.props.className || '' + ' barchart'}
        height={this.props.height}
        width={this.props.width}
      >
        <span className="max-y" key="max-y">
          {maxval}
        </span>
        <span className="min-y" key="min-y">
          {0}
        </span>
        {children}
      </figure>
    );
  }
}

export default BarChart;
