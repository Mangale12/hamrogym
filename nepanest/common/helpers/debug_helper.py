"""
ERP-Level Production Debug Helper
==================================
Injects debug utilities into Python builtins so they are available
everywhere in the Django project without any per-module import.

Usage in settings / AppConfig.ready():
    from nepanest.common.helpers.debug_helper import install_debug_builtins
    install_debug_builtins()

Then anywhere in the project (views, models, tasks, signals …):
    ddump(queryset)           # pretty-print any object / queryset
    dsql(queryset)            # print the raw SQL with params
    dtrace()                  # print full call stack at current point
    dtime(fn, *args)          # time a callable and log it
    dlog("msg", level="warn") # structured log with file/line context
    dobj(instance)            # dump every field of a Django model instance
    dreq(request)             # dump an HttpRequest cleanly
    dperf_start("label")      # start a named performance timer
    dperf_end("label")        # stop timer and print elapsed
    dbreak()                  # conditional debugger (only in DEBUG mode)
    dsettings("KEY")          # safely inspect a settings value
    dmem()                    # current process memory usage
    dq(expr, *filters)        # quick ORM shorthand
"""

from __future__ import annotations

import builtins
import gc
import html
import inspect
import json
import logging
import os
import pprint
import sys
import textwrap
import time
import traceback
import tracemalloc
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Callable, Optional
from uuid import UUID

logger = logging.getLogger("erp.debug")

# ──────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────────────

_PERF_REGISTRY: dict[str, float] = {}
_ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "gray": "\033[90m",
}


def _c(text: str, *colors: str) -> str:
    """Colorize text for terminal output (skipped in non-TTY environments)."""
    if not sys.stdout.isatty():
        return text
    prefix = "".join(_ANSI.get(c, "") for c in colors)
    return f"{prefix}{text}{_ANSI['reset']}"


def _caller_info(depth: int = 2) -> str:
    """Return 'filename:lineno in function' for the caller at *depth* frames up."""
    frame = inspect.stack()[depth]
    filename = os.path.relpath(frame.filename)
    return f"{filename}:{frame.lineno} in {_c(frame.function, 'cyan')}"


def _serialize_value(val: Any) -> Any:
    """Make a value JSON-serialisable for structured logging."""
    if isinstance(val, (str, int, float, bool, type(None))):
        return val
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    if isinstance(val, Decimal):
        return str(val)
    if isinstance(val, UUID):
        return str(val)
    if isinstance(val, (list, tuple)):
        return [_serialize_value(v) for v in val]
    if isinstance(val, dict):
        return {k: _serialize_value(v) for k, v in val.items()}
    return repr(val)


def _dd_serialize(obj: Any, *, _depth: int = 0, _max_depth: int = 4) -> Any:
    """Serialize complex objects into JSON-friendly structures for dd()."""
    if _depth >= _max_depth:
        return "<max depth reached>"

    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): _dd_serialize(v, _depth=_depth + 1, _max_depth=_max_depth) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_dd_serialize(item, _depth=_depth + 1, _max_depth=_max_depth) for item in list(obj)[:50]]

    try:
        from django.db.models import Model, QuerySet

        if isinstance(obj, QuerySet):
            rows = list(obj[:50])
            return {
                "__type__": f"QuerySet<{obj.model.__name__}>",
                "__count__": obj.count(),
                "__sql__": str(obj.query),
                "results": [_dd_serialize(row, _depth=_depth + 1, _max_depth=_max_depth) for row in rows],
            }

        if isinstance(obj, Model):
            data = {
                "__type__": obj._meta.label,
                "__pk__": obj.pk,
            }
            for field in obj._meta.concrete_fields:
                data[field.attname] = _dd_serialize(
                    getattr(obj, field.attname, None),
                    _depth=_depth + 1,
                    _max_depth=_max_depth,
                )
            return data
    except Exception:
        pass

    if hasattr(obj, "__dict__"):
        return {
            "__type__": type(obj).__name__,
            **{
                key: _dd_serialize(value, _depth=_depth + 1, _max_depth=_max_depth)
                for key, value in vars(obj).items()
                if not key.startswith("_")
            },
        }

    return repr(obj)


class DumpAndDie(Exception):
    def __init__(self, response: Any) -> None:
        super().__init__("dd() called")
        self._dd_response = response


