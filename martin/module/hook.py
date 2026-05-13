"""Martin Module — Hook/Extension system.

Allows modules to register hooks that other modules can extend.

Usage:
    from martin.module.hook import register_hook, resolve_hooks

    # Module A declares a hook point:
    register_hook("contacts.form_fields", default=[...])

    # Module B extends it:
    register_hook("contacts.form_fields", my_field_fn, priority=20, module="crm")
"""

from __future__ import annotations

from typing import Any, Callable

_HOOKS: dict[str, list[dict[str, Any]]] = {}


def register_hook(
    name: str,
    fn: Callable | None = None,
    *,
    priority: int = 50,
    module: str = "",
    default: Any = None,
) -> None:
    """Register a hook or declare a hook point.

    Args:
        name: Hook identifier, e.g. "contacts.form_fields"
        fn: Callback. Receives (widget_instance, context) returns rendered HTML.
        priority: Lower = runs first. Default 50.
        module: Source module name.
        default: Default value for hook point declaration.
    """
    if name not in _HOOKS:
        _HOOKS[name] = []

    entry: dict[str, Any] = {
        "fn": fn,
        "priority": int(priority),
        "module": str(module or ""),
    }
    if default is not None:
        entry["default"] = default

    if fn is not None:
        _HOOKS[name].append(entry)
        # Keep sorted by priority
        _HOOKS[name].sort(key=lambda x: x["priority"])


def resolve_hooks(name: str, context: dict | None = None) -> list[Any]:
    """Resolve a hook: return sorted list of contributions.

    Args:
        name: Hook identifier.
        context: Optional dict passed to each callback.

    Returns:
        List of results from each hook callback (or defaults).
    """
    entries = _HOOKS.get(name, [])
    if not entries:
        return []

    results = []
    for entry in entries:
        fn = entry.get("fn")
        if fn is None:
            results.append(entry.get("default"))
        elif callable(fn):
            try:
                result = fn(context or {})
                results.append(result)
            except Exception as exc:
                import traceback
                traceback.print_exc()
                results.append(None)
        else:
            results.append(fn)
    return results


def clear_hooks(name: str | None = None) -> None:
    """Clear hooks. Used in tests."""
    if name:
        _HOOKS.pop(name, None)
    else:
        _HOOKS.clear()


def list_hooks() -> dict[str, list[dict[str, Any]]]:
    """Return all registered hooks (for introspection)."""
    return dict(_HOOKS)


def has_hooks(name: str) -> bool:
    """Check if a hook has any registrations."""
    return name in _HOOKS and bool(_HOOKS[name])


def extend(hook_name: str, *, priority: int = 50, module: str = ""):
    """Decorator: register a function as a hook contribution.

    Usage:
        @extend("ResourceForm.form_fields", module="crm")
        def add_source(context):
            return Select(name="source", ...)
    """
    def decorator(fn):
        register_hook(hook_name, fn, priority=priority, module=module)
        return fn
    return decorator
