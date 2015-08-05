# -*- coding: utf-8 -*-


class FresqueException(Exception):
    ''' Parent class of all the exception for all Fresque specific
    exceptions.
    '''
    pass


class RepoExistsException(FresqueException):
    ''' Exception thrown when trying to create a repository that already
    exists.
    '''
    pass


class FileNotFoundException(FresqueException):
    ''' Exception thrown when trying to create a repository that already
    exists.
    '''
    pass
