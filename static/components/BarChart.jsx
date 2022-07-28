import * as React from 'react';
import {addMinutes, addSeconds, format} from 'date-fns';
import PropTypes from 'prop-types';

function floatFormat(number, places) {
  const multi = Math.pow(10, places);
  return parseInt(number * multi, 10) / multi;
}

function timeLabelAsHour(point) {
  const date = new Date(point.x * 1000);
  const nextDate = addMinutes(date, 59);

  return (
    <span>
      {format(date, 'PPP')}
      <br />
      {format(date, 'p')} &mdash;&rsaquo; {format(nextDate, 'p')}
    </span>
  );
}

function timeLabelAsDay(point) {
  const date = new Date(point.x * 1000);
  return <span>{format(date, 'PPP')}</span>;
}

function timeLabelAsFull(point) {
  const date = new Date(point.x * 1000);
  return format(date, 'PPp');
}

function timeLabelAsRange(interval, point) {
  const date = new Date(point.x * 1000);
  const nextDate = addSeconds(date, interval - 1);

  return (
    <span>
      {format(date, 'PPp')}
      <br />
      &mdash;&rsaquo; {format(nextDate, 'PPp')}
    </span>
  );
}

function BarChart({className, height, width, label = '', points = []}) {
  let maxval = 10;
  points.forEach(function (point) {
    if (point.y > maxval) {
      maxval = point.y;
    }
  });

  const pointWidth = floatFormat(100.0 / points.length, 2) + '%';
  const interval = points.length > 1 ? points[1].x - points[0].x : null;

  let timeLabelFunc;
  switch (interval) {
    case 3600:
      timeLabelFunc = timeLabelAsHour;
      break;
    case 86400:
      timeLabelFunc = timeLabelAsDay;
      break;
    case null:
      timeLabelFunc = timeLabelAsFull;
      break;
    default:
      timeLabelFunc = p => timeLabelAsRange(interval, p);
  }

  const children = points.map(point => {
    const pct = floatFormat((point.y / maxval) * 99, 2) + '%';
    const timeLabel = timeLabelFunc(point);

    const tooltipText = (
      <div style={{minWidth: 100}}>
        {point.y} {label}
        <br />
        {timeLabel}
      </div>
    );

    return (
      <div key={point.x} className="barchart-bar" style={{width: pointWidth}}>
        <span style={{height: pct}}>{point.y}</span>
        <div className="barchart-tooltip">{tooltipText}</div>
      </div>
    );
  });

  return (
    <figure className={className || '' + ' barchart'} height={height} width={width}>
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

BarChart.propTypes = {
  height: PropTypes.string,
  width: PropTypes.string,
  points: PropTypes.arrayOf(
    PropTypes.shape({
      x: PropTypes.number.isRequired,
      y: PropTypes.number.isRequired,
    })
  ),
};

export default BarChart;
