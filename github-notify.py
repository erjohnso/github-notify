#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2014 Matt Martz
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import re
import json
import yaml
import requests
import argparse

from github import Github


def get_config(path=None):
    if path is None:
        config_files = (
            './github-notify.yaml',
            os.path.expanduser('~/.github-notify.yaml'),
            os.path.expanduser('~/github-notify/github-notify.yaml'),
            '/etc/github-notify.yaml'
        )
        for config_file in config_files:
            try:
                with open(os.path.realpath(config_file)) as f:
                    config = yaml.load(f)
            except:
                pass
            else:
                return config
    with open(os.path.realpath(path)) as f:
        return yaml.load(f)

    raise SystemExit('Config file not found at: %s' % ', '.join(config_files))


def alert(found, config, item, known, repo):
    if repo not in known:
        known[repo] = []
    known[repo].append(item.number)
    return 'Found in: %s\n\tURL: %s\n\tTitle: %s\n\tUser: %s\n' % (
            found, item.html_url, item.title, item.user.login)


def scan_github_issues(config, cache, ignoref):
    output = {}
    pattern = re.compile(config['regex_pattern'], flags=re.I)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        with open(cache) as f:
            known = json.load(f)
    except IOError, ValueError:
        known = {}
    try:
        with open(ignoref) as f:
            ignore = json.load(f)
    except IOError, ValueError:
        ignore = {}

    if "github_username" in config and "github_password" in config:
        g = Github(config["github_username"], config["github_password"],
                   per_page=100)
    elif "client_id" in config and "client_secret" in config:
        g = Github(client_id=config["github_client_id"],
                   client_secret=config["github_client_secret"],
                   per_page=100)

    if not isinstance(config['github_repository'], list):
        repos = [config['github_repository']]
    else:
        repos = config['github_repository']

    for repo_name in repos:
        try:
            repo = g.get_repo(repo_name)
        except Exception as e:
            print "Error fetching repo: '%s'" % repo_name
            print e
            continue

        for pull in repo.get_pulls(state=config['github_state']):
            if pull.number in known.get(repo_name, []):
                continue
            if pull.number in ignore.get(repo_name, []):
                continue

            try:
                if pattern.search(pull.title) and pull.title.find(config['skip_string']) == -1:
                    if repo_name in output:
                        output[repo_name].append(alert('pull.title', config, pull, known, repo_name))
                    else:
                        output[repo_name] = [alert('pull.title', config, pull, known, repo_name)]
                    continue
            except TypeError:
                pass

            try:
                if pattern.search(pull.body) and pull.body.find(config['skip_string']) == -1:
                    if repo_name in output:
                        output[repo_name].append(alert('pull.body', config, pull, known, repo_name))
                    else:
                        output[repo_name] = [alert('pull.body', config, pull, known, repo_name)]
                    continue
            except TypeError:
                pass

        for issue in repo.get_issues(state=config['github_state']):
            if issue.number in known.get(repo_name, []):
                continue
            if issue.number in ignore.get(repo_name, []):
                continue

            try:
                if issue.pull_request is not None:
                    continue
            except Exception as e:
                print "Error '%s' with repo/issue: %s/%s" % (str(e), repo_name, issue.number)
                continue

            try:
                if pattern.search(issue.title) and issue.title.find(config['skip_string']) == -1:
                    if repo_name in output:
                        output[repo_name].append(alert('issue.title', config, issue, known, repo_name))
                    else:
                        output[repo_name] = [alert('issue.title', config, issue, known, repo_name)]
                    continue
            except TypeError:
                pass

            try:
                if pattern.search(issue.body) and issue.body.find(config['skip_string']) == -1:
                    if repo_name in output:
                        output[repo_name].append(alert('issue.body', config, issue, known, repo_name))
                    else:
                        output[repo_name] = [alert('issue.body', config, issue, known, repo_name)]
                    continue
            except TypeError:
                pass

    for repo_name in output:
        print "# Repo:", repo_name
        print "\t" + u"\n\t".join(output[repo_name]).encode('utf-8')
        print

    if output:
        try:
            with open(cache, 'w+') as f:
                json.dump(known, f, indent=4, sort_keys=True)
        except (IOError, ValueError):
            pass

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument("--config", help="path to YAML config file", default=None)
    p.add_argument("--cache", help="path to JSON cache file", default=None)
    p.add_argument("--ignore", help="path to JSON ignore file", default=None)
    args = p.parse_args()

    if args.cache is None:
        args.cache = os.path.expanduser('~/github-notify/cache.json')
    if args.ignore is None:
        args.ignore = os.path.expanduser('~/github-notify/ignore.json')

    scan_github_issues(get_config(args.config), args.cache, args.ignore)

