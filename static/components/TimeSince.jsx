import {useCallback, useEffect, useMemo, useRef, useState} from 'react';
import {formatDistanceToNowStrict} from 'date-fns';
import PropTypes from 'prop-types';

const DELAY = 2600;

function TimeSince({date}) {
  const dateObject = useMemo(() => new Date(date), [date]);

  const getRelativeDate = useCallback(
    () => formatDistanceToNowStrict(dateObject, {addSuffix: true}),
    [dateObject]
  );

  const [relativeDate, setRelativeDate] = useState(getRelativeDate());
  const tickerRef = useRef(undefined);

  useEffect(() => {
    tickerRef.current = setInterval(() => setRelativeDate(getRelativeDate), DELAY);

    return () => {
      clearInterval(tickerRef.current);
      tickerRef.current = undefined;
    };
  }, [getRelativeDate]);

  const time = dateObject.toISOString();

  return (
    <time title={time} dateTime={time}>
      {relativeDate}
    </time>
  );
}

TimeSince.propTypes = {
  date: PropTypes.any.isRequired,
};

export default TimeSince;
