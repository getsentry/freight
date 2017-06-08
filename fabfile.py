from fabric.api import task, env, execute, sudo, run
from fabric.context_managers import cd, prefix
from gonzo.tasks import release as gonzo_release, supervisord


@task
def release():
    hosts = env.hosts

    for task in [
        gonzo_release.push,
        gonzo_release.activate,
        restart_services,
    ]:
        execute(task, hosts=hosts)

    sudo('chown -R freight: /srv/freight')
    with cd('/srv/freight/releases/current/freight'):
        sudo('npm install --unsafe-perm')


@task
def freight_first_setup():
    release()

    with cd('/srv/freight/releases/current/freight'):
        sudo(
            '/srv/freight/bin/python /srv/freight/releases/current/freight/setup.py develop',
            user='freight'
        )
        db_setup()
    sudo('/etc/init.d/nginx restart')
    execute(restart_services)


@task
def restart_services():
    supervisord.restart('freight-frontend')
    supervisord.restart('freight-worker')


def db_setup():
    env.warn_only = True
    dir = "/srv/freight/releases/current/freight"
    sudo('createdb -E utf-8 freight;', user='postgres')
    sudo("psql -c 'CREATE ROLE root superuser';", user='postgres')
    sudo("psql -c 'GRANT ROOT TO root';", user='postgres')
    sudo("psql -c 'ALTER role root with login';", user='postgres')
    with cd(dir), prefix('. /srv/freight/bin/activate'):
        sudo('./bin/upgrade', user='root')

    sudo("psql -c 'CREATE ROLE freight';", user='postgres')
    sudo("psql -c 'GRANT ROOT TO freight';", user='postgres')
    sudo("psql -c 'ALTER role freight with login';", user='postgres')