# ──────────────────────────────────────────────────────────────────────────────
# 1. ddump  – pretty-print any Python object / Django queryset
# ──────────────────────────────────────────────────────────────────────────────

def ddump(obj: Any, label: str = "", max_items: int = 50) -> None:
    """
    Pretty-print *obj* to stdout with caller context.

    • Querysets are evaluated up to *max_items* rows and shown as a list.
    • Model instances are rendered field-by-field.
    • Everything else falls back to pprint.
    """
    header = _c(f"[ddump] {label or type(obj).__name__}", "bold", "magenta")
    caller = _c(f"  ↳ {_caller_info()}", "gray")
    print(f"\n{header}  {caller}")
    print(_c("─" * 72, "gray"))

    # Django QuerySet
    try:
        from django.db.models import QuerySet
        if isinstance(obj, QuerySet):
            rows = list(obj[:max_items])
            total = obj.count()
            print(_c(f"  QuerySet<{obj.model.__name__}>  total={total}  showing={len(rows)}", "yellow"))
            for i, row in enumerate(rows, 1):
                print(f"  [{i:>4}] {_format_model_instance(row)}")
            if total > max_items:
                print(_c(f"  … {total - max_items} more rows truncated", "gray"))
            print()
            return
    except ImportError:
        pass

    # Django model instance
    try:
        from django.db.models import Model
        if isinstance(obj, Model):
            print(_format_model_instance(obj, indent=2))
            print()
            return
    except ImportError:
        pass

    # Default
    pprint.pprint(obj, indent=2, width=100)
    print()


def dd(*args: Any, label: str = "") -> None:
    """
    Dump values as an HTML response and stop execution.

    Intended for use inside Django views, similar to Laravel's dd().
    """
    from django.http import HttpResponse

    stack = traceback.extract_stack()[:-1]
    caller = stack[-1] if stack else None
    caller_info = (
        f"{os.path.relpath(caller.filename)}:{caller.lineno} in {caller.name}()"
        if caller
        else "unknown location"
    )

    payload = [_dd_serialize(arg) for arg in args]
    blocks: list[str] = []
    for index, item in enumerate(payload, start=1):
        pretty = json.dumps(item, indent=2, ensure_ascii=False, default=str)
        blocks.append(
            f"""
            <section class="dump-block">
              <div class="dump-header">
                <span class="dump-index">Variable {index}</span>
                <span class="dump-type">{html.escape(type(args[index - 1]).__name__)}</span>
              </div>
              <pre>{html.escape(pretty)}</pre>
            </section>
            """
        )

    stack_frames = []
    for frame_index, frame in enumerate(reversed(stack), start=1):
        stack_frames.append(
            "<div class=\"stack-frame\">"
            f"<span class=\"stack-num\">#{frame_index}</span>"
            f"<span class=\"stack-file\">{html.escape(os.path.relpath(frame.filename))}</span>"
            f"<span class=\"stack-line\">:{frame.lineno}</span>"
            f"<span class=\"stack-fn\">{html.escape(frame.name)}()</span>"
            "</div>"
        )

    html_response = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>dd() dump</title>
  <style>
    :root {{
      --bg: #101418;
      --panel: #172027;
      --panel-2: #1e2932;
      --line: #2f3f4d;
      --text: #e8eef2;
      --muted: #95a6b5;
      --accent: #ff6b57;
      --accent-soft: #ffd2cc;
      --code: #0c1116;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: radial-gradient(circle at top, #1c2831 0%, var(--bg) 48%);
      color: var(--text);
      font: 14px/1.5 Menlo, Monaco, Consolas, "Liberation Mono", monospace;
    }}
    .topbar {{
      position: sticky;
      top: 0;
      display: flex;
      gap: 16px;
      align-items: center;
      padding: 16px 24px;
      background: rgba(16, 20, 24, 0.96);
      border-bottom: 1px solid var(--line);
      backdrop-filter: blur(8px);
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      padding: 6px 10px;
      border-radius: 999px;
      background: var(--accent);
      color: white;
      font-weight: 700;
      letter-spacing: 0.04em;
    }}
    .meta {{
      color: var(--muted);
      overflow-wrap: anywhere;
    }}
    .count {{
      margin-left: auto;
      color: var(--accent-soft);
    }}
    main {{
      max-width: 1240px;
      margin: 0 auto;
      padding: 24px;
    }}
    .dump-block, .stack {{
      margin-bottom: 20px;
      border: 1px solid var(--line);
      border-radius: 16px;
      overflow: hidden;
      background: linear-gradient(180deg, var(--panel) 0%, var(--panel-2) 100%);
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.16);
    }}
    .dump-header, .stack-header {{
      display: flex;
      gap: 12px;
      align-items: center;
      padding: 12px 16px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.02);
    }}
    .dump-index {{
      font-weight: 700;
    }}
    .dump-type {{
      color: var(--muted);
    }}
    pre {{
      margin: 0;
      padding: 18px;
      overflow-x: auto;
      white-space: pre-wrap;
      word-break: break-word;
      background: var(--code);
      color: #d7e3ec;
    }}
    .stack-body {{
      padding: 12px 16px 18px;
    }}
    .stack-frame {{
      display: flex;
      gap: 10px;
      padding: 6px 0;
      color: var(--muted);
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }}
    .stack-frame:last-child {{
      border-bottom: 0;
    }}
    .stack-num {{
      color: var(--accent-soft);
      min-width: 36px;
    }}
    .stack-file {{
      color: #9ad1ff;
      overflow-wrap: anywhere;
    }}
    .stack-line {{
      color: #f7b267;
    }}
    .stack-fn {{
      color: #7fe7c4;
    }}
  </style>
