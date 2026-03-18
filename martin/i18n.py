"""
Martin i18n/l10n helpers.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None


class I18n:
    """
    Dot-key translator with interpolation.
    """

    def __init__(
        self,
        messages: Dict[str, Dict[str, Any]] | None = None,
        default_locale: str = "es",
        fallback_locale: str = "en",
    ):
        self.messages = messages or {}
        self.default_locale = str(default_locale or "es")
        self.fallback_locale = str(fallback_locale or "en")
        self.locale = self.default_locale

    def use(self, locale: str):
        self.locale = str(locale or self.default_locale)
        return self

    @staticmethod
    def _deep_get(data: Dict[str, Any], key: str):
        cur: Any = data
        for part in str(key).split("."):
            if isinstance(cur, dict) and part in cur:
                cur = cur[part]
            else:
                return None
        return cur

    def t(self, key: str, locale: str | None = None, default: str | None = None, **vars):
        loc = locale or self.locale or self.default_locale
        text = self._deep_get(self.messages.get(loc, {}), key)
        if text is None and self.fallback_locale:
            text = self._deep_get(self.messages.get(self.fallback_locale, {}), key)
        if text is None:
            text = self._deep_get(self.messages.get(self.default_locale, {}), key)
        if text is None:
            text = default if default is not None else key
        out = str(text)
        if vars:
            try:
                out = out.format(**vars)
            except Exception:
                pass
        return out


class L10n:
    """
    Lightweight localization helpers (locale, timezone, currency, RTL).
    """

    _RTL_PREFIXES = ("ar", "he", "fa", "ur", "ps", "dv")

    _CURRENCY_SYMBOL = {
        "USD": "$",
        "EUR": "EUR ",
        "GBP": "GBP ",
        "JPY": "JPY ",
        "COP": "COP ",
        "MXN": "MXN ",
        "PEN": "PEN ",
    }

    def __init__(self, locale: str = "es-EC", timezone: str = "UTC", currency: str = "USD"):
        self.locale = locale
        self.timezone = timezone
        self.currency = currency.upper()

    def is_rtl(self, locale: str | None = None) -> bool:
        loc = (locale or self.locale or "").lower().replace("_", "-")
        return loc.startswith(self._RTL_PREFIXES)

    def text_direction(self, locale: str | None = None) -> str:
        return "rtl" if self.is_rtl(locale) else "ltr"

    def to_timezone(self, dt: datetime, timezone: str | None = None) -> datetime:
        tzname = timezone or self.timezone
        if ZoneInfo is None:
            return dt
        try:
            tz = ZoneInfo(tzname)
        except Exception:
            return dt
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        return dt.astimezone(tz)

    @staticmethod
    def _to_decimal(value: Any) -> Decimal:
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError):
            return Decimal("0")

    def format_number(self, value: Any, decimals: int = 0, locale: str | None = None) -> str:
        loc = (locale or self.locale or "en-US").lower()
        d = self._to_decimal(value)
        fmt = f"{{:,.{max(0, int(decimals))}f}}"
        out = fmt.format(float(d))
        if loc.startswith("es") or loc.startswith("fr") or loc.startswith("de") or loc.startswith("it"):
            out = out.replace(",", "X").replace(".", ",").replace("X", ".")
        return out

    def format_currency(
        self,
        value: Any,
        currency: str | None = None,
        decimals: int = 2,
        locale: str | None = None,
    ) -> str:
        cur = (currency or self.currency or "USD").upper()
        symbol = self._CURRENCY_SYMBOL.get(cur, cur + " ")
        n = self.format_number(value, decimals=decimals, locale=locale)
        return f"{symbol}{n}"

    def format_date(self, dt: datetime, locale: str | None = None, timezone: str | None = None) -> str:
        loc = (locale or self.locale or "en-US").lower()
        zdt = self.to_timezone(dt, timezone)
        if loc.startswith("en"):
            return zdt.strftime("%m/%d/%Y")
        return zdt.strftime("%d/%m/%Y")

    def format_time(self, dt: datetime, locale: str | None = None, timezone: str | None = None) -> str:
        loc = (locale or self.locale or "en-US").lower()
        zdt = self.to_timezone(dt, timezone)
        if loc.startswith("en"):
            return zdt.strftime("%I:%M %p")
        return zdt.strftime("%H:%M")

    def format_datetime(self, dt: datetime, locale: str | None = None, timezone: str | None = None) -> str:
        return f"{self.format_date(dt, locale=locale, timezone=timezone)} {self.format_time(dt, locale=locale, timezone=timezone)}"

