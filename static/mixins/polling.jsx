import api from '../api';

var PollingMixin = {
  getInitialState() {
    return {
      pollingActive: true
    };
  },
  pushNotification(){
    let body;
    let {app, env, number} = this.props.params;

    let hostname = location.hostname
    var path = `/deploys/${app}/${env}/${number}`;

    if(this.state.task == undefined){
      let {name} = this.state.deploys[0].app
      let {environment, number} = this.state.deploys[0]

      var path = `/deploys/${name}/${environment}/${number}`
    }

    if(hostname == "localhost"){
      var url = `${location.protocol}//${location.hostname}:${location.port}${path}`
      var ourl = `${location.protocol}//${location.hostname}:${location.port}${path}`
    }else{
      var url = `${location.protocol}//${location.hostname}${path}`
      var ourl = `${location.protocol}//${location.hostname}${path}`
    }

    if(this.state.task !== undefined){
      body = `${/[^@]*/.exec(this.state.task.user.name)}'s deploy ${this.state.task.status}`;
    }else{
      body = `${/[^@]*/.exec(this.state.deploys[0].user.name)}'s deploy ${this.state.deploys[0].status}`;
    }

    const options = {
      body: body,
      icon: "/static/favicon.png"
    }

  if (Notification.permission === "granted") {
    if(this.state.task != undefined){
      let notification = new Notification(this.state.task.name, options)
        notification.onclick = function(event){
          event.preventDefault();
          window.open(url)
      }
    }
      let notification = new Notification(this.state.deploys[0].name, options)
        notification.onclick = function(event){
          event.preventDefault();
          window.open(ourl)
    }
  }
  else if (Notification.permission !== 'denied') {
    Notification.requestPermission(function (permission) {
      if (permission === "granted" ) {
        if(this.state.task != undefined){
          let notification = new Notification(this.state.task.name, options)
            notification.onclick = function(event){
              event.preventDefault();
              window.open(url)
          }
        }
          let notification = new Notification(this.state.deploys[0].name, options)
            notification.onclick = function(event){
              event.preventDefault();
              window.open(ourl)
          }
        }
      });
    }
  },
  componentWillMount(prevProps, prevState) {
    this._timeoutId = window.setTimeout(this.pollForChanges, 3000);
  },
  componentDidUpdate(prevProps, prevState){
    if (prevState.task && prevState.task.status === 'in_progress' && this.state.task.status === 'finished') {
      this.pushNotification();
    }
  },
  componentWillUnmount() {
    if (this._timeoutId) {
      window.clearTimeout(this._timeoutId);
    }
  },

  pollForChanges() {
    var url = this.getPollingUrl();

    if (!this.state.pollingActive) {
      this._timeoutId = window.setTimeout(this.pollForChanges, 3000);
    }

    api.request(url, {
      success: (data) => {
        this.pollingReceiveData(data);
        this._timeoutId = window.setTimeout(this.pollForChanges, 3000);
      },
      error: () => {
        this._timeoutId = window.setTimeout(this.pollForChanges, 10000);
      }
    });
  },
};

export default PollingMixin;
