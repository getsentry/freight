import {useEffect, useRef} from 'react';

import pushNotification from 'app/utils/pushNotification';

/**
 * Produces a mapping of deploy.id -> deploy.status
 */
function mapDeployStatus(deploys) {
  return Object.fromEntries(deploys.map(deploy => [deploy.id, deploy.status]));
}

/**
 * Triggers a notification when any of the deploys in the list become completed
 */
function useDeployFinishedNotification(deploys) {
  const lastDeployStatus = useRef(null);

  if (lastDeployStatus.current === null) {
    lastDeployStatus.current = mapDeployStatus(deploys);
  }

  useEffect(() => {
    deploys.forEach(deploy => {
      // Did the deploy status change from in_progress to finished?
      if (
        lastDeployStatus.current[deploy.id] === 'in_progress' &&
        deploy.status === 'finished'
      ) {
        const {name} = deploy.app;
        const {environment, number} = deploy;
        const path = `/deploys/${name}/${environment}/${number}`;
        pushNotification(deploy, path);
      }
    });

    lastDeployStatus.current = mapDeployStatus(deploys);
  }, [deploys]);

  // Request permission for notifications
  useEffect(() => {
    if (window.Notification && window.Notification.permission !== 'denied') {
      window.Notification.requestPermission();
    }
  }, []);
}

export default useDeployFinishedNotification;
