import api from '../api';

var PollingMixin = {
  getInitialState() {
    return {
      pollingActive: true
    };
  },
  pushNotification(){
    let {app, env, number} = this.props.params;
    const url = `/deploys/${app}/${env}/${number}`;
    let body = ''

    let options = {
      body: body,
      icon: "../static/favicon.png"
    }

    if(this.state.task != undefined){
      body += `${/[^@]*/.exec(this.state.task.user.name)}'s deploy ${this.state.task.status}`
    }else{
      body += `${/[^@]*/.exec(this.state.deploys[0].user.name)}'s deploy ${this.state.deploys[0].status}`
    }

    if (!("Notification" in window)) {
    alert("This browser does not support system notifications");
    }

  else if (Notification.permission === "granted") {
    if(this.state.task != undefined){
      let notification = new Notification(`${this.state.task.name}`, options)
        notification.onclick = function(event){
        event.preventDefault();
        window.open('http://freight.getsentry.net' + url)
      }
    }
    let notification = new Notification(`${this.state.deploys[0].name}`, options)
      notification.onclick = function(event){
      event.preventDefault();
      window.open('http://freight.getsentry.net' + url)
    }
  }
  else if (Notification.permission !== 'denied') {
    Notification.requestPermission(function (permission) {
      if (permission === "granted" ) {
        if(this.state.task != undefined){
          let notification = new Notification("Freight Deploy " + this.state.task.number , options)
            notification.onclick = function(event){
            event.preventDefault();
            window.open('http://freight.getsentry.net' + url)
          }
        }
        let notification = new Notification("Freight Deploy " + this.state.deploys[0].number, options)
          notification.onclick = function(event){
          event.preventDefault();
          window.open('http://freight.getsentry.net' + url)
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
