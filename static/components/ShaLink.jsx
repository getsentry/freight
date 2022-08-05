import * as React from 'react';

import IconGithub from 'app/icons/IconGithub';

function getRemoteIcon({name}) {
  if (name === 'github.com') {
    return <IconGithub size="12px" />;
  }

  return null;
}

function ShaLink({sha, url, remote}) {
  const icon = getRemoteIcon(remote ?? {});

  const shaNode = (
    <React.Fragment>
      {icon} {sha.substr(0, 7)}
    </React.Fragment>
  );

  if (!url) {
    return <span className="sha">{shaNode}</span>;
  }

  return (
    <a href={url} className="sha" target="_blank" rel="noreferrer">
      {shaNode}
    </a>
  );
}

export default ShaLink;
