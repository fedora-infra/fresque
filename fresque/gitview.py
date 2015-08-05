# -*- coding: utf-8 -*-

'''
package for the fresque flask application
'''

from __future__ import absolute_import, unicode_literals, print_function

import os
import flask
import pygit2
import fresque

import kitchen.text.converters as ktc

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import guess_lexer_for_filename
from pygments.lexers.special import TextLexer
from pygments.util import ClassNotFound

import mimetypes
import chardet

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


def __get_file_in_tree(repo_obj, tree, filepath):
    ''' Retrieve the entry corresponding to the provided filename in a
    given tree.
    '''
    filename = filepath[0]
    if isinstance(tree, pygit2.Blob):
        return
    for entry in tree:
        if entry.name == filename:
            if len(filepath) == 1:
                return repo_obj[entry.oid]
            else:
                return __get_file_in_tree(
                    repo_obj, repo_obj[entry.oid], filepath[1:])


@APP.route("/git/repo/<packagename>")
def repo_base_view(packagename):
    repo_obj = get_repo_by_name(packagename)

    tree = []
    if not repo_obj.is_empty:
        try:
            last_commit = repo_obj.get_last_commit()
            tree = sorted(last_commit.tree, key=lambda x: x.filemode)
        except pygit2.GitError:
            pass

    return flask.render_template(
        '/git/repo.html',
        select="files",
        tree=tree,
        last_commit=last_commit,
        repo=packagename,
        repo_obj=repo_obj,
        branches=sorted(repo_obj.listall_branches()),
        branchname='master'
    )


@APP.route('/git/<repo>/blob/<path:identifier>/f/<path:filename>')
def view_file(repo, identifier, filename):
    """ Displays the content of a file or a tree for the specified repo.
    """
    if not repo:
        flask.abort(404, 'Project not found')

    repo_obj = get_repo_by_name(repo)

    if repo_obj.is_empty:
        flask.abort(404, 'Empty repo cannot have a file')

    if identifier in repo_obj.listall_branches():
        branchname = identifier
        branch = repo_obj.lookup_branch(identifier)
        commit = branch.get_object()
    else:
        try:
            commit = repo_obj.get(identifier)
            branchname = identifier
        except ValueError:
            if 'master' not in repo_obj.listall_branches():
                flask.abort(404, 'Branch no found')
            # If it's not a commit id then it's part of the filename
            commit = repo_obj[repo_obj.head.target]
            branchname = 'master'

    if commit and not isinstance(commit, pygit2.Blob):
        content = __get_file_in_tree(
            repo_obj, commit.tree, filename.split('/'))
        if not content:
            flask.abort(404, 'File not found')
        content = repo_obj[content.oid]
    else:
        content = commit

    if isinstance(content, pygit2.Blob):
        if content.is_binary:
            output_type = 'binary'
        else:
            try:
                lexer = guess_lexer_for_filename(
                    filename,
                    content.data
                )
            except ClassNotFound:
                lexer = TextLexer()

            content = highlight(
                content.data,
                lexer,
                HtmlFormatter(
                    noclasses=True,
                    style="tango",)
            )
            output_type = 'file'
    else:
        content = sorted(content, key=lambda x: x.filemode)
        output_type = 'tree'

    return flask.render_template(
        '/git/file.html',
        select='files',
        repo=repo,
        branchname=branchname,
        filename=filename,
        content=content,
        output_type=output_type,
        last_commit=repo_obj.get_last_commit()
    )


@APP.route('/git/<repo>/raw/<path:identifier>/f/<path:filename>')
def view_raw_file(repo, identifier, filename):

    if not repo:
        flask.abort(404, 'Project not found')

    repo_obj = get_repo_by_name(repo)

    if repo_obj.is_empty:
        flask.abort(404, 'Empty repo cannot have a file')

    if identifier in repo_obj.listall_branches():
        branch = repo_obj.lookup_branch(identifier)
        commit = branch.get_object()
    else:
        try:
            commit = repo_obj.get(identifier)
        except ValueError:
            if 'master' not in repo_obj.listall_branches():
                flask.abort(404, 'Branch no found')
            # If it's not a commit id then it's part of the filename
            commit = repo_obj[repo_obj.head.target]

    if not commit:
        flask.abort(400, 'Commit %s not found' % (identifier))

    mimetype = None
    encoding = None
    if filename:
        content = __get_file_in_tree(
            repo_obj, commit.tree, filename.split('/'))
        if not content or isinstance(content, pygit2.Tree):
            flask.abort(404, 'File not found')

        mimetype, encoding = mimetypes.guess_type(filename)
        data = repo_obj[content.oid].data
    else:
        if commit.parents:
            diff = commit.tree.diff_to_tree()

            try:
                parent = repo_obj.revparse_single('%s^' % identifier)
                diff = repo_obj.diff(parent, commit)
            except (KeyError, ValueError):
                flask.abort(404, 'Identifier not found')
        else:
            # First commit in the repo
            diff = commit.tree.diff_to_tree(swap=True)
        data = diff.patch

    if not data:
        flask.abort(404, 'No content found')

    if not mimetype and data[:2] == '#!':
        mimetype = 'text/plain'

    if not mimetype:
        if '\0' in data:
            mimetype = 'application/octet-stream'
        else:
            mimetype = 'text/plain'

    if mimetype.startswith('text/') and not encoding:
        encoding = chardet.detect(ktc.to_bytes(data))['encoding']

    headers = {'Content-Type': mimetype}
    if encoding:
        headers['Content-Encoding'] = encoding

    return (data, 200, headers)
