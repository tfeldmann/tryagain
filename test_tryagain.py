import mock
import pytest
import logging
import tryagain
import functools

# TODO: test with uncallable hooks, function and wait func

counter = 0


def _return_true():
    return True


def _always_raise_exception():
    raise Exception()


def _reset_counter():
    global counter
    counter = 0


def test_call_once():
    assert tryagain.call(_return_true) is True


def test_call_twice():
    assert tryagain.call(_return_true, max_attempts=2) is True


def test_raise_after_retry():
    with pytest.raises(Exception):
        tryagain.call(_always_raise_exception, max_attempts=2)


def test_custom_wait_function():
    def mywait(attempt):
        global counter
        counter = attempt
        return 0

    _reset_counter()
    with pytest.raises(Exception):
        assert tryagain.call(
            _always_raise_exception, wait=mywait, max_attempts=2) is None
    assert counter == 1


def test_repeat():
    assert (
        list(tryagain._repeat('x', times=10)) ==
        ['x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x', 'x'])


def test_is_callable():
    with pytest.raises(TypeError):
        tryagain._assert_callable(None, allow_none=False)
    with pytest.raises(TypeError):
        tryagain._assert_callable(3, allow_none=True)
    assert tryagain._assert_callable(_return_true) is None
    assert tryagain._assert_callable(lambda: None) is None


def test_attempts():
    with pytest.raises(ValueError):
        tryagain.call(_return_true, max_attempts=0)
    assert tryagain.call(_return_true, max_attempts=None)
    assert tryagain.call(_return_true, max_attempts=1)


def test_unexpected_exception():
    pass


class Namespace:
    pass


def test_full_execution():
    ns = Namespace()
    actions = []
    ns.count = 0

    def unstable():
        ns.count += 1
        if ns.count == 3:
            actions.append('success %s' % ns.count)
            return 'result %s' % ns.count
        else:
            actions.append('fail %s' % ns.count)
            raise Exception

    def cleanup():
        actions.append('cleanup %s' % ns.count)

    def pre_retry():
        actions.append('pre_retry %s' % ns.count)

    def wait(attempt):
        actions.append('wait %s' % attempt)
        return 0

    result = tryagain.call(unstable, wait=wait, max_attempts=5,
                           cleanup_hook=cleanup, pre_retry_hook=pre_retry)
    print(actions)
    assert actions == [
        'fail 1', 'cleanup 1', 'wait 1', 'pre_retry 1',
        'fail 2', 'cleanup 2', 'wait 2', 'pre_retry 2',
        'success 3']
    assert result == 'result 3'


class reprwrapper(object):
    def __init__(self, repr, func):
        self._repr = repr
        self._func = func
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kw):
        return self._func(*args, **kw)

    def __repr__(self):
        return self._repr


def test_logging():
    ns = Namespace()
    ns.count = 0

    def unstable():
        ns.count += 1
        if ns.count == 2:
            return True
        else:
            raise Exception('Exception message')

    wrapped_unstable = reprwrapper('unstable', unstable)

    logger = logging.getLogger('tryagain')
    with mock.patch.object(logger, 'debug') as mock_debug:
        assert tryagain.call(wrapped_unstable) is True
        mock_debug.assert_called_once_with(
           'Attempt 1 at calling unstable failed (Exception message)')


def test_logging_limited_attempts():
    ns = Namespace()
    ns.count = 0

    def unstable():
        ns.count += 1
        if ns.count == 2:
            return True
        else:
            raise Exception('Exception message')

    wrapped_unstable = reprwrapper('unstable', unstable)

    logger = logging.getLogger('tryagain')
    with mock.patch.object(logger, 'debug') as mock_debug:
        assert tryagain.call(wrapped_unstable, max_attempts=5) is True
        mock_debug.assert_called_once_with(
           'Attempt 1 / 5 at calling unstable failed (Exception message)')


def test_decorator():
    ns = Namespace()
    ns.count = 0

    @tryagain.retries()
    def unstable():
        ns.count += 1
        if ns.count == 2:
            return True
        else:
            raise Exception('Exception message')

    assert tryagain.call(unstable)


def test_decorator_with_parameters():
    ns = Namespace()
    ns.count = 0

    @tryagain.retries(max_attempts=5)
    def unstable():
        ns.count += 1
        if ns.count == 2:
            return True
        else:
            raise Exception('Exception message')

    assert tryagain.call(unstable)


def test_decorator_in_class():
    pass


def test_decorator_hooks():
    pass


def test_decorator_fails():
    ns = Namespace()
    ns.count = 0

    @tryagain.retries(max_attempts=5)
    def unstable(pass_on_count=2):
        ns.count += 1
        if ns.count == pass_on_count:
            return True
        else:
            raise Exception('Exception message')

    with pytest.raises(Exception):
        unstable(pass_on_count=10)

    ns.count = 0
    assert unstable(pass_on_count=2) is True
