"""Contexto runtime para render de página actual."""

from contextvars import ContextVar


_CURRENT_PATH = ContextVar("martin_current_path", default="/")


def get_current_path():
    return _CURRENT_PATH.get()


def set_current_path(path):
    return _CURRENT_PATH.set(path or "/")


def reset_current_path(token):
    _CURRENT_PATH.reset(token)
