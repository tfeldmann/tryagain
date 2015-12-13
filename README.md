# tryagain
A python retry helper.

<!-- MarkdownTOC -->

- [Quickstart][quickstart]

<!-- /MarkdownTOC -->


## Quickstart

### Retry calling an unstable function
```python
from tryagain import retry_call

def unstable():
    ...

retry_call(unstable, max_attempts=3)
```

### Retry a function call with parameters


### Waittimes


### Custom waittimes


### Function decorator
```python
from tryagain import retry

@retry(max_attempts=3)
def unstable():
```

### Hooks
