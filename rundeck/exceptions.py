__docformat__ = "restructuredtext en"
"""
:summary: Exceptions

:license: Creative Commons Attribution-ShareAlike 3.0 Unported
:author: Mark LaPerriere
:contact: rundeckrun@mindmind.com
:copyright: Mark LaPerriere 2013
"""


class InvalidAuthentication(Exception):
    """ The method of authentication is not valid """


class JobNotFound(Exception):
    """ The Job could not be found in the Project """


class MissingProjectArgument(Exception):
    """ The requested action requires a Project name to be supplied """


class InvalidJobArgument(Exception):
    """ The Job name or ID is not valid """


class InvalidResponseFormat(Exception):
    """ The requested response format is not supported """
