"""
Martin i18n/l10n helpers.
"""

from __future__ import annotations

import ast
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Dict

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None


_RTL_PREFIXES = ("ar", "he", "fa", "ur", "ps", "dv")

_LANGUAGE_NAMES = {
    "ar": "العربية",
    "de": "Deutsch",
    "en": "English",
    "es": "Español",
    "fa": "فارسی",
    "fr": "Français",
    "he": "עברית",
    "it": "Italiano",
    "ja": "日本語",
    "ko": "한국어",
    "nl": "Nederlands",
    "pl": "Polski",
    "pt": "Português",
    "ru": "Русский",
    "tr": "Türkçe",
    "uk": "Українська",
    "zh": "中文",
}

_COUNTRY_NAMES_EN = {
    "AR": "Argentina",
    "BR": "Brazil",
    "CA": "Canada",
    "CN": "China",
    "DE": "Germany",
    "EC": "Ecuador",
    "EG": "Egypt",
    "ES": "Spain",
    "FR": "France",
    "GB": "United Kingdom",
    "IT": "Italy",
    "JP": "Japan",
    "KR": "South Korea",
    "MX": "Mexico",
    "NL": "Netherlands",
    "PE": "Peru",
    "PL": "Poland",
    "PT": "Portugal",
    "RU": "Russia",
    "TR": "Turkey",
    "UA": "Ukraine",
    "US": "United States",
    "VE": "Venezuela",
}

_COUNTRY_NAMES_ES = {
    "AR": "Argentina",
    "BR": "Brasil",
    "CA": "Canadá",
    "CN": "China",
    "DE": "Alemania",
    "EC": "Ecuador",
    "EG": "Egipto",
    "ES": "España",
    "FR": "Francia",
    "GB": "Reino Unido",
    "IT": "Italia",
    "JP": "Japón",
    "KR": "Corea del Sur",
    "MX": "México",
    "NL": "Países Bajos",
    "PE": "Perú",
    "PL": "Polonia",
    "PT": "Portugal",
    "RU": "Rusia",
    "TR": "Turquía",
    "UA": "Ucrania",
    "US": "Estados Unidos",
    "VE": "Venezuela",
}


def normalize_locale(locale: str | None) -> str:
    raw = str(locale or "").strip()
    if not raw:
        return ""
    raw = raw.replace("-", "_")
    parts = [p for p in raw.split("_") if p]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0].lower()
    language = parts[0].lower()
    country = parts[1].upper()
    tail = [p.upper() for p in parts[2:]]
    return "_".join([language, country, *tail])


def locale_language(locale: str | None) -> str:
    norm = normalize_locale(locale)
    return norm.split("_", 1)[0] if norm else ""


def locale_country(locale: str | None) -> str:
    norm = normalize_locale(locale)
    parts = norm.split("_")
    return parts[1] if len(parts) > 1 else ""


def is_rtl_locale(locale: str | None) -> bool:
    return locale_language(locale).startswith(_RTL_PREFIXES)


def flag_emoji(country_code: str | None) -> str:
    code = str(country_code or "").strip().upper()
    if len(code) != 2 or not code.isalpha():
        return "🌐"
    base = 127397
    return chr(base + ord(code[0])) + chr(base + ord(code[1]))


def flag_image_url(country_code: str | None) -> str:
    code = str(country_code or "").strip().lower()
    if len(code) != 2 or not code.isalpha():
        return ""
    return f"https://flagcdn.com/{code}.svg"


def locale_label(locale: str | None) -> str:
    norm = normalize_locale(locale)
    if not norm:
        return "Idioma"
    lang = locale_language(norm)
    country = locale_country(norm)
    language_name = _LANGUAGE_NAMES.get(lang, lang.capitalize() or "Idioma")
    if not country:
        return language_name
    country_names = _COUNTRY_NAMES_ES if lang == "es" else _COUNTRY_NAMES_EN
    country_name = country_names.get(country, country)
    return f"{language_name} ({country_name})"


def describe_locale(locale: str | None) -> Dict[str, str]:
    norm = normalize_locale(locale)
    lang = locale_language(norm)
    country = locale_country(norm)
    return {
        "code": norm,
        "language": lang,
        "country": country,
        "label": locale_label(norm),
        "flag": flag_emoji(country),
        "flag_url": flag_image_url(country),
        "dir": "rtl" if is_rtl_locale(norm) else "ltr",
    }


def _deep_set(target: Dict[str, Any], key: str, value: Any):
    parts = [part for part in str(key).split(".") if part]
    if not parts:
        return
    cur = target
    for part in parts[:-1]:
        nxt = cur.get(part)
        if not isinstance(nxt, dict):
            nxt = {}
            cur[part] = nxt
        cur = nxt
    cur[parts[-1]] = value


def _po_unquote(raw: str) -> str:
    raw = str(raw or "").strip()
    if not raw.startswith('"'):
        return raw
    try:
        return ast.literal_eval(raw)
    except Exception:
        return raw.strip('"')


