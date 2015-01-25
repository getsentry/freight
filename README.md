The basis for this is modeled after Heaven, but we may want to take an alternative approach. GitHub shouldn't be hardcoded for the system to work, but rather the primary implementation will be GitHub (i.e. specific endpoints just for it).

For a simple integration, it would work like the following:

```
POST /api/0/:app/deploy
    ?[sha=:sha]
    &[force=true]
    &[env=:environment]
```

The logic for the endpoint would be a bit like this:

```
# call out to GitHub and attempt to register a new deployment
# this will fail if certain checks do not pass

# this is the deploy API endpoint
def deploy(app, params):
    if not github.create_deployment(params):
        return 400, "reason"

# listen for github webhooks suggesting the deployment was created
# this allow other services to also create deployments
def on_github_deployment(data):
    clone_or_update_repo()
    run_deployment_command()
```


The deployment command could be specific per application, and would be specified via the application configuration:

```
{
    "sentry": {
        # the raw shell command that should run, with a few variables available
        "deploy": "fab -R {env} deploy:sha={sha}",
        
        # we want a way to specify which deployment integration this is using
        "via": "github"
    }
}
```
