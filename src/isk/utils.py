###############################################################################
# begin                : Sun Aug  6, 2006  4:58 PM
# copyright            : (C) 2012 by Ricardo Niederberger Cabral,
#                      : (C) 2016 Dmitry Litvinenko
# email                : ricardo dot cabral at imgseek dot net
#                      : anti1869@gmail.com
#
###############################################################################
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
###############################################################################

import logging
from itertools import chain

from isk.exceptions import ImageDBException

logger = logging.getLogger(__name__)


def deprecated(func):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """
    def _wrapper(*args, **kwargs):
        logger.warn("Call to deprecated function %s." % func.__name__,
                    category=DeprecationWarning)
        return func(*args, **kwargs)

    _wrapper.__name__ = func.__name__
    _wrapper.__doc__ = func.__doc__
    _wrapper.__dict__.update(func.__dict__)

    return _wrapper


def dump_args(func):
    """This decorator dumps out the arguments passed to a function before calling it"""

    argnames = func.__code__.co_varnames[:func.__code__.co_argcount]
    fname = func.__name__

    def _wrapper(*args, **kwargs):
        # TODO: Use setting whether to actually dump this (many calls clutter log file)
        logger.debug(
            "%s (%s)",
            fname,
            ", ".join('%s=%r' % entry for entry in chain(zip(argnames, args), kwargs.items()) if entry[0] != 'self')
        )
        return func(*args, **kwargs)
    return _wrapper


def require_known_db_id(func):
    """Checks if the 1st parameter (which should be a dbId is valid (has an internal dbSpace entry)"""
    def _wrapper(imgdb_instance, db_id, *args, **kwargs):
        if db_id not in imgdb_instance.db_spaces:
            raise ImageDBException(
                "Attempt to call %s with unknown dbid %d. "
                "Have you created it first with createdb() or loaddb()?" % (func.__name__, db_id)
            )
        return func(imgdb_instance, db_id, *args, **kwargs)
    return _wrapper


def tail(f, n: int = 20) -> str:
    """
    Returns last n ines from text file.

    :param f: Already opened file.
    :param n: How many lines to tail.
    :return: Last n lines as one string
    """

    # http://stackoverflow.com/questions/136168/get-last-n-lines-of-a-file-with-python-similar-to-tail

    BUFSIZ = 1024
    f.seek(0, 2)
    bytes = f.tell()
    size = n
    block = -1
    data = []
    while size > 0 and bytes > 0:
        if (bytes - BUFSIZ > 0):
            # Seek back one whole BUFSIZ
            f.seek(block*BUFSIZ, 2)
            # read BUFFER
            data.append(f.read(BUFSIZ))
        else:
            # file too small, start from begining
            f.seek(0, 0)
            # only read what was not read
            data.append(f.read(bytes))
        linesFound = data[-1].count('\n')
        size -= linesFound
        bytes -= BUFSIZ
        block -= 1

    return '\n'.join(''.join(data).splitlines()[-n:])
