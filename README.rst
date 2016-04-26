|Build Status| |Coverage Status|

tryagain
========

A lightweight and pythonic retry helper.

``tryagain`` aims to simplify working with unstable functions. Whether
you have networking code that sometimes raises timeout exceptions or you
are controlling devices which only seem to listen on the second try -
``tryagain`` makes it easier to repeat the call.

``tryagain`` offers you hooks to clean up after a failed attempt or to
prepare for the next call. You can set a waittime between retries or
specify your own waittime function to realize exponential waittimes etc.

``tryagain`` is lightweight, fully tested, MIT licensed and comes as a single
python file with no dependencies. It supports Python 2.6+ and 3.2+.

To install, run ``pip install tryagain``.


Basic syntax
------------
Using the tryagain function ``call``:

.. code:: python

    import tryagain

    def unstable_function():
        # Attention: This function sometimes fails!
        ...

    result = tryagain.call(unstable_function,
                           max_attempts=None, exceptions=Exception, wait=0.0,
                           cleanup_hook=None, pre_retry_hook=None)

Using the tryagain decorator ``retries``:

.. code:: python

    from tryagain import retries

    @retries(max_attempts=3)
    def unstable_funcation(arg1, arg2):
        # Attention: This function sometimes fails!
        ...

    result = unstable_function('foo', arg2='bar')


Parameters
~~~~~~~~~~

-  ``func``: The unstable function to call
-  ``max_attemps``: Any integer number to limit the maximum number of
   attempts. Set to None for unlimited retries. (Default = None)
-  ``exceptions``: An iterable of exceptions that should result in a
   retry. (Default = ``Exception``)
-  ``wait``: Can be an integer or float value (to specify a waittime in seconds) or a custom function (see Waittime documentation) (Default = 0.0)
-  ``cleanup_hook``: Can be set to a callable and will be called after
   an exception is raised from calling ``func``. (Default = None)
-  ``pre_retry_hook``: Can be set to any callable that will be called
   before ``func`` is called. (Default = None)


Result
~~~~~~

``tryagain.call`` will return whatever the unstable function would
return. ``tryagain.call`` (and the decorator ``tryagain.retries``) reraises
any exception which is:

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
    result = tryagain.call(unstable)

    # limit to maximum 5 attempts
    result = tryagain.call(unstable, max_attempts=5)

    # only retry after specific exceptions
    result = tryagain.call(unstable, exceptions=(ValueError, TypeError))


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

The ``tryagain.call``-function only supports a function reference as the
``func`` parameter. To pass arguments to the unstable function you have to use
one of the following idioms:

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

But it is much nicer to wrap your unstable function in the ``@retries``
decorator.
This way you can call your unstable function with parameters easily:


Function decorator
~~~~~~~~~~~~~~~~~~

Instead of using the ``tryagain.call`` function, you can use the ``retries``
decorator.

.. code:: python

    from tryagain import retries
    @retries(max_attempts=3, exceptions=(TypeError, ValueError))
    def unstable(arg1, arg2):
        # your unstable function here

    result = unstable('foo', arg2='bar')

The decorator takes the same arguments as the ``call``-function
except the ``func`` parameter.


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


.. |Build Status| image:: https://travis-ci.org/tfeldmann/tryagain.svg?branch=master
   :target: https://travis-ci.org/tfeldmann/tryagain
.. |Coverage Status| image:: https://coveralls.io/repos/github/tfeldmann/tryagain/badge.svg?branch=master
   :target: https://coveralls.io/github/tfeldmann/tryagain?branch=master
