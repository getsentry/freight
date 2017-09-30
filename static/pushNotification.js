
function pushNotification(task, path){
  let userName = /[^@]*/.exec(task.user.name);
  let body     = `${userName}'s deploy ${task.status}`;
  let {hostname, protocol,port} = window.location;

  if(port !== ''){
    var url  = `${protocol}//${hostname}:${port}${path}`;
  }else{
    var url  = `${protocol}//${hostname}${path}`;
  }

  const options = {
    body: body,
    icon: "/static/favicon.png"
  };

  function createNotification(message, url, options){
    let notification = new Notification(message, options);
    notification.onclick = function(event){
      event.preventDefault();
      window.open(url);
    }
  }

  if(window.Notification && Notification.permission !== 'denied'){
    Notification.requestPermission(function(permission){
      if(permission === 'granted'){
        createNotification(task.name, url, options);
      }
    })
  }
}

export default pushNotification;