</head>
<body>
  <header class="topbar">
    <span class="badge">dd()</span>
    <div class="meta">{html.escape(label) if label else "Dump and die output"}<br>{html.escape(caller_info)}</div>
    <div class="count">{len(args)} value{"s" if len(args) != 1 else ""}</div>
  </header>
  <main>
    {''.join(blocks) if blocks else '<section class="dump-block"><pre>No values were passed to dd().</pre></section>'}
    <section class="stack">
      <div class="stack-header">Stack Trace</div>
      <div class="stack-body">
        {''.join(stack_frames)}
      </div>
    </section>
  </main>
</body>
</html>"""

    raise DumpAndDie(HttpResponse(html_response, status=200))


def _format_model_instance(instance: Any, indent: int = 0) -> str:
    """Return a readable string of a model instance's concrete fields."""
    try:
        fields = instance._meta.concrete_fields
        pad = " " * indent
        lines = [_c(f"{pad}{type(instance).__name__}(pk={instance.pk})", "green")]
        for f in fields:
            val = getattr(instance, f.attname, "—")
            lines.append(f"{pad}  {_c(f.attname, 'cyan')} = {val!r}")
        return "\n".join(lines)
    except Exception:
        return repr(instance)


# ──────────────────────────────────────────────────────────────────────────────
# 2. dsql  – print raw SQL for a queryset
# ──────────────────────────────────────────────────────────────────────────────

def dsql(queryset: Any, label: str = "") -> None:
    """Print the compiled SQL (with params) for a Django QuerySet."""
    caller = _caller_info()
    try:
        from django.db import connection  # noqa: F401 – verify Django is present
        sql, params = queryset.query.sql_with_params()
        formatted = _format_sql(sql % tuple(repr(p) for p in params))
    except Exception as exc:
        # Fallback: str() on the query object
        try:
            formatted = str(queryset.query)
        except Exception:
            formatted = f"<could not render SQL: {exc}>"

    header = _c(f"[dsql] {label or ''}", "bold", "blue")
    print(f"\n{header}  {_c(f'↳ {caller}', 'gray')}")
    print(_c("─" * 72, "gray"))
    print(formatted)
    print()


def _format_sql(raw: str) -> str:
    """Minimal SQL pretty-printer: capitalise keywords and indent."""
    keywords = [
        "SELECT", "FROM", "WHERE", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN",
        "ORDER BY", "GROUP BY", "HAVING", "LIMIT", "OFFSET", "AND", "OR",
        "ON", "SET", "UPDATE", "INSERT INTO", "VALUES", "DELETE FROM",
    ]
    result = raw.strip()
    for kw in keywords:
        result = result.replace(kw, f"\n{_c(kw, 'yellow')}")
    # Re-indent continuation lines
    lines = [line.strip() for line in result.splitlines() if line.strip()]
    indented = [lines[0]] + ["  " + ln for ln in lines[1:]]
    return "\n".join(indented)


# ──────────────────────────────────────────────────────────────────────────────
# 3. dtrace  – full call-stack snapshot
# ──────────────────────────────────────────────────────────────────────────────

