
function pushNotification(task, path){
  let userName = /[^@]*/.exec(task.user.name);
  let body     = `${userName}'s deploy ${task.status}`;
  let {hostname, protocol,port} = location;

  if(hostname == "localhost"){
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

  if(Notification.permission !== 'denied'){
    Notification.requestPermission(function(permission){
      if(permission === 'granted'){
        createNotification(task.name, url, options);
      }
    })
  }
}

export default pushNotification;
