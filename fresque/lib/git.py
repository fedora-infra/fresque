# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function
import os
import pygit2
import stat
import json
import flask
from datetime import datetime
from flask import current_app
from collections import defaultdict
from fresque.lib.utils import decode


class Repository(pygit2.Repository):

    ''' initialise the exiting repo as pygit2 Repository object'''
    def __init__(self, path):
        if os.path.exists(path):
            super(Repository, self).__init__(path)
        else:
            super(Repository, self).__init__(path + '.git')

    ''' get description of the repository '''
    def get_description(self):
        desc = os.path.join(self.path, 'description')
        if not os.path.exists(desc):
            return ""
        with open(desc) as fd:
            return decode(fd.read())
    description = property(get_description)

    ''' get name of the repository '''
    def get_name(self):
        user_repo_path = os.path.join(
            current_app.config['GIT_DIRECTORY_PATH'] +
            flask.g.fas_user.username)
        name = self.path.replace(user_repo_path, '')
        if name.startswith('/'):
            name = name[1:]
        if name.endswith('/.git/'):
            name = name[:-6]
        else:
            name = name[:-5]
        return name
    name = property(get_name)

    def get_clone_urls(self):
        ''' implement clone url for different protocols like https, ssh
            for timebeing we will be using ssh
        '''
        pass

    def branches(self):
        ''' get all the branchs of the repo '''
        return sorted(
            [x[11:] for x in self.listall_references()
                if x.startswith('refs/heads/')])

    def tags(self):
        ''' get all the tags refs for the repo '''
        return sorted(
            [x[10:] for x in self.listall_references()
                if x.startswith('refs/tags/')])

    def get_reverse_refs(self):
        ''' get the refs in form of {refs:['head', 'master']} '''
        ret = defaultdict(list)
        for ref in self.listall_references():
            if ref.startswith('refs/remotes/'):
                continue
            if ref.startswith('refs/tags/'):
                obj = self[self.lookup_reference(ref).target.hex]
                if obj.type == pygit2.GIT_OBJ_COMMIT:
                    ret[obj.hex].append(('tag', ref[10:]))
                else:
                    ret[self[self[obj.target].hex].hex].append(('tag', ref[10:]))
            else:
                ret[self.lookup_reference(ref).target.hex].append(('head', ref[11:]))
        return ret
    reverse_refs = property(get_reverse_refs)

    def ref_for_commit(self, hex):
        ''' get refs from the commit id '''
        if hasattr(hex, 'hex'):
            hex = hex.hex
        refs = self.reverse_refs.get(hex, None)
        if not refs:
            return hex
        return refs[-1][1]

    @property
    def head(self):
        try:
            return super(Repository, self).head
        except pygit2.GitError:
            return None

    def get_commits(self, skip=0, count=1, search=None, file=None):
        ''' get all the commit of the repo '''
        num = 0
        path = list()
        commits = list()
        if file:
            path = file.split('/')
        for commit in self.walk(self.head.target, pygit2.GIT_SORT_TIME):
            if search and search not in commit.message:
                continue
            if path:
                in_current = found_same = in_parent = False
                try:
                    tree = commit.tree
                    for file in path[:-1]:
                        tree = self[tree[file].hex]
                        if not isinstance(tree, pygit2.Tree):
                            raise KeyError(file)
                    oid = tree[path[-1]].oid
                    in_current = True
                except KeyError:
                    pass
                try:
                    for parent in commit.parents:
                        tree = parent.tree
                        for file in path[:-1]:
                            tree = self[tree[file].hex]
                            if not isinstance(tree, pygit2.Tree):
                                raise KeyError(file)
                        if tree[path[-1]].oid == oid:
                            in_parent = found_same = True
                            break
                        in_parent = True
                except KeyError:
                    pass
                if not in_current and not in_parent:
                    continue
                if found_same:
                    continue

            num += 1
            if num < skip:
                continue
            if num >= skip + count:
                break
            commits.append(commit)
        return commits

    def get_last_commit(self):
        ''' loops through all the commits
            has it changed since last commit?
            let's compare it's sha with the previous found sha
        '''
        for commit in self.walk(self.head.target, pygit2.GIT_SORT_TIME):
            return commit

    def get_commit_diff(self, commitid1=None, commitid2=None):
        """ Returns the diff of commit(s).
        """
        if commitid1 is None and commitid2 is None:
            diff = self.diff()
        elif None in [commitid1, commitid2]:
            commitid = [
                el
                for el in [commitid1, commitid2]
                if el is not None
            ][0]
            commit = self.get(commitid)
            if commit is None:
                raise pygit2.GitError
            if len(commit.parents) > 1:
                diff = ''
            elif len(commit.parents) == 1:
                parent = self.revparse_single('%s^' % commitid)
                diff = self.diff(parent, commit)
            else:
                # First commit in the repo
                diff = commit.tree.diff_to_tree(swap=True)
        else:
            c_t0 = self.revparse_single(commitid1)
            c_t1 = self.revparse_single(commitid2)
            diff = self.diff(c_t0, c_t1)

        return diff

    def ls_tree(self, tree, path=''):
        ret = []
        for entry in tree:
            if stat.S_ISDIR(entry.filemode):
                ret += self.ls_tree(
                    self[entry.hex], os.path.join(path, entry.name))
            else:
                ret.append(os.path.join(path, entry.name))
        return ret

    def commit_to_patch(self, commits):
        if not isinstance(commits, list):
            commits = [commits]

        patch = ""
        for cnt, commit in enumerate(commits):
            if commit.parents:
                diff = commit.tree.diff_to_tree()

                parent = self.revparse_single('%s^' % commit.oid.hex)
                diff = self.diff(parent, commit)
            else:
                # First commit in the repo
                diff = commit.tree.diff_to_tree(swap=True)

            subject = message = ''
            if '\n' in commit.message:
                subject, message = commit.message.split('\n', 1)
            else:
                subject = commit.message

            if len(commits) > 1:
                subject = '[PATCH %s/%s] %s' % (cnt + 1, len(commits), subject)

            patch += u"""From {commit} Mon Sep 17 00:00:00 2001
                From: {author_name} <{author_email}>
                Date: {date}
                Subject: {subject}

                {msg}
                ---

                {patch}
    """.format(commit=commit.oid.hex,
               author_name=commit.author.name,
               author_email=commit.author.email,
               date=datetime.utcfromtimestamp(
                   commit.commit_time).strftime('%b %d %Y %H:%M:%S +0000'),
               subject=subject,
               msg=message,
               patch=diff.patch)
        return patch

