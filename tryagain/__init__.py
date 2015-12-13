
#  _/_
#  /  __  __  , __.  _,  __.  o ____
# <__/ (_/ (_/_(_/|_(_)_(_/|_<_/ / <_
#           /        /|
#          '        |/

""" tryagain: A python retry helper
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Full documentation is at ___.

    :copyright: (c) 2015 by Thomas Feldmann.
    :license:   MIT, see LICENSE for more details.
"""

import time
import logging
from functools import wraps
from itertools import repeat
logger = logging.getLogger(__name__)


__version__ = 1.0


def _check_callable(func, allow_none=True):
    if not (func is None and allow_none):
        if not callable(func):
            raise TypeError('{} is not callable'.format(func))


def retry_call(func, max_attempts=None, retry_exceptions=Exception, delay=0.0,
               cleanup_hook=None, pre_retry_hook=None):
    """
        :param func (callable):
            The function to retry. No arguments are passed to this function.
            If your function requires arguments, consider defining a separate
            function or use functools.partial / a lambda function.

        :param max_attempts:
            Any integer number to limit the maximum number of attempts.
            Set to None for unlimited retries.

        :param retry_exceptions:
            An iterable of exceptions that should result in a retry.

        :param delay:
            Specify how many seconds

        :param cleanup_hook:
            Can be set to a callable and will be called after an exception is
            raised from calling `func`.
            No arguments are passed to this function.
            If your function requires arguments, consider defining a separate
            function or use functools.partial / a lambda function.

        :param pre_retry_hook:
            Can be set to any callable that will be called before `function`
            is called.
            No arguments are passed to this function.
            If your function requires arguments, consider defining a separate
            function or use functools.partial / a lambda function.
            If `delay` is set, `pre_retry_hook` will be called before the
            waittime.
            Exceptions that are raised when calling this hook are not caught.

        :returns:
            - The result of calling the given `func`.

        :raises:
            Any exception which is
             - not in the given `retry_exceptions`
             - raised in `pre_retry_hook` or in `cleanup_hook`
             - raised in the last attempt at calling `func`
    """
    # we check the callables in advance to prevent raising exceptions
    # after making the first attempt
    _check_callable(func, allow_none=False)
    _check_callable(cleanup_hook, allow_none=True)
    _check_callable(pre_retry_hook, allow_none=True)
    if not (max_attempts is None or max_attempts >= 1):
        raise ValueError('max_attempts must be None or an integer >= 1')

    for attempt, f in enumerate(repeat(func, max_attempts), start=1):
        try:
            return f()
        except retry_exceptions as e:
            if max_attempts is not None:
                nr_display = '#{0} / {1}'.format(attempt, max_attempts)
            else:
                nr_display = '#{}'.format(attempt)
            logger.debug('Attempt {nr} at calling {func} failed ({msg})'
                         .format(nr=nr_display, func=f, msg=e))
            if cleanup_hook is not None:
                cleanup_hook()
            if attempt == max_attempts:
                raise
            if delay:
                time.sleep(delay)
            if pre_retry_hook is not None:
                pre_retry_hook()


def retry(*args, **kwargs):
    """ A decorator factory for retry_call().

        Wrap your function in @retriable(...) to give it retry powers!

    Arguments:
        Same as for `retry`, with the exception
        of `action`, `args`, and `kwargs`,
        which are left to the normal function definition.
    Returns:
        A function decorator
    Example:
        >>> count = 0
        >>> @retry(sleeptime=0, jitter=0)
        ... def foo():
        ...     global count
        ...     count += 1
        ...     print(count)
        ...     if count < 3:
        ...         raise ValueError("count too small")
        ...     return "success!"
        >>> foo()
        1
        2
        3
        'success!'
    """
    def _retry_factory(func):
        @wraps(func)
        def _retry_wrapper(*args, **kwargs):
            return retry_call(func, *args, **kwargs)
        return _retry_wrapper
    return _retry_factory
