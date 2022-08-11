import * as React from 'react';

import LoadingIndicator from './LoadingIndicator';
import TimeSince from './TimeSince';

function ExpectedChanges({changes}) {
  if (changes === undefined) {
    return (
      <LoadingIndicator>Fetching changes.. This may take a moment.</LoadingIndicator>
    );
  }

  if (changes === null) {
    return (
      <div className="alert alert-block alert-danger">
        There was a problem fetching the list of changes.
      </div>
    );
  }

  const changeList = changes.map(commit => {
    const resolvedCommit = commit.externalCommit ?? commit;

    const title = resolvedCommit?.messageHeadline ?? '';
    const titleWithoutPr = title.replace(/ \(#[0-9]+(\u2026|\))$/g, '');

    const pr =
      resolvedCommit.associatedPullRequests.nodes.length > 0
        ? resolvedCommit.associatedPullRequests.nodes[0]
        : null;

    const prLink = !pr ? null : (
      <a href={pr.url} target="_blank" rel="noreferrer" className="change-link">
        #{pr.number}
      </a>
    );

    const author = (
      <div className="change-author">
        <img src={resolvedCommit.author.avatarUrl} /> {resolvedCommit.author.name}
      </div>
    );

    const commitDate = <TimeSince date={resolvedCommit.committedDate} />;

    const labels =
      pr?.labels.nodes.map(label => (
        <div
          className="change-label"
          style={{backgroundColor: `#${label.color}`}}
          key={label.name}
        >
          {label.name}
        </div>
      )) ?? [];

    const repo = resolvedCommit.repository;

    const commitName = (
      <a
        href={resolvedCommit.url}
        target="_blank"
        rel="noreferrer"
        className="change-commit"
      >
        {repo.nameWithOwner}@{resolvedCommit.oid.slice(0, 8)}
      </a>
    );

    return (
      <li key={resolvedCommit.oid}>
        <div className="change-title">
          {titleWithoutPr} ({prLink})
        </div>
        <div className="change-tags">
          {author}
          {commitName}
          {commitDate}
        </div>
        {labels.length > 0 && <div className="change-tags">{labels}</div>}
      </li>
    );
  });

  if (changeList.length === 0) {
    return <p>Nothing to deploy!</p>;
  }

  return <ul className="remote-changes">{changeList}</ul>;
}

export default ExpectedChanges;
