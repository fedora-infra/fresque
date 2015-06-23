# -*- coding: utf-8 -*-

'''
package for the fresque flask application
'''

from __future__ import absolute_import, unicode_literals, print_function

import os
import flask
import pygit2
import fresque

from fresque import doc_utils
from fresque import APP
from fresque.lib.git import Repository


def get_repo_by_name(name):
    path = os.path.join(
        APP.config['GIT_DIRECTORY_PATH'], flask.g.fas_user.username)
    try:
        repo_obj = Repository(os.path.join(path, name))
    except IOError:
        return "No such repo", 404
    return repo_obj


@APP.route("/git/repo/<name>")
def repo_base_view(name):
    repo_obj = get_repo_by_name(name)

    cnt = 0
    last_commits = []
    tree = []
    if not repo_obj.is_empty:
        try:
            for commit in repo_obj.walk(
                    repo_obj.head.target, pygit2.GIT_SORT_TIME):
                last_commits.append(commit)
                cnt += 1
                if cnt == 3:
                    break
            tree = sorted(last_commits[0].tree, key=lambda x: x.filemode)
        except pygit2.GitError:
            pass
    # show readme
    readme = None
    safe = False
    for i in tree:
        name, ext = os.path.splitext(i.name)
        if name == 'README':
            content = repo_obj[i.oid].data
            readme, safe = doc_utils.convert_readme(
                content, ext,
                view_file_url="#")

    return flask.render_template(
        '/git/repo.html',
        select="files",
        tree=tree,
        last_commit=repo_obj.get_last_commit(),
        repo=name,
        repo_obj=repo_obj,
        username=flask.g.fas_user.username,
        readme=readme,
        branches=sorted(repo_obj.listall_branches()),
        branchname='master'
    )