def load_po_catalog(path: str | Path) -> Dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        return {}

    messages: Dict[str, Any] = {}
    msgid_parts: list[str] = []
    msgstr_parts: list[str] = []
    current = None

    def flush():
        key = "".join(msgid_parts)
        value = "".join(msgstr_parts)
        if key:
            _deep_set(messages, key, value or key)

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            flush()
            msgid_parts = []
            msgstr_parts = []
            current = None
            continue
        if line.startswith("#"):
            continue
        if line.startswith("msgid "):
            flush()
            msgid_parts = [_po_unquote(line[6:])]
            msgstr_parts = []
            current = "id"
            continue
        if line.startswith("msgstr "):
            msgstr_parts = [_po_unquote(line[7:])]
            current = "str"
            continue
        if line.startswith('"'):
            if current == "id":
                msgid_parts.append(_po_unquote(line))
            elif current == "str":
                msgstr_parts.append(_po_unquote(line))

    flush()
    return messages


def load_locale_catalogs(path: str | Path) -> Dict[str, Dict[str, Any]]:
    base = Path(path)
    if not base.exists():
        return {}
    catalogs: Dict[str, Dict[str, Any]] = {}
    for po_file in sorted(base.glob("*.po")):
        code = normalize_locale(po_file.stem)
        if code:
            catalogs[code] = load_po_catalog(po_file)
    return catalogs


def discover_locale_codes(
    path: str | Path | None = None,
    locales: list[str] | tuple[str, ...] | None = None,
    messages: Dict[str, Dict[str, Any]] | None = None,
) -> list[str]:
    found: list[str] = []
    for locale in locales or []:
        norm = normalize_locale(locale)
        if norm and norm not in found:
            found.append(norm)
    for locale in (messages or {}).keys():
        norm = normalize_locale(locale)
        if norm and norm not in found:
            found.append(norm)
    if path:
        base = Path(path)
        if base.exists():
            for po_file in sorted(base.glob("*.po")):
                norm = normalize_locale(po_file.stem)
                if norm and norm not in found:
                    found.append(norm)
    return found


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
        self.default_locale = normalize_locale(default_locale or "es") or "es"
        self.fallback_locale = normalize_locale(fallback_locale or "en") or "en"
        self.locale = self.default_locale

    @classmethod
    def from_po_directory(
        cls,
        path: str | Path,
        default_locale: str = "es_ES",
        fallback_locale: str = "en_US",
    ):
        return cls(
            messages=load_locale_catalogs(path),
            default_locale=default_locale,
            fallback_locale=fallback_locale,
        )

    def available_locales(self) -> list[str]:
        return discover_locale_codes(messages=self.messages)

    def use(self, locale: str):
        self.locale = normalize_locale(locale or self.default_locale) or self.default_locale
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

    @staticmethod
    def _locale_candidates(locale: str | None) -> list[str]:
        norm = normalize_locale(locale)
        if not norm:
            return []
        candidates = [norm]
        base = locale_language(norm)
        if base and base not in candidates:
            candidates.append(base)
        alt = norm.replace("_", "-")
        if alt not in candidates:
            candidates.append(alt)
        return candidates

    def t(self, key: str, locale: str | None = None, default: str | None = None, **vars):
        lookup_order: list[str] = []
        for candidate in self._locale_candidates(locale or self.locale):
            if candidate not in lookup_order:
                lookup_order.append(candidate)
        for candidate in self._locale_candidates(self.fallback_locale):
            if candidate not in lookup_order:
                lookup_order.append(candidate)
        for candidate in self._locale_candidates(self.default_locale):
            if candidate not in lookup_order:
                lookup_order.append(candidate)

        text = None
        for loc in lookup_order:
            text = self._deep_get(self.messages.get(loc, {}), key)
            if text is not None:
                break
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

    _RTL_PREFIXES = _RTL_PREFIXES

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
        self.locale = normalize_locale(locale) or "es_EC"
        self.timezone = timezone
        self.currency = currency.upper()

    def is_rtl(self, locale: str | None = None) -> bool:
        loc = (normalize_locale(locale or self.locale) or "").lower().replace("_", "-")
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
        loc = (normalize_locale(locale or self.locale) or "en_US").lower()
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
        loc = (normalize_locale(locale or self.locale) or "en_US").lower()
        zdt = self.to_timezone(dt, timezone)
        if loc.startswith("en"):
            return zdt.strftime("%m/%d/%Y")
        return zdt.strftime("%d/%m/%Y")

    def format_time(self, dt: datetime, locale: str | None = None, timezone: str | None = None) -> str:
        loc = (normalize_locale(locale or self.locale) or "en_US").lower()
        zdt = self.to_timezone(dt, timezone)
        if loc.startswith("en"):
            return zdt.strftime("%I:%M %p")
        return zdt.strftime("%H:%M")

    def format_datetime(self, dt: datetime, locale: str | None = None, timezone: str | None = None) -> str:
        return f"{self.format_date(dt, locale=locale, timezone=timezone)} {self.format_time(dt, locale=locale, timezone=timezone)}"
