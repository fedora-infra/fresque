'''
package for the fresque flask application
'''

from __future__ import absolute_import, unicode_literals, print_function

import os
import flask
import pygit2

from fresque import APP
from fresque.lib.git import Repository


@APP.route("/repo/<name>")
def repo_base_view(name):
    path = os.path.join(
        APP.config['GIT_DIRECTORY_PATH'], flask.g.fas_user.username)

    try:
        repo_obj = Repository(os.path.join(path, name))
    except IOError:
        return "No such repo", 404

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
    return flask.render_template('/git/repo.html', tree=tree)
