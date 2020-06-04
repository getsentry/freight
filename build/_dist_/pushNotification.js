function createNotification(message, url, options) {
  const notification = new Notification(message, options);

  notification.onclick = function (event) {
    event.preventDefault();
    window.open(url);
  };
}

function pushNotification(task, path) {
  const userName = /[^@]*/.exec(task.user.name);
  const body = `${userName}'s deploy ${task.status}`;
  const {
    hostname,
    protocol,
    port
  } = window.location;
  let url;

  if (port !== '') {
    url = `${protocol}//${hostname}:${port}${path}`;
  } else {
    url = `${protocol}//${hostname}${path}`;
  }

  const options = {
    body,
    icon: '/static/favicon.png'
  };

  if (window.Notification && Notification.permission !== 'denied') {
    Notification.requestPermission(function (permission) {
      if (permission === 'granted') {
        createNotification(task.name, url, options);
      }
    });
  }
}

export default pushNotification;