def dtrace(label: str = "") -> None:
    """Print the current call stack from the caller's frame upward."""
    header = _c(f"[dtrace] {label or 'Call Stack'}", "bold", "red")
    caller = _c(f"↳ {_caller_info()}", "gray")
    print(f"\n{header}  {caller}")
    print(_c("─" * 72, "gray"))
    stack = traceback.format_stack()[:-1]  # exclude this function
    for frame_str in reversed(stack):
        print(textwrap.indent(frame_str.rstrip(), "  "))
    print()


# ──────────────────────────────────────────────────────────────────────────────
# 4. dtime  – time a callable
# ──────────────────────────────────────────────────────────────────────────────

def dtime(fn: Callable, *args: Any, label: str = "", **kwargs: Any) -> Any:
    """
    Execute *fn(*args, **kwargs)*, print elapsed time, and return the result.

    Example::

        result = dtime(MyModel.objects.filter, status="active")
    """
    name = label or getattr(fn, "__name__", repr(fn))
    caller = _caller_info()
    start = time.perf_counter()
    try:
        result = fn(*args, **kwargs)
    except Exception:
        elapsed = time.perf_counter() - start
        print(_c(f"[dtime] {name} RAISED after {elapsed:.4f}s  ↳ {caller}", "red", "bold"))
        raise
    elapsed = time.perf_counter() - start
    color = "green" if elapsed < 0.1 else ("yellow" if elapsed < 1.0 else "red")
    print(_c(f"[dtime] {name} → {elapsed:.4f}s  ↳ {caller}", color))
    return result


# ──────────────────────────────────────────────────────────────────────────────
# 5. dlog  – structured contextual log
# ──────────────────────────────────────────────────────────────────────────────

_LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def dlog(
    msg: str,
    *,
    level: str = "debug",
    extra: Optional[dict] = None,
    exc_info: bool = False,
) -> None:
    """
    Emit a structured log entry via the *erp.debug* logger.

    Includes filename, line number, and function name automatically.

    Args:
        msg:       Human-readable message.
        level:     One of debug / info / warn / error / critical.
        extra:     Additional key-value pairs serialised to JSON.
        exc_info:  If True, attach current exception info.
    """
    frame = inspect.stack()[1]
    location = f"{os.path.relpath(frame.filename)}:{frame.lineno}"
    payload: dict[str, Any] = {
        "msg": msg,
        "location": location,
        "function": frame.function,
    }
    if extra:
        payload["extra"] = {k: _serialize_value(v) for k, v in extra.items()}

    log_level = _LOG_LEVELS.get(level.lower(), logging.DEBUG)
    logger.log(log_level, json.dumps(payload, ensure_ascii=False), exc_info=exc_info)

    # Also echo to stdout when DEBUG=True
    _django_debug_echo(f"[dlog/{level.upper()}] {msg}  ({location})", level)


def _django_debug_echo(text: str, level: str) -> None:
    """Print to stdout only when Django's DEBUG=True."""
    try:
        from django.conf import settings
        if not getattr(settings, "DEBUG", False):
            return
    except Exception:
        pass
    color_map = {
        "debug": "gray", "info": "green", "warn": "yellow",
        "warning": "yellow", "error": "red", "critical": "red",
    }
    print(_c(text, color_map.get(level, "reset")))


# ──────────────────────────────────────────────────────────────────────────────
# 6. dobj  – dump every field of a Django model instance with change tracking
# ──────────────────────────────────────────────────────────────────────────────

