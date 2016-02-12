|Build Status| |Coverage Status|

tryagain
========

A lightweight and pythonic retry helper.

***Warning: This library is currently in development and not yet ready
for production.***

``tryagain`` aims to simplify working with unstable functions. Whether
you have networking code that sometimes raises timeout exceptions or you
are controlling devices which only seem to listen on the second try -
``tryagain`` makes it easier to repeat the call.

``tryagain`` offers you hooks to clean up after a failed attempt or to
prepare for the next call. You can set a waittime between retries or
specify your own waittime function to realize exponential waittimes etc.

``tryagain`` is lightweight, fully tested, MIT licensed and comes as a
single python file with no dependencies.

To install, run ``pip install tryagain``. (Does not work yet.)

Basic syntax
------------

.. code:: python

    import tryagain

    def unstable_function():
        # Attention: This function sometimes fails!
        ...

    result = tryagain.call(unstable_function,
                           max_attempts=None, exceptions=Exception, wait=0.0,
                           cleanup_hook=None, pre_retry_hook=None)

Parameters
~~~~~~~~~~

-  ``func``: The unstable function to call
-  ``max_attemps``: Any integer number to limit the maximum number of
   attempts. Set to None for unlimited retries.
-  ``exceptions``: An iterable of exceptions that should result in a
   retry.
-  ``wait``: Can be an integer or float value (to specify a waittime in seconds) or a custom function (see Waittime documentation)
-  ``cleanup_hook``: Can be set to a callable and will be called after
   an exception is raised from calling ``func``.
-  ``pre_retry_hook``: Can be set to any callable that will be called
   before ``func`` is called.

Result
~~~~~~

``tryagain.call`` will return whatever the unstable function would
return. ``tryagain.call`` reraises any exception which is:

-  not in the given ``exceptions``
-  raised in the ``pre_retry_hook`` or in ``cleanup_hook``
-  raised in the last attempt at calling the unstable function.

Quickstart
----------

Retry calling an unstable function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    import tryagain

    def unstable():
        ...

    # retry calling 'unstable' until it returns without raising an exception
    tryagain.call(unstable)

    # limit to maximum 5 attempts
    tryagain.call(unstable, max_attempts=5)

    # only retry after specific exceptions
    tryagain.call(unstable, exceptions=[ValueError, TypeError])

Waittimes
~~~~~~~~~

The tryagain library allows fixed wait values as well as custom waittime
functions.

.. code:: python

    # wait one second before trying again
    tryagain.call(unstable, wait=1.0)

    # waittime rises linearly (n is the number of attempts)
    # (will wait 1s, 2s, 3s, ...)
    tryagain.call(unstable, wait=lambda n: n)

    # waittime rises exponentially with each attempt
    # (will wait 2s, 4s, 8s, ...)
    tryagain.call(unstable, wait=lambda n: 2 ** n)

    # exponentially rising waittime with maximum
    # (will wait 2s, 4s, 5s, 5s, ..., 5s)
    tryagain.call(unstable, wait=lambda n: min(n ** 2, 5))

    # no waiting time before second attempt, 1.0s afterwards
    def no_first_wait(attempt):
        if attempt == 2:
            return 0
        else:
            return 1.0
    tryagain.call(unstable, wait=no_first_wait)

Retry calling a function with parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    # using a lambda
    tryagain.call(lambda: unstable('message', some_arg=True), wait=1.0)

    # using a partial
    from functools import partial
    tryagain.call(partial(unstable, 'message', some_arg=True), wait=1.0)

    # using a separate function
    def call_unstable_function():
        msg = 'message'
        return unstable(msg, some_arg=True)
    tryagain.call(call_unstable_function, wait=1.0)

Function decorator
~~~~~~~~~~~~~~~~~~

.. code:: python

    from tryagain import retries

    @retries(max_attempts=3)
    def unstable(arg1, arg2):
        # your unstable function here

    unstable('foo', arg2='bar')

Hooks
~~~~~

The tryagain library features two hooks that can be used,
``cleanup_hook`` and ``pre_retry_hook``.

.. code:: python


    def unstable():
        print('Calling unstable function')
        print('Exception!')
        raise Exception

    tryagain.call(unstable, max_attempts=2,
                  wait=lambda n: print('waiting'),
                  cleanup_hook=lambda: print('cleaning up'),
                  pre_retry_hook=lambda: print('do preparations'))
    'Calling unstable function'
    'Exception!'
    'cleaning up'
    'waiting'
    'do preparations'
    'Calling unstable function'
    'Exception!'
    'cleaning up'
    Error: Exception raised...

.. |Build Status| image:: https://travis-ci.org/tfeldmann/tryagain.svg?branch=develop
   :target: https://travis-ci.org/tfeldmann/tryagain
.. |Coverage Status| image:: https://coveralls.io/repos/github/tfeldmann/tryagain/badge.svg?branch=develop
   :target: https://coveralls.io/github/tfeldmann/tryagain?branch=develop
