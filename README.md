# tryagain
A simple and pythonic retry helper.
This library is currently in development.

To install, run `pip install tryagain`.


## Quickstart


### Retry calling an unstable function
```python
from tryagain import retry_call

def unstable():
    ...

# retry calling 'unstable' until it returns without raising an exception
retry_call(unstable)

# limit to maximum 5 attempts
retry_call(unstable, max_attempts=5)

# only retry after specific exceptions
retry_call(unstable, exceptions=[ValueError, TypeError])
```


### Waittimes
The tryagain library allows fixed wait values as well as custom waittime
functions.

```python
# wait one second before trying again
retry_call(unstable, wait=1.0)

# waittime rises linearly (n is the number of attempts)
# (will wait 1s, 2s, 3s, ...)
retry_call(unstable, wait=lambda n: n)

# waittime rises exponentially with each attempt
# (will wait 2s, 4s, 8s, ...)
retry_call(unstable, wait=lambda n: 2 ** n)

# exponentially rising waittime with maximum
# (will wait 2s, 4s, 5s, 5s, ..., 5s)
retry_call(unstable, wait=lambda n: min(n ** 2, 5))

# no waiting time before second attempt, 1.0s afterwards
def no_first_wait(attempt):
    if attempt == 2:
        return 0
    else:
        return 1.0
retry_call(unstable, wait=no_first_wait)
```


### Retry calling a function with parameters
```python
# using a lambda
retry_call(lambda: unstable('message', underscores=True), wait=1.0)

# using a partial
from functools import partial
retry_call(partial(unstable, 'message', underscores=True), wait=1.0)

# using a separate function
def call_unstable_function():
    msg = 'message'
    return unstable(msg, underscores=True)
retry_call(call_unstable_function, wait=1.0)

# using the 'args' and 'kwargs' parameters
retry_call(unstable, args=['message'], kwargs={'underscores': True}, wait=1.0)
```


### Function decorator
```python
from tryagain import retry

@retry(max_attempts=3)
def unstable():
```


### Hooks
The tryagain library features two hooks that can be used, `cleanup_hook` and
`pre_retry_hook`.

```python

def unstable():
    print('Calling unstable function')
    raise Exception
# TODO: Optional variable attempts in wait und hooks!

retry_call(unstable, max_attempts=2,
           wait=lambda n: print('waiting'),
           cleanup_hook=lambda: print('cleaning up'),
           pre_retry_hook=lambda: print('do preparations'))
'Calling unstable function'
# [our unstable function raised an exception]
'cleaning up'
'waiting'
'do preparations'
'Calling unstable function'
# [our unstable function raised an exception]
'cleaning up'
Error: Exception raised...
```
