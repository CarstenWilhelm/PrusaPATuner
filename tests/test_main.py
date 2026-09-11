import signal
from unittest.mock import Mock

from prusa_pa_tuner import __main__ as cli


def test_console_close_raises_sigint_and_waits_for_shutdown(monkeypatch):
    raised = []
    shutdown_complete = Mock()

    monkeypatch.setattr(cli.signal, "raise_signal", raised.append)

    assert not cli._handle_console_event(0, shutdown_complete)
    assert cli._handle_console_event(cli._CTRL_CLOSE_EVENT, shutdown_complete)

    assert raised == [signal.SIGINT]
    shutdown_complete.wait.assert_called_once_with(timeout=cli._CLOSE_SHUTDOWN_TIMEOUT_S)
