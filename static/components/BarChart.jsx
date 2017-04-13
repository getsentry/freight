const moment = require("moment");
const React = require("react");

const TooltipTrigger = require("./TooltipTrigger");

const BarChart = React.createClass({
  propTypes: {
    points: React.PropTypes.arrayOf(React.PropTypes.shape({
      x: React.PropTypes.number.isRequired,
      y: React.PropTypes.number.isRequired,
      label: React.PropTypes.string
    })),
    interval: React.PropTypes.string,
    placement: React.PropTypes.string,
    label: React.PropTypes.string
  },

  getDefaultProps(){
    return {
      placement: "bottom",
      points: [],
      label: ""
    };
  },

  floatFormat(number, places) {
      const multi = Math.pow(10, places);
      return parseInt(number * multi, 10) / multi;
  },

  timeLabelAsHour(point) {
    const timeMoment = moment(point.x * 1000);
    const nextMoment = timeMoment.clone().add(59, "minute");

    return (
      <span>
        {timeMoment.format("LL")}<br />
        {timeMoment.format("LT")} &mdash;&rsaquo; {nextMoment.format("LT")}
      </span>
    );
  },

  timeLabelAsDay(point) {
    const timeMoment = moment(point.x * 1000);

    return (
      <span>
        {timeMoment.format("LL")}
      </span>
    );
  },

  timeLabelAsRange(interval, point) {
    const timeMoment = moment(point.x * 1000);
    const nextMoment = timeMoment.clone().add(interval - 1, "second");

    return (
      <span>
        {timeMoment.format("lll")}<br />
        &mdash;&rsaquo; {nextMoment.format("lll")}
      </span>
    );
  },

  timeLabelAsFull(point) {
    const timeMoment = moment(point.x * 1000);
    return timeMoment.format("lll");
  },

  render(){
    const points = this.props.points;
    let maxval = 10;
    points.forEach(function(point){
      if (point.y > maxval) {
        maxval = point.y;
      }
    });

    const pointWidth = this.floatFormat(100.0 / points.length, 2) + "%";

    const interval = (points.length > 1 ? points[1].x - points[0].x : null);
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
      const pct = this.floatFormat(point.y / maxval * 99, 2) + "%";
      const timeLabel = timeLabelFunc(point);

      let title = (
        <div style={{minWidth: 100}}>
          {point.y} {this.props.label}<br/>
          {timeLabel}
        </div>
      );
      if (point.label) {
        title += <div>({point.label})</div>;
      }

      return (
        <TooltipTrigger
            placement={this.props.placement}
            key={point.x}
            title={title}>
          <a style={{width: pointWidth}}>
            <span style={{height: pct}}>{point.y}</span>
          </a>
        </TooltipTrigger>
      );
    });

    return (
      <figure className={this.props.className || '' + ' barchart'}
              height={this.props.height}
              width={this.props.width}>
        <span className="max-y" key="max-y">{maxval}</span>
        <span className="min-y" key="min-y">{0}</span>
        {children}
      </figure>
    );
  }
});

export default BarChart;
