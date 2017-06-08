# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  # this is a third-party xenial image because:
  #  1. trusty has a python 2.7 that's too old and upgrading more or less requires fetch & compile
  #  2. canonical's xenial image is broken under vagrant: https://bugs.launchpad.net/cloud-images/+bug/1569237
  config.vm.box = "bento/ubuntu-16.04"

  # default flask debug server port
  config.vm.network "forwarded_port", guest: 5000, host: 5000

  config.vm.provision "shell", path: "bin/setup-dev-env", privileged: false
end
