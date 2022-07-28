import * as React from 'react';
import {formatDistanceToNowStrict} from 'date-fns';
import PropTypes from 'prop-types';

const DELAY = 2600;

function TimeSince({date}) {
  const dateObject = React.useMemo(() => new Date(date), [date]);

  const getRelativeDate = React.useCallback(
    () => formatDistanceToNowStrict(dateObject, {addSuffix: true}),
    [dateObject]
  );

  const [relativeDate, setRelativeDate] = React.useState(getRelativeDate());
  const tickerRef = React.useRef(undefined);

  React.useEffect(() => {
    tickerRef.current = setInterval(() => setRelativeDate(getRelativeDate), DELAY);

    return () => {
      clearInterval(tickerRef.current);
      tickerRef.current = undefined;
    };
  }, [getRelativeDate]);

  return <time dateTime={dateObject.toISOString()}>{relativeDate}</time>;
}

TimeSince.propTypes = {
  date: PropTypes.any.isRequired,
};

export default TimeSince;
