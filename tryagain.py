#
#  _/_
#  /  __  __  , __.  _,  __.  o ____
# <__/ (_/ (_/_(_/|_(_)_(_/|_<_/ / <_
#           /        /|
#          '        |/
#

""" tryagain: A simple and pythonic retry helper
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Full documentation is at http://tryagain.readthedocs.org

    :license: MIT, see LICENSE for more details.
"""
import time
import logging
import inspect
from functools import wraps
logger = logging.getLogger('tryagain')


__version__ = '1.0'


# this code is taken from the itertools.repeat documentation. The function
# from the itertools module cannot be used in this context because of a weird
# behaviour in python: https://bugs.python.org/issue25926
def _repeat(obj, times=None):
    # repeat(10, 3) --> 10 10 10
    if times is None:
        while True:
            yield obj
    else:
        for i in range(times):
            yield obj


def _assert_callable(func, allow_none=True):
    if not (func is None and allow_none):
        if not callable(func):
            raise TypeError('{} is not callable'.format(func))


def call(func, max_attempts=None, exceptions=Exception, wait=0.0,
         cleanup_hook=None, pre_retry_hook=None):
    """ :param func (callable):
            The function to retry. No arguments are passed to this function.
            If your function requires arguments, consider defining a separate
            function or use functools.partial / a lambda function.

        :param max_attempts:
            Any integer number to limit the maximum number of attempts.
            Set to None for unlimited retries.

        :param exceptions:
            An iterable of exceptions that should result in a retry.

        :param wait:
            This can be an integer / float to specify the waittime in seconds
            before the next attempt. You can also pass a function

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
            If `wait` is set, `pre_retry_hook` will be called before the
            waittime.
            Exceptions that are raised when calling this hook are not caught.

        :returns:
            The result of calling the given `func`.

        :raises:
            Any exception which is
             - not in the given `exceptions`
             - raised in `pre_retry_hook` or in `cleanup_hook`
             - raised in the last attempt at calling `func`
    """
    # we check the callables in advance to prevent raising exceptions
    # after making the first attempt
    _assert_callable(func, allow_none=False)
    _assert_callable(cleanup_hook, allow_none=True)
    _assert_callable(pre_retry_hook, allow_none=True)
    if not (max_attempts is None or max_attempts >= 1):
        raise ValueError('max_attempts must be None or an integer >= 1')

    # if the user sets the waittime to a fixed value (int or float) we create
    # a function which always returns this fixed value. This way we avoid
    # having to make this decision in the retry loop.
    wait_func = wait if type(wait) not in [int, float] else lambda _: wait

    # check if our wait_func is a function with a single argument
    if len(inspect.signature(wait_func).parameters) != 1:
        raise ValueError(
            'The wait function must be a function with a single argument')

    def log_failed_attempt(attempt, error):
        if max_attempts is None:
            nr_display = '{}'.format(attempt)
        else:
            nr_display = '{0} / {1}'.format(attempt, max_attempts)
        logger.debug('Attempt {nr} at calling {func} failed ({msg})'
                     .format(nr=nr_display, func=func, msg=error))

    for attempt, f in enumerate(_repeat(func, max_attempts), start=1):
        try:
            return f()
        except exceptions as e:
            log_failed_attempt(attempt=attempt, error=e)
            if cleanup_hook is not None:
                cleanup_hook()
            if attempt == max_attempts:
                raise
            if wait:
                waittime = wait_func(attempt)
                time.sleep(waittime)
            if pre_retry_hook is not None:
                pre_retry_hook()


def retries(*args, **kwargs):
    """ A decorator factory for tryagain.call().

        Wrap your function in @retries(...) to give it retry powers!

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
            return call(func, *args, **kwargs)
        return _retry_wrapper
    return _retry_factory
