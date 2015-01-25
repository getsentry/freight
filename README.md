The deployment services works in the following fashion:

```
# call out to GitHub and attempt to register a new deployment
# this will fail if certain checks do not pass
if not create_github_deployment(force=False):
    explain_error()

# listen for github webhooks suggesting the deployment was created
# this allow other services to also create deployments
def on_github_deployment(data):
    deploy()

def deploy():
    clone_or_update_repo()
    run_deployment_command()
```