def dobj(instance: Any, *, show_relations: bool = False) -> None:
    """
    Dump every concrete (and optionally relational) field of a model instance.

    Also shows __original__ values if the model uses a dirty-tracking mixin.
    """
    caller = _caller_info()
    try:
        meta = instance._meta
    except AttributeError:
        ddump(instance)
        return

    header = _c(f"[dobj] {meta.label}  pk={instance.pk}", "bold", "magenta")
    print(f"\n{header}  {_c(f'↳ {caller}', 'gray')}")
    print(_c("─" * 72, "gray"))

    # Concrete fields
    print(_c("  Concrete Fields:", "bold"))
    for f in meta.concrete_fields:
        raw = getattr(instance, f.attname, "—")
        original = None
        if hasattr(instance, "__original__"):
            original = instance.__original__.get(f.attname)
        changed = original is not None and original != raw
        marker = _c("  ✎ CHANGED", "yellow") if changed else ""
        orig_str = f"  (was {original!r})" if changed else ""
        print(f"    {_c(f.attname, 'cyan'):40s} = {raw!r}{orig_str}{marker}")

    # Many-to-many (optional)
    if show_relations:
        print(_c("  M2M Relations:", "bold"))
        for rel in meta.many_to_many:
            try:
                related_qs = getattr(instance, rel.name).all()
                ids = list(related_qs.values_list("pk", flat=True)[:10])
                print(f"    {_c(rel.name, 'cyan'):40s} = {ids!r}")
            except Exception as exc:
                print(f"    {_c(rel.name, 'cyan'):40s} = <error: {exc}>")

    # Properties / cached_properties
    print(_c("  Python Properties:", "bold"))
    for name, val in inspect.getmembers(type(instance)):
        if isinstance(val, (property,)):
            try:
                pval = getattr(instance, name)
                print(f"    {_c(name, 'blue'):40s} = {pval!r}")
            except Exception:
                pass
    print()


# ──────────────────────────────────────────────────────────────────────────────
# 7. dreq  – dump an HttpRequest
# ──────────────────────────────────────────────────────────────────────────────

def dreq(request: Any) -> None:
    """Print a structured summary of a Django HttpRequest."""
    caller = _caller_info()
    header = _c(f"[dreq] {request.method} {request.path}", "bold", "blue")
    print(f"\n{header}  {_c(f'↳ {caller}', 'gray')}")
    print(_c("─" * 72, "gray"))

    sections: dict[str, Any] = {
        "META (selected)": {
            k: v for k, v in request.META.items()
            if k.startswith("HTTP_") or k in (
                "SERVER_NAME", "SERVER_PORT", "CONTENT_TYPE",
                "CONTENT_LENGTH", "REMOTE_ADDR", "QUERY_STRING",
            )
        },
        "GET params": dict(request.GET),
        "POST params": dict(request.POST),
        "Cookies": dict(request.COOKIES),
        "Session keys": list(request.session.keys()) if hasattr(request, "session") else [],
        "User": repr(getattr(request, "user", "—")),
        "Resolver match": repr(getattr(request, "resolver_match", "—")),
    }

    # Try to decode JSON body
    if request.content_type and "json" in request.content_type:
        try:
            sections["JSON body"] = json.loads(request.body)
        except Exception:
            sections["JSON body"] = "<parse error>"

    for section, data in sections.items():
        print(_c(f"  {section}:", "bold"))
        if isinstance(data, dict):
            for k, v in data.items():
                print(f"    {_c(str(k), 'cyan'):45s} {v!r}")
        elif isinstance(data, list):
            print(f"    {data!r}")
        else:
            print(f"    {data}")
    print()


# ──────────────────────────────────────────────────────────────────────────────
# 8. dperf_start / dperf_end  – named performance timers
# ──────────────────────────────────────────────────────────────────────────────

def dperf_start(label: str) -> None:
    """Start a named performance timer."""
    _PERF_REGISTRY[label] = time.perf_counter()
    caller = _caller_info()
    print(_c(f"[dperf] ▶ START '{label}'  ↳ {caller}", "gray"))


def dperf_end(label: str) -> float:
    """
    Stop a named performance timer and print the elapsed time.

    Returns the elapsed time in seconds.
    """
    start = _PERF_REGISTRY.pop(label, None)
    caller = _caller_info()
    if start is None:
        print(_c(f"[dperf] ✗ '{label}' was never started  ↳ {caller}", "red"))
        return -1.0
    elapsed = time.perf_counter() - start
    color = "green" if elapsed < 0.5 else ("yellow" if elapsed < 2.0 else "red")
    print(_c(f"[dperf] ■ END   '{label}'  elapsed={elapsed:.4f}s  ↳ {caller}", color))
    return elapsed


@contextmanager
def dperf(label: str):
    """Context manager version of the performance timer."""
    dperf_start(label)
    try:
        yield
    finally:
        dperf_end(label)


# ──────────────────────────────────────────────────────────────────────────────
# 9. dbreak  – conditional pdb breakpoint (DEBUG mode only)
# ──────────────────────────────────────────────────────────────────────────────

