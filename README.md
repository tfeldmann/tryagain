# tryagain
A python retry helper.

<!-- MarkdownTOC -->

- [Quickstart][quickstart]
    - [Retry calling an unstable function][retry-calling-an-unstable-function]
    - [Retry a function call with parameters][retry-a-function-call-with-parameters]
    - [Waittimes][waittimes]
    - [Custom waittimes][custom-waittimes]
    - [Function decorator][function-decorator]
    - [Hooks][hooks]

<!-- /MarkdownTOC -->


<a name="quickstart"></a>
## Quickstart

<a name="retry-calling-an-unstable-function"></a>
### Retry calling an unstable function
```python
from tryagain import retry_call

def unstable():
    ...

retry_call(unstable, max_attempts=3)
```

<a name="retry-a-function-call-with-parameters"></a>
### Retry a function call with parameters


<a name="waittimes"></a>
### Waittimes


<a name="custom-waittimes"></a>
### Custom waittimes


<a name="function-decorator"></a>
### Function decorator
```python
from tryagain import retry

@retry(max_attempts=3)
def unstable():
```

<a name="hooks"></a>
### Hooks
