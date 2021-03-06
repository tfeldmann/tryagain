import mock
import pytest
import logging
import tryagain
import functools


class Namespace:
    pass


def _return_true():
    return True


def _raise_exception():
    raise Exception()


def test_call_once():
    assert tryagain.call(_return_true) is True


def test_call_twice():
    assert tryagain.call(_return_true, max_attempts=2) is True


def test_raise_after_retry():
    with pytest.raises(Exception):
        tryagain.call(_raise_exception, max_attempts=2)


def test_wait_time():

    def works_on_second_try():
        if ns.count == 0:
            ns.count = 1
            raise ValueError
        return True

    ns = Namespace()
    ns.count = 0

    with mock.patch('time.sleep') as mock_sleep:
        assert tryagain.call(works_on_second_try, wait=1.2) is True
        mock_sleep.assert_called_once_with(1.2)


def test_custom_wait_function():

    def mywait(attempt):
        ns.counter = attempt
        return 0

    ns = Namespace()
    ns.counter = 0
    with pytest.raises(Exception):
        tryagain.call(_raise_exception, wait=mywait, max_attempts=2)
    assert ns.counter == 1


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


def test_full_execution_decorator():
    ns = Namespace()
    actions = []
    ns.count = 0

    def cleanup():
        actions.append('cleanup %s' % ns.count)

    def pre_retry():
        actions.append('pre_retry %s' % ns.count)

    def wait(attempt):
        actions.append('wait %s' % attempt)
        return 0

    @tryagain.retries(wait=wait, max_attempts=5,
                      cleanup_hook=cleanup, pre_retry_hook=pre_retry)
    def unstable():
        ns.count += 1
        if ns.count == 3:
            actions.append('success %s' % ns.count)
            return 'result %s' % ns.count
        else:
            actions.append('fail %s' % ns.count)
            raise Exception

    result = unstable()
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

    class MyClass:

        def __init__(self):
            self.count = 0

        @tryagain.retries(max_attempts=5)
        def unstable(self, pass_on_count):
            self.count += 1
            if self.count == pass_on_count:
                return True
            else:
                raise Exception('Exception message')

    with pytest.raises(Exception):
        c1 = MyClass()
        c1.unstable(pass_on_count=10)

    c2 = MyClass()
    assert c2.unstable(pass_on_count=2) is True


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


def test_unexpected_exception():

    @tryagain.retries(max_attempts=5, exceptions=(TypeError, ValueError))
    def unstable():
        ns.count += 1
        raise EnvironmentError()

    ns = Namespace()
    ns.count = 0
    with pytest.raises(EnvironmentError):
        unstable()
    assert ns.count == 1


def test_multiple_exceptions():

    @tryagain.retries(exceptions=(ValueError, OSError))
    def unstable(pass_on_count=2):
        ns.count += 1
        if ns.count == 1:
            raise OSError
        elif ns.count < pass_on_count:
            raise ValueError
        else:
            return True

    ns = Namespace()
    ns.count = 0
    assert unstable(pass_on_count=5) is True


def test_exception_in_wait_function():

    def wait(attempt):
        raise ValueError('Exception in wait function')

    with pytest.raises(ValueError):
        tryagain.call(_raise_exception, wait=wait)


def test_exception_in_cleanup_hook():

    def cleanup():
        raise ValueError('Exception in cleanup')

    with pytest.raises(ValueError):
        tryagain.call(_raise_exception, cleanup_hook=cleanup)


def test_exception_in_pre_retry_hook():

    def pre_retry():
        raise ValueError('Exception in pre_retry hook')

    with pytest.raises(ValueError):
        tryagain.call(_raise_exception, pre_retry_hook=pre_retry)


def test_callable_hooks():
    def wait():
        # parameter 'attempt' is missing
        pass

    def pre_retry(too, many, arguments):
        pass

    def cleanup(too, many, arguments):
        pass

    with pytest.raises(TypeError):
        tryagain.call(_raise_exception, wait=wait)
    with pytest.raises(TypeError):
        tryagain.call(_raise_exception, pre_retry_hook=pre_retry)
    with pytest.raises(TypeError):
        tryagain.call(_raise_exception, cleanup_hook=cleanup)
