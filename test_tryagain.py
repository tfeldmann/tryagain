import pytest
import tryagain


counter = 0


def _return_true():
    return True


def _always_raise_exception():
    raise Exception()


def _reset_counter():
    global counter
    counter = 0


def test_call_once():
    tryagain.call(_return_true)


def test_call_twice():
    tryagain.call(_return_true, max_attempts=2)


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
        tryagain.call(_always_raise_exception, wait=mywait, max_attempts=2)
    assert counter == 1


def test_detect_invalid_wait_function():
    with pytest.raises(ValueError):
        tryagain.call(_return_true, wait=lambda too, many, arguments: None)


def test_detect_invalid_cleanup_hook():
    with pytest.raises(ValueError):
        tryagain.call(_return_true, cleanup_hook=lambda somearg: None)


def test_detect_invalid_pre_retry_hook():
    with pytest.raises(ValueError):
        tryagain.call(_return_true, pre_retry_hook=lambda somearg: None)
