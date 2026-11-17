"""Importing an unprotected .knxproj with KNX Secure data offers to keep the keys in the clear."""

import threading
from types import MethodType, SimpleNamespace
from unittest.mock import Mock

from editor_gui import main
from editor_gui.widgets.password_form import NewPasswordForm


def _app() -> SimpleNamespace:
    finished = threading.Thread(target=lambda: None)  # not started: is_alive() is False
    app = SimpleNamespace(
        _import_thread=finished,
        _progress_running=True,
        _import_needs_project_password=True,
        _new_password_form=NewPasswordForm(),
        _log=Mock(),
    )
    app._start_import = Mock()
    app._clear_import_prompt = Mock()
    # The modal request is the real method; only the import dispatch is mocked.
    app._request_new_password = MethodType(main.KnxGuiApp._request_new_password, app)
    return app


def test_import_secure_data_offers_without_password() -> None:
    app = _app()
    app._import_pw = "archive-pw"

    main.KnxGuiApp._poll_import(app)

    assert app._import_thread is None
    assert app._progress_running is False
    assert app._new_password_requested
    assert app._new_password_action is not None
    assert callable(app._new_password_cancel)
    without = app._new_password_without
    assert callable(without)
    # "Without Password" re-imports with the archive password but no project password.
    without()
    app._start_import.assert_called_once_with("archive-pw", None, True)


def test_import_secure_data_action_and_cancel_unchanged() -> None:
    app = _app()
    app._import_pw = None

    main.KnxGuiApp._poll_import(app)

    action, cancel, without = (
        app._new_password_action,
        app._new_password_cancel,
        app._new_password_without,
    )
    action("chosen")
    app._start_import.assert_called_once_with(None, "chosen")
    assert callable(cancel) and callable(without)
