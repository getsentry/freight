import * as React from 'react';

import BarChart from 'app/components/BarChart';
import usePolling from 'app/hooks/usePolling';

function dataToPoints(data) {
  return data.map(point => ({x: point[0], y: point[1]}));
}

function DeployChart({app}) {
  const [data, setData] = React.useState([]);

  const url = `/deploy-stats/${app ? `?app=${app}` : ''}`;
  usePolling({url, handleRecieveData: setData});

  return (
    <div className="section">
      <BarChart points={dataToPoints(data)} label="deploys" />
    </div>
  );
}

export default DeployChart;