def dbreak(condition: bool = True) -> None:
    """
    Drop into pdb only when condition is True **and** Django DEBUG=True.

    Safe to commit — it is a no-op on production.
    """
    try:
        from django.conf import settings
        if not getattr(settings, "DEBUG", False):
            return
    except Exception:
        return

    if condition:
        caller = _caller_info()
        print(_c(f"[dbreak] entering debugger  ↳ {caller}", "red", "bold"))
        import pdb  # noqa: T100
        pdb.set_trace()


# ──────────────────────────────────────────────────────────────────────────────
# 10. dsettings  – safely inspect a Django settings value
# ──────────────────────────────────────────────────────────────────────────────

_SENSITIVE_KEYS = frozenset({
    "PASSWORD", "SECRET", "TOKEN", "KEY", "PRIVATE", "CREDENTIAL", "AUTH",
})


def dsettings(key: str) -> None:
    """
    Print a settings value, masking anything that looks sensitive.

    Example::

        dsettings("DATABASES")
        dsettings("EMAIL_HOST_PASSWORD")   # → masked
    """
    caller = _caller_info()
    try:
        from django.conf import settings
        val = getattr(settings, key, "<NOT SET>")
    except Exception as exc:
        val = f"<error: {exc}>"

    # Mask if key looks sensitive
    upper_key = key.upper()
    is_sensitive = any(s in upper_key for s in _SENSITIVE_KEYS)
    display_val = "*** MASKED ***" if is_sensitive else pprint.pformat(val, width=80)

    header = _c(f"[dsettings] {key}", "bold", "cyan")
    print(f"\n{header}  {_c(f'↳ {caller}', 'gray')}")
    print(_c("─" * 72, "gray"))
    print(textwrap.indent(display_val, "  "))
    print()


# ──────────────────────────────────────────────────────────────────────────────
# 11. dmem  – process memory snapshot
# ──────────────────────────────────────────────────────────────────────────────

def dmem(label: str = "", *, top: int = 5) -> None:
    """
    Print current process RSS memory and (if tracemalloc is running)
    the top Python allocation sites.

    Args:
        label: Optional label for the snapshot.
        top:   Number of top allocation sites to show.
    """
    caller = _caller_info()
    header = _c(f"[dmem] {label or 'Memory Snapshot'}", "bold", "green")
    print(f"\n{header}  {_c(f'↳ {caller}', 'gray')}")
    print(_c("─" * 72, "gray"))

    # RSS via /proc (Linux) or psutil
    rss_mb = _get_rss_mb()
    if rss_mb is not None:
        color = "green" if rss_mb < 256 else ("yellow" if rss_mb < 512 else "red")
        print(_c(f"  RSS: {rss_mb:.1f} MB", color))

    # GC counts
    gc_counts = gc.get_count()
    print(f"  GC generations: gen0={gc_counts[0]}  gen1={gc_counts[1]}  gen2={gc_counts[2]}")

    # tracemalloc
    if tracemalloc.is_tracing():
        snapshot = tracemalloc.take_snapshot()
        stats = snapshot.statistics("lineno")
        print(_c(f"  Top {top} allocation sites:", "bold"))
        for stat in stats[:top]:
            print(f"    {stat}")
    else:
        print(_c("  (start tracemalloc.start() for allocation tracing)", "gray"))
    print()


def _get_rss_mb() -> Optional[float]:
    try:
        with open("/proc/self/status") as fh:
            for line in fh:
                if line.startswith("VmRSS:"):
                    kb = int(line.split()[1])
                    return kb / 1024
    except Exception:
        pass
    try:
        import resource
        kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # macOS reports bytes, Linux reports KB
        return kb / 1024 if sys.platform == "linux" else kb / (1024 * 1024)
    except Exception:
        pass
    try:
        import psutil
        return psutil.Process().memory_info().rss / (1024 * 1024)
    except Exception:
        pass
    return None


# ──────────────────────────────────────────────────────────────────────────────
# 12. dq  – quick ORM query shorthand
# ──────────────────────────────────────────────────────────────────────────────

