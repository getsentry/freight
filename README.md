# Deployment Service [name TBD]

**This project is a work in progress and is not yet intended to be production ready.**

This service is intended to augment your existing deployment processes. It should improve on what you may already have, or help you fill in what you're missing.

The overarching goal of the system is to provide easy manual and automated deploys, with a consistent central view of the world. It's heavily inspired by GitHub's processes (and it's Heaven project) as well as personal experiences of internal tools from members of the Sentry team.

It's not designed to replace something like Heroku, or other PaaS services, but rather to work *with* your existing processes, no matter what they are.

## Features

- Multiple applications. All configuration is unique per application
- Release state management (know what versions are active where, and provide a historical view)
- Per-environment deployments (i.e. different versions on staging and production)
- Environment locking (i.e. prevent people from deploying to an environment)
- Automatic deploys (i.e. by looking for VCS changes)
- Workspace management (i.e. whatever your deploy command is may be generating local artifacts, those should be cleaned up)
- Deploy queue (i.e. cramer queued sha XXX, armin queued sha YYY)
- Support for at least Fabric-based (simple shell commands) and Heroku-based deploys
- Integration with GitHub status checks (i.e. did Circle CI pass on sha XXX)
- Works behind-firewall (no inbound traffic)
- API-accessible deploy logs
- Hubot integration (starting deploys)
- Slack integraiton (notifying when deploys start/finish/fail)

## Future Ideas

The following could be considered v2 features.

### Machine-consistency service

We could run a service on each machine that would check-in with the master. This would record the current version of the application. The service would be configured with a set of apps (their environment info, how to get app version). The service could also be aware of "how do I deploy a version" which could assist in pull-based deploys.

## Heaven Inspiration

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
    enque_deployment()

def deployment_task(data):
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
