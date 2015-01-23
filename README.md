# github-notify

GitHub Issue Notifier

## Forked!!

This is forked from https://github.com/sivel/github-notify.git. I used it as a base to scratch my own itch.

## This version has

Sends an email alert based on matching a regex pattern in one of the following:

1. Issue/Pull Request Subject
1. Issue/Pull Request Body

## Installing

1. `pip install -r requirements.txt`
1. Create a `github-notify.yaml` configuration file as described below

## github-notify.yaml

This file can live at `./github-notify.yaml`, `~/.github-notify.yaml`, or `/etc/github-notify.yaml`

```yaml
---
github_username: 'erjohnso'
github_password: '6689ba85bb024d1b97370c45f1316a16d08bba20'
#github_client_id: 1ecad3b34f7b437db6d0
#github_client_secret: 6689ba85bb024d1b97370c45f1316a16d08bba20

github_repository:
    - 'apache/libcloud'
    - 'jclouds/jclouds-labs-google'
    - 'fog/fog'
    - 'ansible/ansible'
    - 'ansible/ansible-modules-core'
    - 'ansible/ansible-modules-extras'
    - 'saltstack/salt'
    - 'chef/knife-google'
    - 'puppetlabs/puppetlabs-gce_compute'
    - 'mitchellh/vagrant-google'
    - 'mitchellh/packer'

regex_pattern: 'gce|gcs|google'
skip_string: '.google.com/'
github_state: 'open'
```

*The above values are dummy placeholder values and are not valid for use*

### GitHub credentials

1. You will need to [register an application](https://github.com/settings/applications/new)
to provide API access.  The Client ID and Secret will need to be populated as
shown in the above example.

1. Or.. you can use your github username/password.

## Running

It is recommended that you run `github-notify.py` via cron. The fewer pull requests and
issues that a project has the more frequently you can run the cron job. I'd recommend
starting with every 60 minutes (1 hour).

NOTE: This is how this version runs also. It writes to stdout and relies on your
local cron/mail settings to deliver the script's stdout to your inbox. This version
strips out the mailgun support.