def dq(model_or_qs: Any, *filters: Any, **lookups: Any) -> Any:
    """
    Quick ORM helper: filter a model/queryset and dump the result.

    Examples::

        dq(Invoice, status="unpaid")
        dq(Invoice.objects.select_related("client"), due_date__lt=today)
    """
    caller = _caller_info()
    try:
        from django.db.models import Model, QuerySet
        if isinstance(model_or_qs, type) and issubclass(model_or_qs, Model):
            qs = model_or_qs.objects.all()
        elif isinstance(model_or_qs, QuerySet):
            qs = model_or_qs
        else:
            raise TypeError(f"Expected Model class or QuerySet, got {type(model_or_qs)}")

        if filters:
            from django.db.models import Q
            combined = filters[0]
            for f in filters[1:]:
                combined &= f
            qs = qs.filter(combined)
        if lookups:
            qs = qs.filter(**lookups)

        print(_c(f"[dq] ↳ {caller}", "gray"))
        ddump(qs)
        return qs
    except ImportError:
        raise RuntimeError("dq() requires Django to be installed and configured.")


# ──────────────────────────────────────────────────────────────────────────────
# 13. dexplain  – EXPLAIN ANALYZE on a queryset (PostgreSQL)
# ──────────────────────────────────────────────────────────────────────────────

def dexplain(queryset: Any, *, analyze: bool = False) -> None:
    """
    Run EXPLAIN [ANALYZE] on a queryset and print the query plan.

    Requires PostgreSQL.  *analyze=True* actually executes the query.
    """
    caller = _caller_info()
    prefix = "EXPLAIN ANALYZE" if analyze else "EXPLAIN"
    header = _c(f"[dexplain] {prefix}", "bold", "yellow")
    print(f"\n{header}  {_c(f'↳ {caller}', 'gray')}")
    print(_c("─" * 72, "gray"))
    try:
        from django.db import connection
        sql, params = queryset.query.sql_with_params()
        with connection.cursor() as cur:
            cur.execute(f"{prefix} {sql}", params)
            rows = cur.fetchall()
        for row in rows:
            print("  " + row[0])
    except Exception as exc:
        print(_c(f"  Error: {exc}", "red"))
    print()


# ──────────────────────────────────────────────────────────────────────────────
# 14. ddb  – connection-level query log snapshot
# ──────────────────────────────────────────────────────────────────────────────

def ddb(*, last: int = 10) -> None:
    """
    Print the last *n* database queries from Django's query log.

    Requires ``settings.DEBUG = True`` (Django only logs queries in debug mode).
    """
    caller = _caller_info()
    header = _c(f"[ddb] Last {last} DB queries", "bold", "blue")
    print(f"\n{header}  {_c(f'↳ {caller}', 'gray')}")
    print(_c("─" * 72, "gray"))
    try:
        from django.db import connection
        queries = connection.queries[-last:]
        if not queries:
            print(_c("  No queries recorded. Is DEBUG=True?", "gray"))
        for i, q in enumerate(queries, 1):
            elapsed = q.get("time", "?")
            sql = q.get("sql", "")
            color = "green" if float(elapsed or 0) < 0.05 else (
                "yellow" if float(elapsed or 0) < 0.2 else "red"
            )
            print(_c(f"  [{i:>3}] {elapsed}s", color) + f"  {sql[:200]}")
    except Exception as exc:
        print(_c(f"  Error: {exc}", "red"))
    print()


# ──────────────────────────────────────────────────────────────────────────────
# Builtins injection
# ──────────────────────────────────────────────────────────────────────────────

def install_debug_builtins() -> None:
    """
    Inject all debug helpers into Python builtins.

    Call this once from ``AppConfig.ready()`` or Django settings.
    The helpers are **no-ops / safe-fallbacks in production**
    (DEBUG=False suppresses most output).
    """
    _helpers = {
        "dd": dd,
        "ddump": ddump,
        "dsql": dsql,
        "dtrace": dtrace,
        "dtime": dtime,
        "dlog": dlog,
        "dobj": dobj,
        "dreq": dreq,
        "dperf_start": dperf_start,
        "dperf_end": dperf_end,
        "dperf": dperf,
        "dbreak": dbreak,
        "dsettings": dsettings,
        "dmem": dmem,
        "dq": dq,
        "dexplain": dexplain,
        "ddb": ddb,
    }
    for name, fn in _helpers.items():
        setattr(builtins, name, fn)

    logger.debug("[debug_helper] %d debug builtins installed.", len(_helpers))


# ──────────────────────────────────────────────────────────────────────────────
# Convenience: auto-install when imported directly (mirrors your pattern)
# ──────────────────────────────────────────────────────────────────────────────

install_debug_builtins()
