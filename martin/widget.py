"""
Martin - Widget Base

Every widget automatically accepts:
    style      — StyleBase | list[StyleBase] | str (raw CSS) | None
    padding    — int  or  Padding(...)
    margin     — int  or  Margin(...)
    width      — int (px) or str ("100%", "auto"...)
    height     — int (px) or str
    color      — str  (text color shorthand)
    background — str  (background-color shorthand)
    radius     — int  (border-radius shorthand)
    shadow     — bool | Shadow(...)
    opacity    — float (0.0 – 1.0)
    hidden     — bool (display: none)
    url        — str  wrap widget in <a href="..."> (optional)
    url_target — str  "_self" same tab | "_blank" new tab (default)

These are merged on top of the widget's own base styles automatically.
"""

import html as _html
import json as _json
import re as _re
from functools import wraps as _wraps

from .conditions import serialize_condition, ConditionExpr
from .styles import resolve_styles, StyleBase


class Widget:
    @staticmethod
    def _iter_style_items(value):
        if value is None:
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                yield from Widget._iter_style_items(item)
            return
        yield value

    @staticmethod
    def _merge_attr_value(current, value):
        if current in (None, ""):
            return value
        if value in (None, ""):
            return current
        current_tokens = str(current).split()
        value_tokens = str(value).split()
        merged = list(current_tokens)
        for token in value_tokens:
            if token not in merged:
                merged.append(token)
        return " ".join(merged)

    _slots: dict = {}  # {slot_name: {"desc": ..., "default": ...}}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register slot declarations in hook system
        slots = cls.__dict__.get("_slots", {})
        if slots:
            try:
                from .module.hook import register_hook as _reg_hook
                for slot_name, slot_config in slots.items():
                    hook_name = f"{cls.__name__}.{slot_name}"
                    _reg_hook(hook_name, default=slot_config.get("default"))
            except ImportError:
                pass  # module system not available

        render = cls.__dict__.get("render")
        if render is None:
            return
        if getattr(render, "_martin_auto_attrs_wrapped", False):
            return

        @_wraps(render)
        def _wrapped_render(self, *args, **kwargs):
            html = render(self, *args, **kwargs)
            html = self._apply_universal_attrs(html)
            html = self._apply_conditional_behavior(html)
            html = self._apply_floating_behavior(html)
            return html

        _wrapped_render._martin_auto_attrs_wrapped = True
        cls.render = _wrapped_render

    def render_slot(self, name: str, context: dict | None = None) -> str:
        """Resolve slot contributions from all modules and render them.

        Args:
            name: Slot name (e.g. "form_fields").
            context: Optional dict passed to each contributor.

        Returns:
            Concatenated HTML from all contributors.
        """
        try:
            from .module.hook import resolve_hooks
            contributions = resolve_hooks(f"{self.__class__.__name__}.{name}", context or {})
            return "".join(str(c) for c in contributions if c is not None)
        except ImportError:
            return ""

    @staticmethod
    def _extract_props(kwargs: dict) -> dict:
        """Pop universal style props from kwargs dict (mutates it)."""
        keys = (
            "style",
            "padding",
            "margin",
            "width",
            "height",
            "color",
            "background",
            "radius",
            "shadow",
            "opacity",
            "hidden",
            "visible",
            "readonly",
            "disabled",
            "url",
            "url_target",
            "attrs",
            "role",
            "tabindex",
            "floating",
            "float_position",
            "float_offset",
            "float_gap",
            "float_z_index",
        )
        props = {k: kwargs.pop(k, None) for k in keys}

        attrs = {}
        raw_attrs = props.get("attrs")
        if isinstance(raw_attrs, dict):
            attrs.update(raw_attrs)

        if props.get("role") is not None:
            attrs.setdefault("role", props.get("role"))
        if props.get("tabindex") is not None:
            attrs.setdefault("tabindex", props.get("tabindex"))
        if props.get("disabled") is True:
            attrs.setdefault("aria-disabled", "true")
        if props.get("readonly") is True:
            attrs.setdefault("aria-readonly", "true")

        for key in list(kwargs.keys()):
            if key.startswith("aria_") or key.startswith("data_"):
                attrs[key.replace("_", "-")] = kwargs.pop(key)

        props["attrs"] = attrs or None
        return props

    @staticmethod
    def _floating_css_size(value, fallback):
        if value is None:
            return fallback
        if isinstance(value, (int, float)):
            return f"{int(value)}px"
        return str(value)

    def _get_universal_attrs(self) -> dict:
        props = getattr(self, "_props", {}) or {}
        attrs = props.get("attrs")
        attrs = dict(attrs) if isinstance(attrs, dict) else {}
        for item in self._iter_style_items(props.get("style")):
            if hasattr(item, "fx_attrs") and callable(item.fx_attrs):
                for key, value in (item.fx_attrs() or {}).items():
                    if value is None:
                        continue
                    if key in attrs:
                        attrs[key] = self._merge_attr_value(attrs[key], value)
                    else:
                        attrs[key] = value
        defaults = self._default_a11y_attrs()
        if isinstance(defaults, dict):
            for key, value in defaults.items():
                if value is None:
                    continue
                attrs.setdefault(key, value)
        return attrs

    def _default_a11y_attrs(self) -> dict:
        """Widget-level defaults that can be overridden by explicit attrs/aria_*."""
        return {}

    @staticmethod
    def _to_plain_text(value) -> str:
        if value is None:
            return ""
        if isinstance(value, Widget):
            return ""
        text = str(value).strip()
        return " ".join(text.split())

    @staticmethod
    def _inject_attrs_into_first_tag(html: str, attrs: dict) -> str:
        if not html or not isinstance(html, str) or not attrs:
            return html

        skip_tags = {"script", "style", "link", "meta"}
        for m in _re.finditer(r"<([a-zA-Z][a-zA-Z0-9:_-]*)(\s[^<>]*?)?>", html):
            tag = (m.group(1) or "").lower()
            if tag in skip_tags:
                continue

            tag_start = m.start()
            tag_end = m.end()
            tag_src = html[tag_start:tag_end]
            parts = []
            for key, value in attrs.items():
                if value is None:
                    continue
                attr = str(key).replace("_", "-")
                if attr.lower() == "class":
                    class_match = _re.search(
                        r"""\bclass\s*=\s*(['"])(.*?)\1""",
                        tag_src,
                        flags=_re.IGNORECASE | _re.DOTALL,
                    )
                    if class_match:
                        existing = class_match.group(2)
                        merged = Widget._merge_attr_value(existing, value)
                        if merged != existing:
                            replacement = f'class="{_html.escape(merged, quote=True)}"'
                            start, end = class_match.span()
                            tag_src = tag_src[:start] + replacement + tag_src[end:]
                            tag_end = tag_start + len(tag_src)
                        continue
                if _re.search(
                    rf"""\b{_re.escape(attr)}(?:\s*=|\s|/?>)""",
                    tag_src,
                    flags=_re.IGNORECASE,
                ):
                    continue
                if isinstance(value, bool):
                    if value:
                        parts.append(attr)
                else:
                    esc = _html.escape(str(value), quote=True)
                    parts.append(f'{attr}="{esc}"')

            if not parts:
                return html[:tag_start] + tag_src + html[m.end() :]

            insert_at = (
                len(tag_src) - 2 if tag_src.endswith("/>") else len(tag_src) - 1
            )
            updated = tag_src[:insert_at] + " " + " ".join(parts) + tag_src[insert_at:]
            return html[:tag_start] + updated + html[m.end() :]

        return html

    def _apply_universal_attrs(self, html: str) -> str:
        attrs = self._get_universal_attrs()
        return self._inject_attrs_into_first_tag(html, attrs)

    def _apply_conditional_behavior(self, html: str) -> str:
        props = getattr(self, "_props", {}) or {}
        visible = props.get("visible")
        if visible is None and props.get("hidden") is not None:
            visible = not bool(props.get("hidden"))
        readonly = props.get("readonly")
        disabled = props.get("disabled")

        if visible is None and readonly is None and disabled is None:
            return html

        uid = f"martin_cond_{id(self) & 0xFFFFFF:x}"
        display_mode = "contents"
        static_wrapper_style = "display:none;" if visible is False else f"display:{display_mode};"
        config = {
            "visible": serialize_condition(visible) if visible is not None else True,
            "readonly": serialize_condition(readonly) if readonly is not None else False,
            "disabled": serialize_condition(disabled) if disabled is not None else False,
            "display": display_mode,
        }
        script = (
            "<script>(function(){"
            "if(!window.__martinConditionEngine){"
            "window.__martinConditionEngine={"
            "items:{},"
            "getTarget:function(wrapper){"
            "if(!wrapper)return null;"
            "for(var i=0;i<wrapper.children.length;i++){"
            "var child=wrapper.children[i];"
            "if(!child||!child.tagName)continue;"
            "if(/^(SCRIPT|STYLE|LINK|META)$/i.test(child.tagName))continue;"
            "return child;"
            "}"
            "return wrapper.firstElementChild||wrapper;"
            "},"
            "getField:function(inputId,source){"
            "if(!inputId)return null;"
            "var el=document.getElementById(inputId)||document.getElementById(inputId+'_val')||document.querySelector('[name=\"'+String(inputId).replace(/\"/g,'\\\\\"')+'\"]');"
            "if(!el)return null;"
            "var tag=(el.tagName||'').toUpperCase();"
            "var type=(el.type||'').toLowerCase();"
            "var mode=(source||'auto').toLowerCase();"
            "if(mode==='text')return (el.textContent||'').trim();"
            "if(mode==='checked')return !!el.checked;"
            "if(tag==='SELECT'&&el.multiple){return Array.prototype.slice.call(el.selectedOptions||[]).map(function(opt){return opt.value;});}"
            "if(type==='checkbox')return !!el.checked;"
            "if(type==='radio'){"
            "if(el.name){var checked=document.querySelector('input[type=\"radio\"][name=\"'+String(el.name).replace(/\"/g,'\\\\\"')+'\"]:checked');return checked?checked.value:null;}"
            "return !!el.checked;"
            "}"
            "if(el.value!==undefined)return el.value;"
            "return (el.textContent||'').trim();"
            "},"
            "truthy:function(value){"
            "if(Array.isArray(value))return value.length>0;"
            "return !!value;"
            "},"
            "compare:function(left,operator,right){"
            "if(operator==='contains'){return Array.isArray(left)?left.indexOf(right)>-1:String(left||'').indexOf(String(right||''))>-1;}"
            "if(operator==='starts_with'){return String(left||'').startsWith(String(right||''));}"
            "if(operator==='ends_with'){return String(left||'').endsWith(String(right||''));}"
            "var leftNum=parseFloat(left), rightNum=parseFloat(right);"
            "var bothNumeric=!isNaN(leftNum)&&!isNaN(rightNum)&&String(left).trim()!==''&&String(right).trim()!=='';"
            "var a=bothNumeric?leftNum:left, b=bothNumeric?rightNum:right;"
            "if(operator==='==')return a==b;"
            "if(operator==='!=')return a!=b;"
            "if(operator==='>')return a>b;"
            "if(operator==='>=')return a>=b;"
            "if(operator==='<')return a<b;"
            "if(operator==='<=')return a<=b;"
            "return !!a;"
            "},"
            "eval:function(expr){"
            "if(expr===undefined||expr===null)return expr;"
            "if(typeof expr!=='object'||Array.isArray(expr))return expr;"
            "var kind=expr.__martin_expr__||'';"
            "if(kind==='Field')return this.getField(expr.input_id,expr.source);"
            "if(kind==='Condition')return this.compare(this.eval(expr.left),expr.operator||'==',this.eval(expr.right));"
            "if(kind==='ConditionGroup'){"
            "var items=Array.isArray(expr.items)?expr.items:[];"
            "if((expr.operator||'and')==='or')return items.some(function(item){return window.__martinConditionEngine.truthy(window.__martinConditionEngine.eval(item));});"
            "return items.every(function(item){return window.__martinConditionEngine.truthy(window.__martinConditionEngine.eval(item));});"
            "}"
            "if(kind==='ConditionNot')return !this.truthy(this.eval(expr.expr));"
            "return expr;"
            "},"
            "apply:function(id){"
            "var item=this.items[id];"
            "if(!item)return;"
            "var wrapper=document.getElementById(id);"
            "if(!wrapper)return;"
            "var target=this.getTarget(wrapper);"
            "var isVisible=this.truthy(this.eval(item.visible));"
            "wrapper.style.display=isVisible?(item.display||'contents'):'none';"
            "var isDisabled=this.truthy(this.eval(item.disabled));"
            "var isReadonly=this.truthy(this.eval(item.readonly));"
            "if(target){"
            "var supportsDisabled=('disabled' in target);"
            "var supportsReadonly=('readOnly' in target);"
            "if(supportsDisabled)target.disabled=!!isDisabled;"
            "if(isDisabled){target.setAttribute('aria-disabled','true');target.setAttribute('data-martin-disabled','1');}"
            "else{target.removeAttribute('aria-disabled');target.removeAttribute('data-martin-disabled');}"
            "if(supportsReadonly)target.readOnly=!!isReadonly;"
            "if(isReadonly){target.setAttribute('aria-readonly','true');target.setAttribute('data-martin-readonly','1');"
            "if(!supportsReadonly&&supportsDisabled)target.disabled=true;}"
            "else{target.removeAttribute('aria-readonly');target.removeAttribute('data-martin-readonly');}"
            "}"
            "if(window.__martinFloatLayout&&window.__martinFloatLayout.schedule){window.__martinFloatLayout.schedule();}"
            "},"
            "mount:function(id,config){this.items[id]=config;this.apply(id);},"
            "refresh:function(){var self=this;Object.keys(self.items).forEach(function(id){self.apply(id);});},"
            "ensure:function(){"
            "if(this._bound)return;"
            "this._bound=true;"
            "var self=this;"
            "document.addEventListener('input',function(){self.refresh();},true);"
            "document.addEventListener('change',function(){self.refresh();},true);"
            "document.addEventListener('click',function(){self.refresh();},true);"
            "window.addEventListener('load',function(){self.refresh();});"
            "document.addEventListener('DOMContentLoaded',function(){self.refresh();});"
            "window.addEventListener('martin:condition-refresh',function(){self.refresh();});"
            "}"
            "};"
            "window.__martinConditionEngine.ensure();"
            "}"
            "window.__martinConditionEngine.mount("
            + _json.dumps(uid)
            + ","
            + _json.dumps(config, ensure_ascii=False)
            + ");"
            "})();</script>"
        )
        return f'<div id="{uid}" data-martin-condition="1" style="{static_wrapper_style}">{html}</div>' + script

    def _apply_floating_behavior(self, html: str) -> str:
        props = getattr(self, "_props", {}) or {}
        if not props.get("floating"):
            return html

        position = str(props.get("float_position") or "bottom-right").strip().lower()
        allowed = {"top-left", "top-right", "bottom-left", "bottom-right"}
        if position not in allowed:
            position = "bottom-right"

        offset = self._floating_css_size(props.get("float_offset"), "20px")
        gap = self._floating_css_size(props.get("float_gap"), "12px")
        z_index = int(props.get("float_z_index") or 999)
        uid = f"martin_float_{id(self) & 0xFFFFFF:x}"

        vertical = "top" if position.startswith("top") else "bottom"
        horizontal = "left" if position.endswith("left") else "right"
        wrapper_style = (
            "position:fixed;"
            f"{vertical}:{offset};"
            f"{horizontal}:{offset};"
            f"z-index:{z_index};"
        )
        wrapper = (
            f'<div id="{uid}" '
            f'data-martin-float="1" '
            f'data-martin-float-pos="{position}" '
            f'data-martin-float-offset="{offset}" '
            f'data-martin-float-gap="{gap}" '
            f'data-martin-float-z="{z_index}" '
            f'style="{wrapper_style}">{html}</div>'
        )
        script = (
            "<script>(function(){"
            "if(!window.__martinFloatLayout){"
            "window.__martinFloatLayout={"
            "schedule:function(){"
            "if(window.__martinFloatLayout._raf)return;"
            "window.__martinFloatLayout._raf=requestAnimationFrame(function(){"
            "window.__martinFloatLayout._raf=0;"
            "window.__martinFloatLayout.reflow();"
            "});"
            "},"
            "reflow:function(){"
            "var nodes=Array.prototype.slice.call(document.querySelectorAll('[data-martin-float=\"1\"]'));"
            "var groups={};"
            "nodes.forEach(function(node){"
            "if(!node||!node.isConnected)return;"
            "var styles=window.getComputedStyle?window.getComputedStyle(node):null;"
            "if(styles&&styles.display==='none')return;"
            "var key=node.getAttribute('data-martin-float-pos')||'bottom-right';"
            "if(!groups[key])groups[key]=[];"
            "groups[key].push(node);"
            "});"
            "Object.keys(groups).forEach(function(key){"
            "var cursor=0;"
            "groups[key].forEach(function(node){"
            "var offset=node.getAttribute('data-martin-float-offset')||'20px';"
            "var gap=node.getAttribute('data-martin-float-gap')||'12px';"
            "var base=parseFloat(offset)||20;"
            "var spacing=parseFloat(gap)||12;"
            "cursor=Math.max(cursor, base);"
            "if(key.indexOf('top')===0){node.style.top=cursor+'px';node.style.bottom='';}"
            "else{node.style.bottom=cursor+'px';node.style.top='';}"
            "if(key.indexOf('left')>-1){node.style.left=offset;node.style.right='';}"
            "else{node.style.right=offset;node.style.left='';}"
            "cursor+=node.offsetHeight+spacing;"
            "});"
            "});"
            "}"
            "};"
            "window.addEventListener('resize',window.__martinFloatLayout.schedule,{passive:true});"
            "window.addEventListener('load',window.__martinFloatLayout.schedule);"
            "document.addEventListener('DOMContentLoaded',window.__martinFloatLayout.schedule);"
            "}"
            "window.__martinFloatLayout.schedule();"
            "})();</script>"
        )
        return wrapper + script

    def _wrap_url(self, html: str) -> str:
        """If url prop is set, wraps rendered HTML in an <a> tag."""
        props = getattr(self, "_props", {})
        url = props.get("url")
        if not url:
            return html
        target = props.get("url_target") or "_blank"
        href = _html.escape(str(url), quote=True)
        target_esc = _html.escape(str(target), quote=True)
        rel = ' rel="noopener noreferrer"' if target == "_blank" else ""
        return f'<a href="{href}" target="{target_esc}"{rel} style="display:contents;text-decoration:none;">{html}</a>'

    def _resolve_props(self, base_css: str = "") -> str:
        """Merge base_css + any universal props into a single inline CSS string."""
        props = getattr(self, "_props", {})
        parts = [p for p in [base_css] if p]

        style = props.get("style")
        if style is not None:
            parts.append(resolve_styles(style))

        p = props.get("padding")
        if p is not None:
            parts.append(
                f"padding: {p}px" if isinstance(p, (int, float)) else resolve_styles(p)
            )

        m = props.get("margin")
        if m is not None:
            parts.append(
                f"margin: {m}px" if isinstance(m, (int, float)) else resolve_styles(m)
            )

        w = props.get("width")
        if w is not None:
            parts.append(
                f"width: {w}px" if isinstance(w, (int, float)) else f"width: {w}"
            )

        h = props.get("height")
        if h is not None:
            parts.append(
                f"height: {h}px" if isinstance(h, (int, float)) else f"height: {h}"
            )

        c = props.get("color")
        if c is not None:
            parts.append(f"color: {c}")

        bg = props.get("background")
        if bg is not None:
            parts.append(f"background: {bg}")

        r = props.get("radius")
        if r is not None:
            parts.append(f"border-radius: {r}px")

        sh = props.get("shadow")
        if sh is not None:
            if isinstance(sh, bool):
                if sh:
                    parts.append("box-shadow: 0 2px 8px rgba(0,0,0,0.15)")
            else:
                parts.append(resolve_styles(sh))

        op = props.get("opacity")
        if op is not None:
            parts.append(f"opacity: {op}")

        if props.get("hidden") or props.get("visible") is False:
            parts.append("display: none")

        return "; ".join(p for p in parts if p)

    @staticmethod
    def _css(*styles) -> str:
        return resolve_styles(*styles)

    @staticmethod
    def _attrs(**kwargs) -> str:
        parts = []
        for k, v in kwargs.items():
            if v is None:
                continue
            attr = k.replace("_", "-")
            if isinstance(v, bool):
                if v:
                    parts.append(attr)
            else:
                escaped = _html.escape(str(v), quote=True)
                parts.append(f'{attr}="{escaped}"')
        return (" " + " ".join(parts)) if parts else ""

    @staticmethod
    def _render_children(children) -> str:
        if not children:
            return ""
        parts = []
        for child in children:
            if isinstance(child, Widget):
                parts.append(child.render())
            elif child is not None:
                parts.append(str(child))
        return "".join(parts)

    @staticmethod
    def _resolve_inner(text=None, child=None, children=None) -> str:
        """
        Resuelve el contenido de un widget hoja.
        Prioridad: children > child > text
        Permite anidar widgets dentro de cualquier widget.
        """
        if children:
            return Widget._render_children(children)
        if child is not None:
            return child.render() if isinstance(child, Widget) else str(child)
        if text is not None:
            return text.render() if isinstance(text, Widget) else str(text)
        return ""

    def render(self) -> str:
        raise NotImplementedError(f"{self.__class__.__name__} must implement render()")

    def __str__(self):
        return self.render()

    def __repr__(self):
        return f"<{self.__class__.__name__}>"
