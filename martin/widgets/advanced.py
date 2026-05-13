"""
Martin advanced widgets.
"""

import json as _json
import uuid as _uuid

from ..widget import Widget

__all__ = [
    "DataGridColumn",
    "DataGrid",
    "WizardStep",
    "Wizard",
    "CommandPalette",
    "Drawer",
    "SplitPane",
    "Skeleton",
    "EmptyState",
    "ErrorState",
    "Form",
    "ResourceForm",
    "ResourceEditor",
    "ResourceTable",
    "ResourceDetails",
    "ResourceCardList",
    "ResourceStats",
    "ResourceFilters",
    "ResourceActions",
    "ResourceBulkActions",
    "ResourceToolbar",
    "ResourcePaginator",
    "ResourceCreateButton",
    "ResourceDuplicateButton",
    "ResourceDeleteButton",
    "ResourceKanban",
    "ResourceView",
    "JSWidgetAdapter",
]


class DataGridColumn:
    """
    DataGrid column definition.
    """

    def __init__(
        self,
        key,
        label=None,
        width=180,
        sortable=True,
        frozen=False,
        align="left",
    ):
        self.key = str(key)
        self.label = str(label if label is not None else key)
        self.width = int(width)
        self.sortable = bool(sortable)
        self.frozen = bool(frozen)
        self.align = str(align or "left")


class DataGrid(Widget):
    """
    Pro DataGrid:
      - fixed header
      - resize columns
      - reorder columns (drag header)
      - frozen columns (left sticky)
      - row grouping
      - virtual scrolling
    """

    def __init__(
        self,
        rows=None,
        columns=None,
        searchable=True,
        sortable=True,
        resizable=True,
        reorderable=True,
        freeze_columns=None,
        group_by=None,
        virtual_scroll=True,
        row_height=40,
        height=420,
        overscan=8,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.rows = rows or []
        self.columns = columns or []
        self.searchable = bool(searchable)
        self.sortable = bool(sortable)
        self.resizable = bool(resizable)
        self.reorderable = bool(reorderable)
        self.freeze_columns = {str(k) for k in (freeze_columns or [])}
        self.group_by = str(group_by) if group_by else ""
        self.virtual_scroll = bool(virtual_scroll)
        self.row_height = max(26, int(row_height))
        self.height = max(180, int(height))
        self.overscan = max(1, int(overscan))
        self.uid = f"dg_{_uuid.uuid4().hex[:8]}"

    def _normalize(self):
        rows = self.rows or []
        if not rows:
            return [], []

        if isinstance(rows[0], dict):
            dict_rows = []
            for r in rows:
                if isinstance(r, dict):
                    dict_rows.append({str(k): r.get(k) for k in r.keys()})
                else:
                    dict_rows.append({})
        else:
            max_cols = max(len(r) if isinstance(r, (list, tuple)) else 0 for r in rows)
            keys = [f"col_{i+1}" for i in range(max_cols)]
            dict_rows = []
            for r in rows:
                rr = {}
                if isinstance(r, (list, tuple)):
                    for i, v in enumerate(r):
                        rr[keys[i]] = v
                dict_rows.append(rr)

        out_cols = []
        if self.columns:
            for c in self.columns:
                if isinstance(c, DataGridColumn):
                    out_cols.append(
                        {
                            "key": c.key,
                            "label": c.label,
                            "width": max(80, int(c.width)),
                            "sortable": bool(c.sortable and self.sortable),
                            "frozen": bool(c.frozen or c.key in self.freeze_columns),
                            "align": c.align if c.align in ("left", "center", "right") else "left",
                        }
                    )
                elif isinstance(c, dict):
                    key = str(c.get("key", ""))
                    if not key:
                        continue
                    out_cols.append(
                        {
                            "key": key,
                            "label": str(c.get("label", key)),
                            "width": max(80, int(c.get("width", 180))),
                            "sortable": bool(c.get("sortable", True) and self.sortable),
                            "frozen": bool(c.get("frozen", False) or key in self.freeze_columns),
                            "align": str(c.get("align", "left")) if str(c.get("align", "left")) in ("left", "center", "right") else "left",
                        }
                    )
                else:
                    key = str(c)
                    if not key:
                        continue
                    out_cols.append(
                        {
                            "key": key,
                            "label": key,
                            "width": 180,
                            "sortable": bool(self.sortable),
                            "frozen": key in self.freeze_columns,
                            "align": "left",
                        }
                    )
        else:
            keys = list(dict_rows[0].keys())
            out_cols = [
                {
                    "key": k,
                    "label": k.replace("_", " ").title(),
                    "width": 180,
                    "sortable": bool(self.sortable),
                    "frozen": k in self.freeze_columns,
                    "align": "left",
                }
                for k in keys
            ]

        return dict_rows, out_cols

    def render(self):
        uid = self.uid
        rows, cols = self._normalize()
        data_js = _json.dumps(rows, ensure_ascii=False)
        cols_js = _json.dumps(cols, ensure_ascii=False)
        group_key = _json.dumps(self.group_by)
        extra = self._resolve_props()

        search_html = ""
        if self.searchable:
            search_html = (
                f'<input id="{uid}_q" type="text" placeholder="Buscar..." '
                f'oninput="{uid}_setQuery(this.value)" '
                f'style="width:100%;padding:8px 12px;margin-bottom:10px;'
                f'border:1px solid var(--border-input,var(--border));border-radius:8px;'
                f'background:var(--input-bg,var(--surface));color:var(--text);outline:none">'
            )

        css = (
            f"<style>"
            f"#{uid}_wrap{{position:relative;border:1px solid var(--border);border-radius:12px;overflow:hidden;background:var(--surface)}}"
            f"#{uid}_scroll{{height:{self.height}px;overflow:auto;position:relative}}"
            f"#{uid}_tbl{{width:max-content;min-width:100%;border-collapse:collapse;table-layout:fixed}}"
            f"#{uid}_tbl th,#{uid}_tbl td{{border-bottom:1px solid var(--border);padding:0 10px;height:{self.row_height}px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}"
            f"#{uid}_tbl th{{position:sticky;top:0;background:var(--bg-secondary,var(--surface));"
            f"backdrop-filter:none;-webkit-backdrop-filter:none;z-index:3;font-size:13px;font-weight:700;color:var(--text);"
            f"user-select:none;box-shadow:inset 0 -1px 0 var(--border)}}"
            f"#{uid}_tbl td{{font-size:13px;color:var(--text)}}"
            f"#{uid}_tbl tr:nth-child(even) td{{background:color-mix(in srgb, var(--surface) 88%, var(--bg-secondary, #000) 12%)}}"
            f"#{uid}_tbl tr.dg-group td{{background:color-mix(in srgb, var(--accent) 10%, var(--surface));font-weight:700;cursor:pointer}}"
            f"#{uid}_tbl th .dg-resize{{position:absolute;top:0;right:0;width:8px;height:100%;cursor:col-resize;z-index:6}}"
            f"#{uid}_tbl th .dg-sort{{margin-left:6px;color:var(--text-muted);font-size:10px}}"
            f"#{uid}_tbl th .dg-drag{{opacity:.45;margin-left:7px;font-size:11px}}"
            f"#{uid}_tbl .dg-frozen{{position:sticky;background:var(--surface);z-index:4;box-shadow:1px 0 0 var(--border)}}"
            f"#{uid}_tbl th.dg-frozen{{z-index:7;background:var(--bg-secondary,var(--surface))}}"
            f"</style>"
        )

        js = (
            f"<script>(function(){{"
            f"var uid='{uid}';"
            f"var rows={data_js};"
            f"var cols={cols_js};"
            f"var sortKey='';var sortDir=1;var q='';"
            f"var groupBy={group_key};"
            f"var collapsed={{}};"
            f"var virtual={str(self.virtual_scroll).lower()};"
            f"var rowH={self.row_height};"
            f"var overscan={self.overscan};"
            f"var reorderable={str(self.reorderable).lower()};"
            f"var resizable={str(self.resizable).lower()};"
            f"var scroll=document.getElementById(uid+'_scroll');"
            f"var head=document.getElementById(uid+'_head');"
            f"var body=document.getElementById(uid+'_body');"
            f"if(!scroll||!head||!body)return;"
            f"var dragCol=-1;var resizing=null;"
            f"function esc(v){{return String(v==null?'':v).replace(/[&<>\\\"']/g,function(m){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','\\\"':'&quot;',\"'\":'&#39;'}}[m];}});}}"
            f"function val(row,key){{var v=row[key];return v==null?'':String(v);}}"
            f"function sortRows(list){{if(!sortKey)return list.slice();var out=list.slice();out.sort(function(a,b){{var va=val(a,sortKey).trim();var vb=val(b,sortKey).trim();var na=Number(va),nb=Number(vb);if(va!==''&&vb!==''&&!isNaN(na)&&!isNaN(nb))return sortDir*(na-nb);return sortDir*va.localeCompare(vb,'es',{{sensitivity:'base'}});}});return out;}}"
            f"function filtered(){{if(!q)return rows.slice();var qq=q.toLowerCase();return rows.filter(function(r){{for(var i=0;i<cols.length;i++){{var k=cols[i].key;if(val(r,k).toLowerCase().indexOf(qq)>=0)return true;}}return false;}});}}"
            f"function buildView(){{var data=sortRows(filtered());if(!groupBy)return data.map(function(r){{return {{t:'r',r:r}};}});var groups={{}};var order=[];for(var i=0;i<data.length;i++){{var g=val(data[i],groupBy)||'Sin grupo';if(!groups[g]){{groups[g]=[];order.push(g);}}groups[g].push(data[i]);}}var out=[];for(var j=0;j<order.length;j++){{var gg=order[j];out.push({{t:'g',g:gg,c:groups[gg].length}});if(!collapsed[gg]){{for(var n=0;n<groups[gg].length;n++)out.push({{t:'r',r:groups[gg][n],g:gg}});}}}}return out;}}"
            f"function frozenOffsets(){{var left=0;var map=[];for(var i=0;i<cols.length;i++){{if(cols[i].frozen){{map[i]=left;left+=Math.max(80,Number(cols[i].width)||180);}}else map[i]=null;}}return map;}}"
            f"function renderHead(){{var offs=frozenOffsets();var h='';for(var i=0;i<cols.length;i++){{var c=cols[i];var w=Math.max(80,Number(c.width)||180);var st='width:'+w+'px;min-width:'+w+'px;max-width:'+w+'px;text-align:'+c.align+';';var cls='';if(c.frozen&&offs[i]!=null){{cls=' dg-frozen';st+='left:'+offs[i]+'px;';}}var sort='';if(c.sortable){{if(sortKey===c.key)sort='<span class=\"dg-sort\">'+(sortDir>0?'▲':'▼')+'</span>';else sort='<span class=\"dg-sort\">⇅</span>';}}var drag=reorderable?'<span class=\"dg-drag\">⋮⋮</span>':'';var rz=resizable?'<span class=\"dg-resize\" data-r=\"'+i+'\"></span>':'';h+='<th class=\"'+cls.trim()+'\" data-c=\"'+i+'\" draggable=\"'+(reorderable?'true':'false')+'\" style=\"'+st+'\">'+esc(c.label)+sort+drag+rz+'</th>';}}head.innerHTML='<tr>'+h+'</tr>';}}"
            f"function rowHtml(entry,offs){{if(entry.t==='g'){{var icon=collapsed[entry.g]?'▶':'▼';return '<tr class=\"dg-group\" data-g=\"'+esc(entry.g)+'\"><td colspan=\"'+cols.length+'\">'+icon+' '+esc(entry.g)+' ('+entry.c+')</td></tr>';}}var h='<tr>';for(var i=0;i<cols.length;i++){{var c=cols[i];var w=Math.max(80,Number(c.width)||180);var st='width:'+w+'px;min-width:'+w+'px;max-width:'+w+'px;text-align:'+c.align+';';var cls='';if(c.frozen&&offs[i]!=null){{cls=' class=\"dg-frozen\"';st+='left:'+offs[i]+'px;';}}h+='<td'+cls+' style=\"'+st+'\">'+esc(val(entry.r,c.key))+'</td>';}}h+='</tr>';return h;}}"
            f"function renderBody(){{var view=buildView();var offs=frozenOffsets();if(!virtual){{var html='';for(var i=0;i<view.length;i++)html+=rowHtml(view[i],offs);body.innerHTML=html||'<tr><td colspan=\"'+cols.length+'\" style=\"padding:16px;color:var(--text-muted)\">Sin resultados</td></tr>';return;}}var top=scroll.scrollTop||0;var vh=scroll.clientHeight||{self.height};var start=Math.max(0,Math.floor(top/rowH)-overscan);var count=Math.ceil(vh/rowH)+overscan*2;var end=Math.min(view.length,start+count);var topPad=start*rowH;var bottomPad=Math.max(0,(view.length-end)*rowH);var html='';if(topPad>0)html+='<tr aria-hidden=\"true\"><td colspan=\"'+cols.length+'\" style=\"height:'+topPad+'px;padding:0;border:none\"></td></tr>';for(var i=start;i<end;i++)html+=rowHtml(view[i],offs);if(bottomPad>0)html+='<tr aria-hidden=\"true\"><td colspan=\"'+cols.length+'\" style=\"height:'+bottomPad+'px;padding:0;border:none\"></td></tr>';body.innerHTML=html||'<tr><td colspan=\"'+cols.length+'\" style=\"padding:16px;color:var(--text-muted)\">Sin resultados</td></tr>';}}"
            f"function renderAll(){{renderHead();renderBody();bindHead();bindBody();}}"
            f"function bindBody(){{body.querySelectorAll('tr.dg-group').forEach(function(tr){{tr.addEventListener('click',function(){{var g=this.getAttribute('data-g');collapsed[g]=!collapsed[g];renderBody();bindBody();}});}});}}"
            "function bindHead(){head.querySelectorAll('th[data-c]').forEach(function(th){var idx=Number(th.getAttribute('data-c'));var c=cols[idx];th.addEventListener('click',function(e){if(e.target&&e.target.getAttribute('data-r')!==null)return;if(!c.sortable)return;if(sortKey===c.key)sortDir*=-1;else{sortKey=c.key;sortDir=1;}renderBody();});if(reorderable){th.addEventListener('dragstart',function(){dragCol=idx;});th.addEventListener('dragover',function(e){e.preventDefault();});th.addEventListener('drop',function(e){e.preventDefault();var to=Number(this.getAttribute('data-c'));if(dragCol<0||to===dragCol)return;var mv=cols.splice(dragCol,1)[0];cols.splice(to,0,mv);dragCol=-1;renderAll();});}});if(resizable){head.querySelectorAll('.dg-resize').forEach(function(gr){gr.addEventListener('mousedown',function(e){e.preventDefault();e.stopPropagation();var i=Number(this.getAttribute('data-r'));resizing={i:i,x:e.clientX,w:Math.max(80,Number(cols[i].width)||180)};});});}}"
            f"window.addEventListener('mousemove',function(e){{if(!resizing)return;var nw=Math.max(80,resizing.w + (e.clientX-resizing.x));cols[resizing.i].width=nw;renderAll();}});"
            f"window.addEventListener('mouseup',function(){{resizing=null;}});"
            f"scroll.addEventListener('scroll',function(){{if(virtual)renderBody();}});"
            f"window[uid+'_setQuery']=function(v){{q=String(v||'');renderBody();}};"
            f"window[uid+'_setGroupBy']=function(k){{groupBy=String(k||'');collapsed={{}};renderBody();bindBody();}};"
            f"window[uid+'_setRows']=function(nextRows){{rows=Array.isArray(nextRows)?nextRows:[];renderBody();bindBody();}};"
            f"renderAll();"
            f"}})();</script>"
        )

        return (
            css
            + f'<div style="{extra}">'
            + search_html
            + f'<div id="{uid}_wrap">'
            + f'  <div id="{uid}_scroll">'
            + f'    <table id="{uid}_tbl" role="grid">'
            + f'      <thead id="{uid}_head"></thead>'
            + f'      <tbody id="{uid}_body"></tbody>'
            + f"    </table>"
            + f"  </div>"
            + f"</div>"
            + js
            + f"</div>"
        )


class WizardStep(Widget):
    """
    Single step used inside Wizard.
    """

    def __init__(self, title="", description="", child=None, children=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.title = title
        self.description = description
        self.child = child
        self.children = children

    def render_content(self):
        return self._resolve_inner(None, self.child, self.children)

    def render(self):
        body = self.render_content()
        extra = self._resolve_props()
        return (
            f'<div style="{extra}">'
            f"{body}"
            f"</div>"
        )


class Wizard(Widget):
    """
    Multi-step flow with progress, step navigation and finish actions.
    """

    def __init__(
        self,
        children=None,
        child=None,
        initial_step=0,
        show_progress=True,
        show_actions=True,
        previous_label="Back",
        next_label="Next",
        finish_label="Finish",
        on_finish="",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.children = children or ([] if child is None else [child])
        self.initial_step = max(0, int(initial_step or 0))
        self.show_progress = bool(show_progress)
        self.show_actions = bool(show_actions)
        self.previous_label = str(previous_label or "Back")
        self.next_label = str(next_label or "Next")
        self.finish_label = str(finish_label or "Finish")
        self.on_finish = str(on_finish or "")
        self.uid = f"wiz_{_uuid.uuid4().hex[:8]}"

    def _normalize_steps(self):
        steps = []
        for index, item in enumerate(self.children):
            if isinstance(item, WizardStep):
                steps.append(item)
            elif isinstance(item, Widget):
                steps.append(WizardStep(title=f"Step {index + 1}", child=item))
        return steps

    def render(self):
        steps = self._normalize_steps()
        if not steps:
            return ""
        uid = self.uid
        extra = self._resolve_props("display:block")
        initial = min(self.initial_step, max(0, len(steps) - 1))

        head_html = ""
        if self.show_progress:
            items = []
            for index, step in enumerate(steps):
                title = str(step.title or f"Step {index + 1}")
                description = str(step.description or "")
                items.append(
                    f'<button type="button" id="{uid}_tab_{index}" data-step="{index}" '
                    f'style="display:flex;align-items:flex-start;gap:10px;text-align:left;border:none;background:transparent;'
                    f'cursor:pointer;padding:0;color:inherit;min-width:0">'
                    f'  <span id="{uid}_bullet_{index}" style="width:30px;height:30px;border-radius:999px;'
                    f'     display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;'
                    f'     border:1px solid var(--border);background:var(--surface-2);color:var(--text-muted);flex-shrink:0">{index + 1}</span>'
                    f'  <span style="display:grid;gap:2px;min-width:0">'
                    f'    <strong style="font-size:13px;line-height:1.2;color:var(--text)">{title}</strong>'
                    f'    <small style="font-size:11px;line-height:1.3;color:var(--text-muted)">{description}</small>'
                    f"  </span>"
                    f"</button>"
                )
            head_html = (
                f'<div id="{uid}_progress" style="display:grid;grid-template-columns:repeat({len(steps)},minmax(0,1fr));'
                f'gap:14px;margin-bottom:18px">{ "".join(items) }</div>'
            )

        body_html = "".join(
            f'<section id="{uid}_panel_{index}" data-step-panel="{index}" style="display:none">'
            f"{step.render_content()}"
            f"</section>"
            for index, step in enumerate(steps)
        )

        actions_html = ""
        if self.show_actions:
            actions_html = (
                f'<div style="display:flex;justify-content:space-between;gap:12px;margin-top:18px">'
                f'  <button type="button" id="{uid}_prev" style="padding:10px 14px;border-radius:10px;'
                f'     border:1px solid var(--border);background:var(--surface-2);color:var(--text);cursor:pointer">{self.previous_label}</button>'
                f'  <button type="button" id="{uid}_next" style="padding:10px 16px;border-radius:10px;'
                f'     border:none;background:var(--accent);color:#fff;cursor:pointer;font-weight:600">{self.next_label}</button>'
                f"</div>"
            )

        js = (
            f"<script>(function(){{"
            f"var uid='{uid}',count={len(steps)},step={initial};"
            f"var prev=document.getElementById(uid+'_prev');"
            f"var next=document.getElementById(uid+'_next');"
            f"function setStep(n){{step=Math.max(0,Math.min(count-1,n));"
            f"for(var i=0;i<count;i++){{"
            f"var panel=document.getElementById(uid+'_panel_'+i);"
            f"var bullet=document.getElementById(uid+'_bullet_'+i);"
            f"var tab=document.getElementById(uid+'_tab_'+i);"
            f"if(panel)panel.style.display=i===step?'block':'none';"
            f"if(bullet){{bullet.style.background=i<=step?'var(--accent)':'var(--surface-2)';bullet.style.color=i<=step?'#fff':'var(--text-muted)';bullet.style.borderColor=i<=step?'transparent':'var(--border)';}}"
            f"if(tab)tab.setAttribute('aria-current',i===step?'step':'false');"
            f"}}"
            f"if(prev)prev.disabled=step===0;"
            f"if(prev)prev.style.opacity=step===0?'.55':'1';"
            f"if(next)next.textContent=step===count-1?{_json.dumps(self.finish_label)}:{_json.dumps(self.next_label)};"
            f"}}"
            f"for(var j=0;j<count;j++){{(function(index){{var tab=document.getElementById(uid+'_tab_'+index);if(tab)tab.addEventListener('click',function(){{setStep(index);}});}})(j);}}"
            f"if(prev)prev.addEventListener('click',function(){{setStep(step-1);}});"
            f"if(next)next.addEventListener('click',function(){{if(step>=count-1){{"
            + (f"try{{(new Function({_json.dumps(self.on_finish)}))();}}catch(e){{console.error(e);}}" if self.on_finish else "")
            + f"return;}}setStep(step+1);}});"
            f"setStep(step);"
            f"}})();</script>"
        )

        return (
            f'<div style="{extra}">'
            f'<div style="border:1px solid var(--border);border-radius:18px;padding:20px;'
            f'background:var(--surface);box-shadow:var(--shadow)">{head_html}{body_html}{actions_html}</div>'
            f"{js}</div>"
        )


class CommandPalette(Widget):
    """
    Global command palette (Ctrl/Cmd+K).
    """

    def __init__(
        self,
        items=None,
        title="Commands",
        placeholder="Type a command...",
        trigger_label="Open commands",
        show_trigger=True,
        hotkey="k",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.items = items or []
        self.title = title
        self.placeholder = placeholder
        self.trigger_label = trigger_label
        self.show_trigger = bool(show_trigger)
        self.hotkey = str(hotkey or "k").lower()
        self.uid = f"cmd_{_uuid.uuid4().hex[:8]}"

    @staticmethod
    def _normalize_item(item):
        if isinstance(item, (tuple, list)):
            label = str(item[0]) if item else ""
            value = str(item[1]) if len(item) > 1 else ""
            payload = {"label": label, "keywords": "", "shortcut": ""}
            if value.startswith(("http://", "https://", "/", "#")):
                payload["href"] = value
            elif value:
                payload["action"] = value
            return payload
        if isinstance(item, dict):
            return {
                "label": str(item.get("label", "")),
                "href": str(item.get("href", "")),
                "action": str(item.get("action", "")),
                "keywords": str(item.get("keywords", "")),
                "shortcut": str(item.get("shortcut", "")),
            }
        return {"label": str(item), "keywords": "", "shortcut": ""}

    def render(self):
        uid = self.uid
        extra = self._resolve_props()
        items = [self._normalize_item(it) for it in self.items]
        data = _json.dumps(items, ensure_ascii=False)
        trigger = ""
        if self.show_trigger:
            trigger = (
                f'<button type="button" onclick="{uid}_open()" style="'
                f'padding:8px 12px;border:1px solid var(--border);border-radius:9px;'
                f'background:var(--surface);color:var(--text);cursor:pointer;font-size:13px;'
                f'font-weight:600">{self.trigger_label}</button>'
            )
        css = (
            f"<style>"
            f"#{uid}_ov{{display:none;position:fixed;inset:0;z-index:100200;"
            f"background:rgba(0,0,0,.54);backdrop-filter:blur(6px)}}"
            f"#{uid}_box{{width:min(760px,92vw);margin:9vh auto 0;background:var(--surface);"
            f"border:1px solid var(--border);border-radius:14px;box-shadow:0 22px 60px rgba(0,0,0,.35);overflow:hidden}}"
            f"#{uid}_head{{padding:12px;border-bottom:1px solid var(--border)}}"
            f"#{uid}_list{{max-height:min(60vh,460px);overflow:auto;padding:8px}}"
            f"#{uid}_item:hover,#{uid}_item[data-a='1']{{background:var(--surface-2)}}"
            f"#{uid}_sc{{font-size:11px;color:var(--text-muted)}}"
            f"</style>"
        )
        html = (
            f'<div style="{extra}">{trigger}</div>'
            f'<div id="{uid}_ov" onclick="{uid}_closeOnBackdrop(event)">'
            f'  <div id="{uid}_box" role="dialog" aria-modal="true" aria-label="{self.title}" onclick="event.stopPropagation()">'
            f'    <div id="{uid}_head">'
            f'      <input id="{uid}_q" type="text" placeholder="{self.placeholder}" '
            f'       style="width:100%;padding:10px 12px;border:1px solid var(--border-input,var(--border));'
            f'       border-radius:10px;background:var(--input-bg,var(--surface));color:var(--text);outline:none">'
            f'    </div>'
            f'    <div id="{uid}_list"></div>'
            f"  </div>"
            f"</div>"
        )
        js = (
            f"<script>(function(){{"
            f"var uid='{uid}',items={data};"
            f"var ov=document.getElementById(uid+'_ov');"
            f"var q=document.getElementById(uid+'_q');"
            f"var list=document.getElementById(uid+'_list');"
            f"if(!ov||!q||!list)return;"
            f"var filtered=items.slice();var active=0;"
            f"function esc(t){{return String(t||'').replace(/[&<>\\\"']/g,function(m){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','\\\"':'&quot;',\"'\":'&#39;'}}[m];}});}}"
            f"function render(){{"
            f"  if(!filtered.length){{list.innerHTML='<div style=\"padding:14px;color:var(--text-muted)\">No results</div>';return;}}"
            f"  var h='';"
            f"  for(var i=0;i<filtered.length;i++){{"
            f"    var it=filtered[i];var sc=it.shortcut?'<span id=\"'+uid+'_sc\">'+esc(it.shortcut)+'</span>':'';"
            f"    h+='<div id=\"'+uid+'_item\" data-a=\"'+(i===active?'1':'0')+'\" style=\"padding:10px 12px;border-radius:10px;display:flex;align-items:center;justify-content:space-between;cursor:pointer\" onclick=\"'+uid+'_pick('+i+')\">'+"
            f"      '<span>'+esc(it.label||'Command')+'</span>'+sc+'</div>';"
            f"  }}"
            f"  list.innerHTML=h;"
            f"}}"
            f"function filter(v){{"
            f"  var s=String(v||'').toLowerCase().trim();"
            f"  if(!s){{filtered=items.slice();active=0;render();return;}}"
            f"  filtered=items.filter(function(it){{"
            f"    var hay=(it.label||'')+' '+(it.keywords||'');"
            f"    return hay.toLowerCase().indexOf(s)>=0;"
            f"  }});"
            f"  active=0;render();"
            f"}}"
            f"window[uid+'_pick']=function(i){{"
            f"  var it=filtered[i];if(!it)return;"
            f"  window[uid+'_close']();"
            f"  if(it.href){{window.location.href=it.href;return;}}"
            f"  if(it.action){{try{{(new Function(it.action))();}}catch(e){{console.error(e);}}}}"
            f"}};"
            f"window[uid+'_open']=function(){{ov.style.display='block';setTimeout(function(){{q.focus();q.select();}},0);}};"
            f"window[uid+'_close']=function(){{ov.style.display='none';q.value='';filter('');}};"
            f"window[uid+'_closeOnBackdrop']=function(e){{if(e&&e.target===ov)window[uid+'_close']();}};"
            f"q.addEventListener('input',function(){{filter(q.value);}});"
            f"q.addEventListener('keydown',function(e){{"
            f"  if(e.key==='ArrowDown'){{active=Math.min(active+1,Math.max(filtered.length-1,0));render();e.preventDefault();}}"
            f"  if(e.key==='ArrowUp'){{active=Math.max(active-1,0);render();e.preventDefault();}}"
            f"  if(e.key==='Enter'){{window[uid+'_pick'](active);e.preventDefault();}}"
            f"  if(e.key==='Escape'){{window[uid+'_close']();e.preventDefault();}}"
            f"}});"
            f"document.addEventListener('keydown',function(e){{"
            f"  var isMac=/Mac|iPhone|iPad|iPod/.test(navigator.platform||'');"
            f"  var open=((isMac&&e.metaKey)||(!isMac&&e.ctrlKey))&&String(e.key||'').toLowerCase()==='{self.hotkey}';"
            f"  if(open){{e.preventDefault();window[uid+'_open']();return;}}"
            f"  if(e.key==='Escape'&&ov.style.display==='block')window[uid+'_close']();"
            f"}});"
            f"filter('');"
            f"}})();</script>"
        )
        return css + html + js


class Drawer(Widget):
    """
    Lateral drawer with optional mobile bottom-sheet behavior.
    """

    def __init__(
        self,
        id,
        title=None,
        side="right",
        width=360,
        mobile_sheet=True,
        mobile_breakpoint=780,
        close_on_backdrop=True,
        children=None,
        child=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.id = str(id)
        self.title = title
        self.side = "left" if str(side).lower() == "left" else "right"
        self.width = max(220, int(width))
        self.mobile_sheet = bool(mobile_sheet)
        self.mobile_breakpoint = max(360, int(mobile_breakpoint))
        self.close_on_backdrop = bool(close_on_backdrop)
        if child is not None and children is None:
            children = [child]
        self.children = children or []

    def render(self):
        did = self.id
        extra = self._resolve_props()
        closed = "translateX(-100%)" if self.side == "left" else "translateX(100%)"
        side_pin = "left:0;" if self.side == "left" else "right:0;"
        title_html = ""
        if self.title is not None:
            t = self.title.render() if isinstance(self.title, Widget) else str(self.title)
            title_html = (
                f'<div style="display:flex;align-items:center;justify-content:space-between;'
                f'padding:14px 16px;border-bottom:1px solid var(--border)">'
                f'<strong style="font-size:15px;color:var(--text)">{t}</strong>'
                f'<button type="button" onclick="closeDrawer(\'{did}\')" '
                f'style="background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:20px">x</button>'
                f"</div>"
            )
        click_backdrop = f' onclick="if(event.target===this)closeDrawer(\'{did}\')"' if self.close_on_backdrop else ""
        mobile_css = ""
        if self.mobile_sheet:
            mobile_css = (
                f"@media(max-width:{self.mobile_breakpoint}px){{"
                f"#{did}_panel{{left:0!important;right:0!important;top:auto!important;bottom:0!important;width:100%!important;"
                f"max-height:82vh!important;border-radius:14px 14px 0 0;transform:translateY(100%)!important;border-left:none!important;border-right:none!important}}"
                f"#{did}[data-open='1'] #{did}_panel{{transform:translateY(0)!important}}"
                f"}}"
            )
        css = f"<style>{mobile_css}</style>" if mobile_css else ""

        return (
            css
            + f'<div id="{did}" data-open="0" style="display:none;position:fixed;inset:0;z-index:100120;background:rgba(0,0,0,.45);"{click_backdrop}>'
            + f'  <aside id="{did}_panel" role="dialog" aria-modal="true" style="'
            + f'    position:absolute;top:0;bottom:0;{side_pin}width:{self.width}px;'
            + f'    background:var(--surface);border-{self.side}:1px solid var(--border);'
            + f'    box-shadow:0 18px 54px rgba(0,0,0,.36);transition:transform .24s cubic-bezier(.4,0,.2,1);'
            + f'    transform:{closed};overflow:auto;{extra}">'
            + title_html
            + f'    <div style="padding:16px">{self._render_children(self.children)}</div>'
            + "  </aside>"
            + "</div>"
            + "<script>"
            + "window._martinDrawerFns=window._martinDrawerFns||{};"
            + f"window._martinDrawerFns[{_json.dumps(did)}]=window._martinDrawerFns[{_json.dumps(did)}]||{{"
            + "open:function(){"
            + f" var d=document.getElementById({_json.dumps(did)}),p=document.getElementById({_json.dumps(did + '_panel')});"
            + " if(!d||!p)return;d.style.display='block';d.setAttribute('data-open','1');"
            + " requestAnimationFrame(function(){p.style.transform='translateX(0)';});"
            + "},"
            + "close:function(){"
            + f" var d=document.getElementById({_json.dumps(did)}),p=document.getElementById({_json.dumps(did + '_panel')});"
            + " if(!d||!p)return;d.setAttribute('data-open','0');"
            + f" var mobile=window.matchMedia('(max-width:{self.mobile_breakpoint}px)').matches;"
            + " if(mobile){p.style.transform='translateY(100%)';}"
            + f" else p.style.transform={_json.dumps(closed)};"
            + " setTimeout(function(){d.style.display='none';},230);"
            + "}"
            + "};"
            + "window.openDrawer=window.openDrawer||function(id){var f=window._martinDrawerFns&&window._martinDrawerFns[id];if(f)f.open();};"
            + "window.closeDrawer=window.closeDrawer||function(id){var f=window._martinDrawerFns&&window._martinDrawerFns[id];if(f)f.close();};"
            + "if(!window._martinDrawerEscBound){window._martinDrawerEscBound=true;document.addEventListener('keydown',function(e){"
            + " if(e.key!=='Escape')return;"
            + " for(var id in (window._martinDrawerFns||{})){var d=document.getElementById(id);if(d&&d.style.display!=='none'){window._martinDrawerFns[id].close();}}"
            + "});}"
            + "</script>"
        )


class SplitPane(Widget):
    """
    Resizable two-pane layout.
    """

    def __init__(
        self,
        left=None,
        right=None,
        ratio=0.5,
        min_left=180,
        min_right=180,
        gutter=10,
        mobile_breakpoint=900,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.left = left
        self.right = right
        self.ratio = max(0.15, min(0.85, float(ratio)))
        self.min_left = max(80, int(min_left))
        self.min_right = max(80, int(min_right))
        self.gutter = max(6, int(gutter))
        self.mobile_breakpoint = max(360, int(mobile_breakpoint))
        self.uid = f"split_{_uuid.uuid4().hex[:8]}"

    def render(self):
        uid = self.uid
        extra = self._resolve_props()
        left = self.left.render() if isinstance(self.left, Widget) else str(self.left or "")
        right = self.right.render() if isinstance(self.right, Widget) else str(self.right or "")
        css = (
            f"<style>"
            f"#{uid}{{display:flex;flex-direction:row;width:100%;min-height:260px}}"
            f"#{uid}_a{{flex:0 0 {self.ratio*100:.3f}%;min-width:{self.min_left}px;overflow:auto}}"
            f"#{uid}_b{{flex:1 1 auto;min-width:{self.min_right}px;overflow:auto}}"
            f"#{uid}_g{{flex:0 0 {self.gutter}px;background:var(--border);cursor:col-resize;position:relative}}"
            f"#{uid}_g:after{{content:'';position:absolute;inset:0;background:linear-gradient(180deg,transparent,rgba(255,255,255,.12),transparent)}}"
            f"@media(max-width:{self.mobile_breakpoint}px){{#{uid}{{flex-direction:column!important}}#{uid}_g{{display:none!important}}#{uid}_a,#{uid}_b{{min-width:0!important;flex-basis:auto!important}}}}"
            f"</style>"
        )
        js = (
            f"<script>(function(){{"
            f"var root=document.getElementById('{uid}');var a=document.getElementById('{uid}_a');var g=document.getElementById('{uid}_g');"
            f"if(!root||!a||!g)return;"
            f"var drag=false,sx=0,sw=0;"
            f"g.addEventListener('mousedown',function(e){{if(window.matchMedia('(max-width:{self.mobile_breakpoint}px)').matches)return;"
            f" drag=true;sx=e.clientX;sw=a.offsetWidth;document.body.style.userSelect='none';e.preventDefault();}});"
            f"window.addEventListener('mousemove',function(e){{if(!drag)return;var dx=e.clientX-sx;var w=sw+dx;var total=root.clientWidth;"
            f" var minA={self.min_left},minB={self.min_right};if(w<minA)w=minA;if(total-w<minB)w=total-minB;a.style.flex='0 0 '+w+'px';}});"
            f"window.addEventListener('mouseup',function(){{if(!drag)return;drag=false;document.body.style.userSelect='';}});"
            f"}})();</script>"
        )
        return (
            css
            + f'<div id="{uid}" style="{extra}">'
            + f'<div id="{uid}_a">{left}</div>'
            + f'<div id="{uid}_g" aria-hidden="true"></div>'
            + f'<div id="{uid}_b">{right}</div>'
            + "</div>"
            + js
        )


class Skeleton(Widget):
    def __init__(self, lines=3, avatar=False, animated=True, line_height=12, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.lines = max(1, int(lines))
        self.avatar = bool(avatar)
        self.animated = bool(animated)
        self.line_height = max(6, int(line_height))
        self.uid = f"sk_{_uuid.uuid4().hex[:8]}"

    def render(self):
        anim = "animation:mnSkPulse 1.25s ease-in-out infinite;" if self.animated else ""
        rows = []
        for i in range(self.lines):
            w = 100 - min(i * 11, 42)
            rows.append(
                f'<div style="height:{self.line_height}px;border-radius:999px;background:var(--surface-2);width:{w}%;{anim}"></div>'
            )
        avatar = ""
        if self.avatar:
            avatar = f'<div style="width:38px;height:38px;border-radius:999px;background:var(--surface-2);{anim}flex-shrink:0"></div>'
        extra = self._resolve_props(
            "display:flex;align-items:flex-start;gap:12px;padding:12px;border:1px solid var(--border);border-radius:12px;background:var(--surface)"
        )
        return (
            "<style>@keyframes mnSkPulse{0%,100%{opacity:.45}50%{opacity:1}}</style>"
            + f'<div id="{self.uid}" style="{extra}">'
            + avatar
            + '<div style="flex:1;display:flex;flex-direction:column;gap:10px">'
            + "".join(rows)
            + "</div></div>"
        )


class EmptyState(Widget):
    def __init__(self, title="No results", description="", icon="[]", action=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.title = title
        self.description = description
        self.icon = icon
        self.action = action

    def render(self):
        action_html = ""
        if self.action is not None:
            action_html = self.action.render() if isinstance(self.action, Widget) else str(self.action)
        extra = self._resolve_props(
            "display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;"
            "padding:28px;border:1px dashed var(--border);border-radius:14px;background:var(--surface)"
        )
        return (
            f'<div style="{extra}">'
            f'<div style="font-size:28px;line-height:1;margin-bottom:8px">{self.icon}</div>'
            f'<div style="font-size:17px;font-weight:700;color:var(--text)">{self.title}</div>'
            f'<div style="font-size:13px;color:var(--text-muted);margin-top:6px;max-width:56ch">{self.description}</div>'
            f'<div style="margin-top:14px">{action_html}</div>'
            f"</div>"
        )


class ErrorState(Widget):
    def __init__(self, title="Something went wrong", description="", action=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.title = title
        self.description = description
        self.action = action

    def render(self):
        action_html = ""
        if self.action is not None:
            action_html = self.action.render() if isinstance(self.action, Widget) else str(self.action)
        extra = self._resolve_props(
            "display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;"
            "padding:28px;border:1px solid color-mix(in srgb, var(--danger,#ef4444) 50%, var(--border));"
            "border-radius:14px;background:color-mix(in srgb, var(--danger,#ef4444) 8%, var(--surface))"
        )
        return (
            f'<div style="{extra}">'
            f'<div style="font-size:28px;line-height:1;margin-bottom:8px">!</div>'
            f'<div style="font-size:17px;font-weight:700;color:var(--text)">{self.title}</div>'
            f'<div style="font-size:13px;color:var(--text-muted);margin-top:6px;max-width:56ch">{self.description}</div>'
            f'<div style="margin-top:14px">{action_html}</div>'
            f"</div>"
        )


class Form(Widget):
    """
    Advanced form:
      - sync validators
      - async validators (per-field URL)
      - masks
      - dirty/touched state
    """

    def __init__(
        self,
        children=None,
        child=None,
        id=None,
        schema=None,
        on_submit="",
        validate_on_input=True,
        validate_on_blur=True,
        prevent_default=True,
        method="post",
        action="",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        if child is not None and children is None:
            children = [child]
        self.children = children or []
        self.schema = schema or {}
        self.on_submit = on_submit or ""
        self.validate_on_input = bool(validate_on_input)
        self.validate_on_blur = bool(validate_on_blur)
        self.prevent_default = bool(prevent_default)
        self.method = str(method or "post")
        self.action = str(action or "")
        self.uid = id or f"form_{_uuid.uuid4().hex[:8]}"

    def render(self):
        uid = self.uid
        extra = self._resolve_props("display:flex;flex-direction:column;gap:12px")
        inner = self._render_children(self.children)
        schema_js = _json.dumps(self.schema, ensure_ascii=False)
        submit_js = _json.dumps(self.on_submit)
        js = (
            f"<script>(function(){{"
            f"var uid='{uid}',form=document.getElementById(uid);if(!form||form.dataset.mfBound)return;"
            f"form.dataset.mfBound='1';"
            f"var schema={schema_js};"
            f"var validateOnInput={str(self.validate_on_input).lower()};"
            f"var validateOnBlur={str(self.validate_on_blur).lower()};"
            f"var box=document.getElementById(uid+'_err');"
            f"var state={{dirty:{{}},touched:{{}},errors:{{}},initial:{{}}}};"
            f"function controls(){{return Array.prototype.slice.call(form.querySelectorAll('input[name],textarea[name],select[name]'));}}"
            f"function values(){{var out={{}};controls().forEach(function(el){{out[el.name]=el.value;}});return out;}}"
            f"function getRule(name){{return schema[name]||{{}};}}"
            f"function setErr(name,msg){{state.errors[name]=msg||'';var el=form.querySelector('[name=\"'+name.replace(/\"/g,'\\\\\"')+'\"]');if(el){{if(msg)el.classList.add('mn-invalid');else el.classList.remove('mn-invalid');el.setAttribute('aria-invalid',msg?'true':'false');}}}}"
            f"function redrawSummary(){{var arr=[];for(var k in state.errors)if(state.errors[k])arr.push(state.errors[k]);if(!box)return;if(!arr.length){{box.style.display='none';box.textContent='';return;}}box.style.display='block';box.textContent=arr[0];}}"
            f"function applyMask(raw,mask){{var out='';var ri=0;for(var i=0;i<mask.length;i++){{var m=mask[i];if(m!=='9'&&m!=='A'&&m!=='*'){{out+=m;continue;}}while(ri<raw.length){{var ch=raw[ri++];var ok=(m==='9'&&/[0-9]/.test(ch))||(m==='A'&&/[a-zA-Z]/.test(ch))||(m==='*'&&/[a-zA-Z0-9]/.test(ch));if(ok){{out+=ch;break;}}}}}}return out;}}"
            f"function syncValidate(name,val,allVals){{var r=getRule(name);var v=String(val==null?'':val);if(r.mask){{v=applyMask(v,r.mask);var el=form.querySelector('[name=\"'+name+'\"]');if(el&&el.value!==v)el.value=v;}}if(r.required&&v.trim()==='')return r.required_message||'This field is required.';if(r.email&&v&& !/^\\S+@\\S+\\.\\S+$/.test(v))return r.email_message||'Invalid email.';if(r.min_length&&v.length<Number(r.min_length))return r.min_length_message||('Minimum '+r.min_length+' characters.');if(r.max_length&&v.length>Number(r.max_length))return r.max_length_message||('Maximum '+r.max_length+' characters.');if(r.pattern){{try{{var re=new RegExp('^(?:'+r.pattern+')$');if(v&&!re.test(v))return r.pattern_message||'Invalid format.';}}catch(e){{}}}}if(r.custom_js){{try{{var msg=(new Function('value','values',r.custom_js))(v,allVals);if(msg)return String(msg);}}catch(e){{}}}}return '';}}"
            f"function asyncValidate(name,val,allVals){{var r=getRule(name);if(!r.async_url)return Promise.resolve('');return fetch(r.async_url,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{field:name,value:val,values:allVals}})}}).then(function(res){{return res.json();}}).then(function(data){{if(data&&data.valid===false)return String(data.message||'Invalid value.');return '';}}).catch(function(){{return '';}});}}"
            f"function markState(el,name){{var cur=String(el.value==null?'':el.value);state.dirty[name]=(cur!==String(state.initial[name]||''));if(state.dirty[name])el.classList.add('mn-dirty');else el.classList.remove('mn-dirty');}}"
            f"function validateOne(name,doAsync){{var el=form.querySelector('[name=\"'+name+'\"]');if(!el)return Promise.resolve('');var vals=values();var msg=syncValidate(name,el.value,vals);setErr(name,msg);if(msg||!doAsync)return Promise.resolve(msg);return asyncValidate(name,el.value,vals).then(function(am){{setErr(name,am);return am;}});}}"
            f"controls().forEach(function(el){{state.initial[el.name]=String(el.value==null?'':el.value);el.addEventListener('input',function(){{markState(el,el.name);if(validateOnInput)validateOne(el.name,false).then(redrawSummary);}});el.addEventListener('blur',function(){{state.touched[el.name]=true;el.classList.add('mn-touched');if(validateOnBlur)validateOne(el.name,true).then(redrawSummary);}});}});"
            f"window[uid+'_getState']=function(){{return {{dirty:state.dirty,touched:state.touched,errors:state.errors,values:values()}};}};"
            f"form.addEventListener('submit',function(e){{var names=controls().map(function(el){{return el.name;}});var jobs=[];for(var i=0;i<names.length;i++)jobs.push(validateOne(names[i],true));Promise.all(jobs).then(function(){{redrawSummary();var hasErr=false;for(var k in state.errors){{if(state.errors[k]){{hasErr=true;break;}}}}if({str(self.prevent_default).lower()}||hasErr)e.preventDefault();if(hasErr)return;var code={submit_js};if(code){{try{{(new Function('event','form','state',code))(e,form,window[uid+'_getState']());}}catch(err){{console.error(err);}}}}}});}});"
            f"}})();</script>"
        )
        return (
            f"<style>.mn-invalid{{border-color:var(--danger,#ef4444)!important;box-shadow:0 0 0 3px rgba(239,68,68,.2)!important}}</style>"
            + f'<form id="{uid}" method="{self.method}" action="{self.action}" style="{extra}">'
            + inner
            + f'<div id="{uid}_err" style="display:none;font-size:13px;color:var(--danger,#ef4444)"></div>'
            + "</form>"
            + js
        )


class ResourceForm(Widget):
    """
    Formulario orientado a recurso, conectado al backend por convención.
    """

    _slots = {
        "header_buttons": {"desc": "Buttons above form title"},
        "form_fields": {"desc": "Extra fields injected into the form grid"},
        "footer_actions": {"desc": "Actions below the submit button"},
    }

    def __init__(
        self,
        resource,
        fields=None,
        endpoint=None,
        title=None,
        submit_label="Guardar",
        target=None,
        method="POST",
        button_variant="primary",
        helper_text="",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.resource = str(resource or "").strip() or "resource"
        self.fields = fields or []
        self.endpoint = endpoint or f"/api/resources/{self.resource}/save"
        self.title = title
        self.submit_label = str(submit_label or "Guardar")
        self.target = target
        self.method = str(method or "POST").upper()
        self.button_variant = str(button_variant or "primary")
        self.helper_text = str(helper_text or "")
        self.uid = f"resource_form_{_uuid.uuid4().hex[:8]}"

    def _build_field_widget(self, spec):
        from .input import (
            TextField,
            TextArea,
            Select,
            Checkbox,
            NumberInput,
            DatePicker,
            TimePicker,
        )

        field = dict(spec or {})
        name = str(field.get("name") or "").strip()
        if not name:
            return None
        kind = str(field.get("type") or "text").lower()
        placeholder = field.get("placeholder") or field.get("label") or name.replace("_", " ").title()
        label = field.get("label")
        required = bool(field.get("required"))
        if kind in {"textarea", "text-area"}:
            return TextArea(name=name, placeholder=placeholder, rows=int(field.get("rows", 3)), value=field.get("value", ""))
        if kind == "select":
            return Select(
                name=name,
                options=field.get("options", []),
                value=field.get("value"),
                search=bool(field.get("search", True)),
                placeholder=placeholder,
            )
        if kind == "checkbox":
            return Checkbox(label or placeholder, name=name, checked=bool(field.get("value", False)))
        if kind == "number":
            return NumberInput(
                name=name,
                value=field.get("value"),
                min=field.get("min"),
                max=field.get("max"),
                step=field.get("step", 1),
                placeholder=placeholder,
            )
        if kind == "date":
            return DatePicker(name=name, label=label or placeholder, value=field.get("value"))
        if kind == "time":
            return TimePicker(name=name, label=label or placeholder, value=field.get("value"))
        return TextField(
            name=name,
            placeholder=placeholder,
            type="email" if kind == "email" else "text",
            value=field.get("value", ""),
            required=required,
        )

    def render(self):
        from .input import Button
        from .layout import Column, Grid, Row
        from .text import Text, Paragraph
        from ..backend.widgets import ResultBox

        field_widgets = [self._build_field_widget(spec) for spec in self.fields]
        field_widgets = [item for item in field_widgets if item is not None]
        schema = {}
        for field in self.fields:
            name = str(field.get("name") or "").strip()
            if not name:
                continue
            rule = {}
            for key in ("required", "min_length", "max_length", "pattern", "email", "async_url", "mask"):
                if key in field:
                    rule[key] = field[key]
            if rule:
                schema[name] = rule

        target_id = self.target or (self.uid + "_result")
        submit_js = (
            "var values=state.values;"
            "fetch(" + _json.dumps(self.endpoint) + ",{"
            "method:" + _json.dumps(self.method) + ","
            "headers:{'Content-Type':'application/json'},"
            "body:JSON.stringify(values)"
            "}).then(function(res){return res.json().then(function(data){return {ok:res.ok,status:res.status,data:data};});})"
            ".then(function(result){"
            "if(result.data&&(result.data.toast||result.data._toast)&&window.__martinToastFromPayload){window.__martinToastFromPayload(result.data.toast||result.data._toast);}"
            "var box=document.getElementById(" + _json.dumps(target_id) + ");"
            "if(box){box.setAttribute('data-state',result.ok?'success':'error');box._martinData=result.data;box.dispatchEvent(new CustomEvent('martin:result',{detail:result.data}));}"
            "})"
            ".catch(function(err){"
            "if(window.__martinToastFromPayload){window.__martinToastFromPayload({message:err.message||'Error de red',variant:'error',position:'top-right'});}"
            "var box=document.getElementById(" + _json.dumps(target_id) + ");"
            "if(box){box.setAttribute('data-state','error');box._martinData={error:err.message};box.dispatchEvent(new CustomEvent('martin:result',{detail:{error:err.message}}));}"
            "});"
            "event.preventDefault();"
        )

        content = []
        # Slot: header_buttons (from extending modules)
        slot_header = self.render_slot("header_buttons", {"resource": self.resource})
        if slot_header:
            content.append(Raw(slot_header))
        if self.title:
            content.append(Text(self.title, style="font-size:16px;font-weight:700;color:var(--text)"))
        if self.helper_text:
            content.append(Paragraph(self.helper_text, style="font-size:13px;color:var(--text-muted);line-height:1.6"))
        # Base form fields
        content.append(Grid(columns=2, gap=12, children=field_widgets))
        # Slot: form_fields (from extending modules)
        slot_fields = self.render_slot("form_fields", {"resource": self.resource})
        if slot_fields:
            content.append(Raw(slot_fields))
        content.append(Row(gap=10, wrap=True, children=[Button(self.submit_label, variant=self.button_variant)]))
        # Slot: footer_actions (from extending modules)
        slot_footer = self.render_slot("footer_actions", {"resource": self.resource})
        if slot_footer:
            content.append(Raw(slot_footer))
        content.append(ResultBox(id=target_id, format="json"))

        return Form(
            id=self.uid,
            schema=schema,
            on_submit=submit_js,
            children=[Column(gap=14, children=content)],
            **self._props,
        ).render()


class ResourceEditor(Widget):
    """
    Resource form that loads an existing record and saves changes back.
    """

    def __init__(
        self,
        resource,
        record_id,
        fields=None,
        endpoint=None,
        detail_endpoint=None,
        title=None,
        submit_label="Actualizar",
        target=None,
        method="PATCH",
        button_variant="primary",
        helper_text="",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.resource = str(resource or "").strip() or "resource"
        self.record_id = str(record_id if record_id is not None else "").strip()
        self.fields = fields or []
        self.endpoint = endpoint or f"/api/resources/{self.resource}/save"
        self.detail_endpoint = detail_endpoint or f"/api/resources/{self.resource}/detail"
        self.title = title
        self.submit_label = str(submit_label or "Actualizar")
        self.target = target
        self.method = str(method or "PATCH").upper()
        self.button_variant = str(button_variant or "primary")
        self.helper_text = str(helper_text or "")
        self.uid = f"resource_editor_{_uuid.uuid4().hex[:8]}"

    def render(self):
        specs = [{"name": "id", "type": "text", "value": self.record_id, "placeholder": "Id"}]
        specs.extend(list(self.fields or []))
        form = ResourceForm(
            resource=self.resource,
            fields=specs,
            endpoint=self.endpoint,
            title=self.title,
            submit_label=self.submit_label,
            target=self.target,
            method=self.method,
            button_variant=self.button_variant,
            helper_text=self.helper_text,
            style="display:block",
        )
        form_html = form.render()
        js = (
            f"<script>(function(){{"
            f"var form=document.getElementById({_json.dumps(form.uid)});"
            f"var endpoint={_json.dumps(self.detail_endpoint)};"
            f"var recordId={_json.dumps(self.record_id)};"
            f"if(!form||!recordId)return;"
            f"function escSel(v){{return String(v).replace(/([ #;?%&,.+*~\\':\\\"!^$\\[\\]()=>|\\/])/g,'\\\\$1');}}"
            f"function fillValue(name,val){{"
            f"  var el=form.querySelector('[name=\"'+String(name).replace(/\"/g,'\\\\\"')+'\"]');"
            f"  if(!el)return;"
            f"  if(el.type==='checkbox'){{el.checked=!!val;el.value=val?'true':'false';el.dispatchEvent(new Event('input',{{bubbles:true}}));return;}}"
            f"  if(el.id&&el.id.slice(-4)==='_val'&&window.pwSelectPick){{"
            f"    var uid=el.id.slice(0,-4);"
            f"    var opt=document.querySelector('#'+escSel(uid)+'_list .pw-opt[data-val=\"'+String(val).replace(/\"/g,'\\\\\"')+'\"]');"
            f"    var label=opt?opt.getAttribute('data-label'):String(val==null?'':val);"
            f"    window.pwSelectPick(uid,String(val==null?'':val),label);"
            f"    el.dispatchEvent(new Event('input',{{bubbles:true}}));"
            f"    return;"
            f"  }}"
            f"  el.value=val==null?'':String(val);"
            f"  el.dispatchEvent(new Event('input',{{bubbles:true}}));"
            f"  el.dispatchEvent(new Event('blur',{{bubbles:true}}));"
            f"}}"
            f"fetch(endpoint+(endpoint.indexOf('?')>=0?'&':'?')+'id='+encodeURIComponent(recordId))"
            f".then(function(res){{return res.json();}})"
            f".then(function(data){{"
            f"  var record=(data&&(data.record||data.item||data.data))||{{}};"
            f"  Object.keys(record).forEach(function(key){{fillValue(key,record[key]);}});"
            f"  if(data&&(data.toast||data._toast)&&window.__martinToastFromPayload)window.__martinToastFromPayload(data.toast||data._toast);"
            f"}})"
            f".catch(function(err){{if(window.__martinToastFromPayload)window.__martinToastFromPayload({{message:err.message||'Error cargando recurso',variant:'error',position:'top-right'}});}});"
            f"}})();</script>"
        )
        return f'<div style="{self._resolve_props("display:block")}">{form_html}{js}</div>'


class ResourceTable(Widget):
    """
    Tabla orientada a recurso, conectada al backend por convención.
    """

    _slots = {
        "toolbar_buttons": {"desc": "Buttons above the table toolbar"},
        "extra_columns": {"desc": "Extra columns appended to the table"},
    }

    def __init__(
        self,
        resource,
        columns=None,
        rows=None,
        endpoint=None,
        title=None,
        helper_text="",
        searchable=True,
        refresh_label="Refrescar",
        height=340,
        selectable=False,
        id_field="id",
        selection_label="Sel.",
        search_param="q",
        page_param="page",
        per_page_param="per_page",
        per_page=10,
        id=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.resource = str(resource or "").strip() or "resource"
        self.columns = columns or []
        self.rows = rows or []
        self.endpoint = endpoint or f"/api/resources/{self.resource}/list"
        self.title = title
        self.helper_text = str(helper_text or "")
        self.searchable = bool(searchable)
        self.refresh_label = str(refresh_label or "Refrescar")
        self.height = int(height or 340)
        self.selectable = bool(selectable)
        self.id_field = str(id_field or "id")
        self.selection_label = str(selection_label or "Sel.")
        self.search_param = str(search_param or "q")
        self.page_param = str(page_param or "page")
        self.per_page_param = str(per_page_param or "per_page")
        self.per_page = max(1, int(per_page or 10))
        self.uid = id or f"resource_table_{_uuid.uuid4().hex[:8]}"

    def render(self):
        from .input import Button
        from .layout import Column, Row
        from .text import Paragraph, Text
        from .special import Raw

        grid_columns = list(self.columns or [])
        if self.selectable:
            grid_columns = [DataGridColumn("__martin_select__", self.selection_label, width=72, sortable=False, align="center")] + grid_columns
        grid = DataGrid(
            rows=self.rows,
            columns=grid_columns,
            searchable=self.searchable,
            sortable=True,
            resizable=True,
            reorderable=True,
            virtual_scroll=True,
            height=self.height,
        )
        grid_html = grid.render()
        js = (
            f"<script>(function(){{"
            f"var uid='{self.uid}',endpoint={_json.dumps(self.endpoint)},activeQuery={{{_json.dumps(self.page_param)}:1,{_json.dumps(self.per_page_param)}:{self.per_page}}},selectedIds={{}},idField={_json.dumps(self.id_field)},selectable={str(self.selectable).lower()},pageParam={_json.dumps(self.page_param)},perPageParam={_json.dumps(self.per_page_param)};"
            f"function esc(v){{return String(v==null?'':v);}}"
            f"function normalizeRows(rows){{rows=Array.isArray(rows)?rows:[];if(!selectable)return rows;return rows.map(function(row){{var next=Object.assign({{}},row||{{}});var key=esc(next[idField]);next.__martin_select__=selectedIds[key]?'☑':'☐';return next;}});}}"
            f"function syncSelectionUi(){{"
            f"if(!selectable)return;"
            f"var wrap=document.getElementById(uid);"
            f"if(!wrap)return;"
            f"var body=wrap.querySelector('tbody');"
            f"if(!body)return;"
            f"var rows=Array.prototype.slice.call(body.querySelectorAll('tr'));"
            f"rows.forEach(function(tr){{"
            f"var first=tr.children&&tr.children[0];"
            f"if(!first)return;"
            f"var text=(first.textContent||'').trim();"
            f"if(text!=='☐'&&text!=='☑')return;"
            f"tr.style.cursor='pointer';"
            f"tr.setAttribute('data-martin-selectable','1');"
            f"if(first.getAttribute('data-bound')==='1')return;"
            f"first.setAttribute('data-bound','1');"
            f"tr.addEventListener('click',function(){{"
            f"var cells=this.children||[];"
            f"if(!cells.length)return;"
            f"var selectCell=cells[0];"
            f"var keyCell=cells.length>1?cells[1]:null;"
            f"var key=esc(keyCell?keyCell.textContent:'');"
            f"if(!key)return;"
            f"selectedIds[key]=!selectedIds[key];"
            f"if(!selectedIds[key])delete selectedIds[key];"
            f"if(window['{grid.uid}_setRows'])window['{grid.uid}_setRows'](normalizeRows(window[uid+'_rows']||[]));"
            f"notifySelection();"
            f"}});"
            f"}});"
            f"}}"
            f"function notifySelection(){{"
            f"var ids=Object.keys(selectedIds).filter(function(key){{return !!selectedIds[key];}});"
            f"window[uid+'_getSelectedIds']=function(){{return ids.slice();}};"
            f"window[uid+'_clearSelection']=function(){{selectedIds={{}};if(window['{grid.uid}_setRows'])window['{grid.uid}_setRows'](normalizeRows(window[uid+'_rows']||[]));notifySelection();}};"
            f"window.dispatchEvent(new CustomEvent(uid+':selectionchange',{{detail:{{ids:ids,count:ids.length}}}}));"
            f"}}"
            f"function notifyPage(data,rows){{"
            f"var meta=((data&&data.meta)||{{}});"
            f"var detail={{page:Number(meta.page||activeQuery[pageParam]||1),per_page:Number(meta.per_page||activeQuery[perPageParam]||{self.per_page}),total:Number(meta.total||rows.length||0),pages:Number(meta.pages||1),count:Array.isArray(rows)?rows.length:0}};"
            f"window[uid+'_pageState']=detail;"
            f"window.dispatchEvent(new CustomEvent(uid+':pagedata',{{detail:detail}}));"
            f"}}"
            f"window[uid+'_refresh']=function(query){{"
            f"if(query&&typeof query==='object')activeQuery=Object.assign({{}},activeQuery,query);"
            f"if(!activeQuery[pageParam])activeQuery[pageParam]=1;"
            f"if(!activeQuery[perPageParam])activeQuery[perPageParam]={self.per_page};"
            f"var qs=new URLSearchParams(activeQuery||{{}}).toString();"
            f"var finalUrl=qs?(endpoint+(endpoint.indexOf('?')>=0?'&':'?')+qs):endpoint;"
            f"fetch(finalUrl).then(function(res){{return res.json();}}).then(function(data){{"
            f"var rows=(data&& (data.rows||data.items||data.data)) || [];"
            f"window[uid+'_rows']=rows;"
            f"if(window['{grid.uid}_setRows'])window['{grid.uid}_setRows'](normalizeRows(rows));"
            f"syncSelectionUi();notifySelection();notifyPage(data,rows);"
            f"if(data&&(data.toast||data._toast)&&window.__martinToastFromPayload)window.__martinToastFromPayload(data.toast||data._toast);"
            f"}}).catch(function(err){{if(window.__martinToastFromPayload)window.__martinToastFromPayload({{message:err.message||'Error cargando recurso',variant:'error',position:'top-right'}});}});"
            f"}};"
            f"new MutationObserver(function(){{syncSelectionUi();}}).observe(document.getElementById({ _json.dumps(grid.uid + '_body') })||document.body,{{childList:true,subtree:true}});"
            f"window[uid+'_refresh']();"
            f"}})();</script>"
        )
        header_items = []
        if self.title:
            header_items.append(Text(self.title, style="font-size:16px;font-weight:700;color:var(--text)"))
        if self.helper_text:
            header_items.append(Paragraph(self.helper_text, style="font-size:13px;color:var(--text-muted);line-height:1.6"))
        header_items.append(
            Row(gap=10, wrap=True, children=[
                Button(self.refresh_label, variant="secondary", on_click=f"{self.uid}_refresh()")
            ])
        )
        return Column(children=header_items + [Raw(grid_html + js)], gap=14, **self._props).render()


class ResourceStats(Widget):
    """
    Metric cards derived from a resource endpoint.
    """

    def __init__(self, resource, metrics=None, endpoint=None, title=None, columns=3, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.resource = str(resource or "").strip() or "resource"
        self.metrics = list(metrics or [])
        self.endpoint = endpoint or f"/api/resources/{self.resource}/stats"
        self.title = title
        self.columns = max(1, int(columns or 3))
        self.uid = f"resource_stats_{_uuid.uuid4().hex[:8]}"

    def render(self):
        extra = self._resolve_props("display:block")
        metrics_js = _json.dumps(self.metrics, ensure_ascii=False)
        js = (
            f"<script>(function(){{"
            f"var box=document.getElementById({_json.dumps(self.uid + '_grid')});if(!box)return;"
            f"var metrics={metrics_js};"
            f"function esc(v){{return String(v==null?'':v);}}"
            f"fetch({_json.dumps(self.endpoint)}).then(function(res){{return res.json();}}).then(function(data){{"
            f"var stats=(data&&(data.stats||data.data||data))||{{}};"
            f"var items=Array.isArray(metrics)&&metrics.length?metrics:Object.keys(stats).map(function(key){{return {{label:key.replace(/_/g,' '),key:key}};}});"
            f"box.innerHTML=items.map(function(item){{var key=item.key||item.name||item.label;var value=stats[key];var prefix=item.prefix||'';var suffix=item.suffix||'';return '<article style=\"display:grid;gap:6px;padding:14px;border:1px solid var(--border);border-radius:16px;background:var(--surface-2,var(--surface))\"><span style=\"font-size:12px;color:var(--text-muted)\">'+esc(item.label||key)+'</span><strong style=\"font-size:24px;color:var(--text)\">'+esc(prefix)+esc(value)+esc(suffix)+'</strong></article>';}}).join('');"
            f"if(data&&(data.toast||data._toast)&&window.__martinToastFromPayload)window.__martinToastFromPayload(data.toast||data._toast);"
            f"}}).catch(function(err){{box.innerHTML='<p style=\"margin:0;color:var(--danger,#ef4444)\">'+(err.message||'Error')+'</p>';}});"
            f"}})();</script>"
        )
        title_html = f'<div style="font-size:16px;font-weight:700;color:var(--text);margin-bottom:12px">{self.title}</div>' if self.title else ""
        return f'<div style="{extra}">{title_html}<div id="{self.uid}_grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax({max(160, int(820 / self.columns))}px,1fr));gap:12px"></div>{js}</div>'


class ResourceDetails(Widget):
    """
    Vista simple de detalle conectada al backend por convención.
    """

    _slots = {
        "detail_fields": {"desc": "Extra fields shown in detail view"},
        "action_buttons": {"desc": "Buttons in the detail footer"},
    }

    def __init__(
        self,
        resource,
        endpoint=None,
        title=None,
        record_id=None,
        fields=None,
        empty_text="Sin datos",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.resource = str(resource or "").strip() or "resource"
        self.endpoint = endpoint or f"/api/resources/{self.resource}/detail"
        self.title = title
        self.record_id = record_id
        self.fields = list(fields or [])
        self.empty_text = str(empty_text or "Sin datos")
        self.uid = f"resource_details_{_uuid.uuid4().hex[:8]}"

    def render(self):
        extra = self._resolve_props("display:block")
        normalized_fields = []
        for field in self.fields:
            if isinstance(field, dict):
                name = str(field.get("name") or "").strip()
                if name:
                    normalized_fields.append({
                        "name": name,
                        "label": str(field.get("label") or name.replace("_", " ").title()),
                    })
            else:
                name = str(field or "").strip()
                if name:
                    normalized_fields.append({
                        "name": name,
                        "label": name.replace("_", " ").title(),
                    })
        fields_js = _json.dumps(normalized_fields, ensure_ascii=False)
        endpoint = self.endpoint + (f"?id={self.record_id}" if self.record_id is not None and "?" not in self.endpoint else "")
        js = (
            f"<script>(function(){{"
            f"var uid='{self.uid}',endpoint={_json.dumps(endpoint)},fields={fields_js};"
            f"var box=document.getElementById(uid+'_body'); if(!box)return;"
            f"fetch(endpoint).then(function(res){{return res.json();}}).then(function(data){{"
            f"var record=(data&&(data.record||data.item||data.data))||{{}};"
            f"var keys=Array.isArray(fields)&&fields.length?fields:Object.keys(record).map(function(key){{return {{name:key,label:String(key).replace(/_/g,' ').replace(/\\b\\w/g,function(c){{return c.toUpperCase();}})}};}});"
            f"if(!keys.length){{box.innerHTML='<p style=\"margin:0;color:var(--text-muted)\">{self.empty_text}</p>';return;}}"
            f"box.innerHTML=keys.map(function(field){{var key=field.name||field;var label=field.label||String(key);var value=record[key]==null?'':record[key];return '<div style=\"display:grid;gap:4px;padding:12px;border:1px solid var(--border);border-radius:12px;background:var(--surface-2,var(--surface))\"><span style=\"font-size:12px;color:var(--text-muted)\">'+label+'</span><strong style=\"font-size:14px;color:var(--text)\">'+value+'</strong></div>';}}).join('');"
            f"if(data&&(data.toast||data._toast)&&window.__martinToastFromPayload)window.__martinToastFromPayload(data.toast||data._toast);"
            f"}}).catch(function(err){{box.innerHTML='<p style=\"margin:0;color:var(--danger,#ef4444)\">'+(err.message||'Error')+'</p>';}});"
            f"}})();</script>"
        )
        title_html = (
            f'<div style="font-size:16px;font-weight:700;color:var(--text);margin-bottom:12px">{self.title}</div>'
            if self.title
            else ""
        )
        return (
            f'<div style="{extra}">'
            f'<div style="border:1px solid var(--border);border-radius:16px;padding:16px;background:var(--surface)">'
            f"{title_html}"
            f'<div id="{self.uid}_body" style="display:grid;gap:10px"></div>'
            f"</div>{js}</div>"
        )


class ResourceCardList(Widget):
    """
    Lista de tarjetas conectada al backend por convención.
    """

    def __init__(
        self,
        resource,
        endpoint=None,
        title=None,
        subtitle_field=None,
        badge_field=None,
        columns=3,
        empty_text="Sin elementos",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.resource = str(resource or "").strip() or "resource"
        self.endpoint = endpoint or f"/api/resources/{self.resource}/list"
        self.title = title
        self.subtitle_field = subtitle_field
        self.badge_field = badge_field
        self.columns = max(1, int(columns or 3))
        self.empty_text = str(empty_text or "Sin elementos")
        self.uid = f"resource_cards_{_uuid.uuid4().hex[:8]}"

    def render(self):
        extra = self._resolve_props("display:block")
        js = (
            f"<script>(function(){{"
            f"var uid='{self.uid}',endpoint={_json.dumps(self.endpoint)};"
            f"var grid=document.getElementById(uid+'_grid'); if(!grid)return;"
            f"fetch(endpoint).then(function(res){{return res.json();}}).then(function(data){{"
            f"var rows=(data&&(data.rows||data.items||data.data))||[];"
            f"if(!rows.length){{grid.innerHTML='<p style=\"margin:0;color:var(--text-muted)\">{self.empty_text}</p>';return;}}"
            f"grid.innerHTML=rows.map(function(item){{var title=item.nombre||item.name||item.titulo||'Item';var subtitle={_json.dumps(self.subtitle_field)}?item[{_json.dumps(self.subtitle_field)}]||'':'';var badge={_json.dumps(self.badge_field)}?item[{_json.dumps(self.badge_field)}]||'':'';return '<article style=\"display:grid;gap:10px;padding:14px;border:1px solid var(--border);border-radius:16px;background:var(--surface-2,var(--surface))\"><div style=\"display:flex;align-items:center;justify-content:space-between;gap:10px\"><strong style=\"font-size:15px;color:var(--text)\">'+title+'</strong>'+(badge?'<span style=\"display:inline-flex;padding:4px 10px;border-radius:999px;background:var(--accent);color:#fff;font-size:11px;font-weight:700\">'+badge+'</span>':'')+'</div>'+(subtitle?'<div style=\"font-size:13px;color:var(--text-muted)\">'+subtitle+'</div>':'')+'<pre style=\"margin:0;font-size:12px;color:var(--text-muted);white-space:pre-wrap\">'+JSON.stringify(item,null,2)+'</pre></article>';}}).join('');"
            f"if(data&&(data.toast||data._toast)&&window.__martinToastFromPayload)window.__martinToastFromPayload(data.toast||data._toast);"
            f"}}).catch(function(err){{grid.innerHTML='<p style=\"margin:0;color:var(--danger,#ef4444)\">'+(err.message||'Error')+'</p>';}});"
            f"}})();</script>"
        )
        title_html = (
            f'<div style="font-size:16px;font-weight:700;color:var(--text);margin-bottom:12px">{self.title}</div>'
            if self.title
            else ""
        )
        return (
            f'<div style="{extra}">'
            f"{title_html}"
            f'<div id="{self.uid}_grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax({max(180, int(840 / self.columns))}px,1fr));gap:12px"></div>'
            f"{js}</div>"
        )


class ResourceFilters(Widget):
    """
    Filtros declarativos para refrescar un ResourceTable por id.
    """

    def __init__(self, target, filters=None, title=None, button_label="Aplicar filtros", **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.target = str(target or "").strip()
        self.filters = list(filters or [])
        self.title = title
        self.button_label = str(button_label or "Aplicar filtros")
        self.uid = f"resource_filters_{_uuid.uuid4().hex[:8]}"

    def render(self):
        from .input import TextField, Select, Button
        from .layout import Column, Grid, Row
        from .text import Text

        widgets = []
        for spec in self.filters:
            item = dict(spec or {})
            name = str(item.get("name") or "").strip()
            if not name:
                continue
            kind = str(item.get("type") or "text").lower()
            placeholder = item.get("placeholder") or item.get("label") or name.replace("_", " ").title()
            if kind == "select":
                widgets.append(
                    Select(
                        id=f"{self.uid}_{name}",
                        name=name,
                        options=item.get("options", []),
                        value=item.get("value"),
                        search=bool(item.get("search", False)),
                        placeholder=placeholder,
                    )
                )
            else:
                widgets.append(
                    TextField(
                        id=f"{self.uid}_{name}",
                        name=name,
                        placeholder=placeholder,
                        value=item.get("value", ""),
                    )
                )

        apply_js = (
            "(function(){"
            f"var params={{}};"
            + "".join(
                [
                    f"var el_{idx}=document.getElementById('{self.uid}_{str((spec or {}).get('name') or '').strip()}_val')||document.getElementById('{self.uid}_{str((spec or {}).get('name') or '').strip()}');"
                    f"if(el_{idx}&&String(el_{idx}.value||'').trim())params[{_json.dumps(str((spec or {}).get('name') or '').strip())}]=el_{idx}.value;"
                    for idx, spec in enumerate(self.filters)
                    if str((spec or {}).get("name") or "").strip()
                ]
            )
            + f"if(window[{_json.dumps(self.target + '_refresh')}])window[{_json.dumps(self.target + '_refresh')}](params);"
            + "})()"
        )

        children = []
        if self.title:
            children.append(Text(self.title, style="font-size:14px;font-weight:700;color:var(--text)"))
        children.append(Grid(columns=max(1, min(3, len(widgets) or 1)), gap=12, children=widgets))
        children.append(Row(gap=10, wrap=True, children=[Button(self.button_label, variant="secondary", on_click=apply_js)]))
        return Column(gap=12, children=children, **self._props).render()


class ResourceActions(Widget):
    """
    Grupo declarativo de acciones para un recurso.
    """

    def __init__(self, actions=None, title=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.actions = list(actions or [])
        self.title = title

    def render(self):
        from .input import Button
        from .layout import Column, Row
        from .text import Text
        from ..backend.widgets import ApiCall, MethodCall

        buttons = []
        for action in self.actions:
            item = dict(action or {})
            label = str(item.get("label") or "Action")
            variant = str(item.get("variant") or "secondary")
            on_click = item.get("on_click")
            if not on_click and item.get("url"):
                on_click = ApiCall(
                    item["url"],
                    method=str(item.get("method") or "POST").upper(),
                    body=item.get("body"),
                    target=item.get("target"),
                )
            if not on_click and item.get("backend_method"):
                on_click = MethodCall(
                    item["backend_method"],
                    params=item.get("params"),
                    target=item.get("target"),
                )
            buttons.append(Button(label, variant=variant, on_click=on_click))

        children = []
        if self.title:
            children.append(Text(self.title, style="font-size:14px;font-weight:700;color:var(--text)"))
        children.append(Row(gap=10, wrap=True, children=buttons))
        return Column(gap=12, children=children, **self._props).render()


class ResourceBulkActions(Widget):
    """
    Bulk actions bound to a selectable ResourceTable.
    """

    def __init__(self, target, actions=None, title=None, empty_message="Selecciona al menos un registro.", **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.target = str(target or "").strip()
        self.actions = list(actions or [])
        self.title = title
        self.empty_message = str(empty_message or "Selecciona al menos un registro.")

    def render(self):
        from .input import Button
        from .layout import Column, Row
        from .text import Text

        buttons = []
        for idx, action in enumerate(self.actions):
            item = dict(action or {})
            label = str(item.get("label") or f"Action {idx + 1}")
            variant = str(item.get("variant") or "secondary")
            method = str(item.get("method") or "POST").upper()
            endpoint = str(item.get("url") or item.get("endpoint") or "").strip()
            backend_method = str(item.get("backend_method") or "").strip()
            payload = item.get("body") if isinstance(item.get("body"), dict) else {}
            target = item.get("target")
            confirm_message = item.get("confirm_message")
            js = (
                "(function(){"
                + f"var ids=(window[{_json.dumps(self.target + '_getSelectedIds')}]?window[{_json.dumps(self.target + '_getSelectedIds')}]():[])||[];"
                + f"if(!ids.length){{if(window.__martinToastFromPayload)window.__martinToastFromPayload({{message:{_json.dumps(self.empty_message)},variant:'warning',position:'top-right'}});return;}}"
                + (f"if(!confirm({_json.dumps(confirm_message)}))return;" if confirm_message else "")
            )
            if endpoint:
                js += (
                    "fetch("
                    + _json.dumps(endpoint)
                    + ",{method:"
                    + _json.dumps(method)
                    + ",headers:{'Content-Type':'application/json'},body:JSON.stringify(Object.assign({},"
                    + _json.dumps(payload, ensure_ascii=False)
                    + ",{ids:ids}))})"
                )
            elif backend_method:
                js += (
                    "fetch('/api/_method',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({method:"
                    + _json.dumps(backend_method)
                    + ",params:Object.assign({},"
                    + _json.dumps(payload, ensure_ascii=False)
                    + ",{ids:ids})})})"
                )
            else:
                js += "Promise.resolve({ok:true,json:function(){return Promise.resolve({ids:ids});}})"
            js += (
                ".then(function(res){return res.json().then(function(data){return {ok:res.ok,data:data};});})"
                ".then(function(result){"
                "if(result.data&&(result.data.toast||result.data._toast)&&window.__martinToastFromPayload){window.__martinToastFromPayload(result.data.toast||result.data._toast);}"
            )
            if target:
                js += (
                    "var box=document.getElementById("
                    + _json.dumps(target)
                    + ");if(box){box.setAttribute('data-state',result.ok?'success':'error');box._martinData=result.data;box.dispatchEvent(new CustomEvent('martin:result',{detail:result.data}));}"
                )
            js += (
                f"if(window[{_json.dumps(self.target + '_refresh')}])window[{_json.dumps(self.target + '_refresh')}]();"
                f"if(window[{_json.dumps(self.target + '_clearSelection')}])window[{_json.dumps(self.target + '_clearSelection')}]();"
                "})"
                ".catch(function(err){if(window.__martinToastFromPayload){window.__martinToastFromPayload({message:err.message||'Error de red',variant:'error',position:'top-right'});}});"
                "})()"
            )
            buttons.append(Button(label, variant=variant, on_click=js))

        children = []
        if self.title:
            children.append(Text(self.title, style="font-size:14px;font-weight:700;color:var(--text)"))
        children.append(Row(gap=10, wrap=True, children=buttons))
        return Column(gap=12, children=children, **self._props).render()


class ResourceToolbar(Widget):
    """
    Search and quick actions toolbar for resource widgets.
    """

    def __init__(
        self,
        target,
        title=None,
        search_placeholder="Buscar registros...",
        search_param="q",
        show_selected_count=True,
        actions=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.target = str(target or "").strip()
        self.title = title
        self.search_placeholder = str(search_placeholder or "Buscar registros...")
        self.search_param = str(search_param or "q")
        self.show_selected_count = bool(show_selected_count)
        self.actions = list(actions or [])
        self.uid = f"resource_toolbar_{_uuid.uuid4().hex[:8]}"

    def render(self):
        from .input import Button, TextField
        from .layout import Column, Row
        from .special import Raw
        from .text import Text

        action_buttons = []
        for item in self.actions:
            action = dict(item or {})
            action_buttons.append(
                Button(
                    str(action.get("label") or "Action"),
                    variant=str(action.get("variant") or "secondary"),
                    on_click=action.get("on_click"),
                )
            )

        count_html = (
            f'<span id="{self.uid}_count" style="display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border:1px solid var(--border);border-radius:999px;background:var(--surface-2,var(--surface));color:var(--text-muted);font-size:12px">0 seleccionados</span>'
            if self.show_selected_count
            else ""
        )
        input_widget = TextField(
            id=f"{self.uid}_search",
            placeholder=self.search_placeholder,
        )
        search_js = (
            "(function(){"
            + f"var input=document.getElementById({_json.dumps(self.uid + '_search')});"
            + "if(!input)return;"
            + f"var fn=window[{_json.dumps(self.target + '_refresh')}];"
            + "if(typeof fn!=='function')return;"
            + "fn({"
            + _json.dumps(self.search_param)
            + ":input.value||''});"
            + "})()"
        )
        bind_js = (
            f"<script>(function(){{"
            f"var count=document.getElementById({_json.dumps(self.uid + '_count')});"
            f"if(!count)return;"
            f"window.addEventListener({_json.dumps(self.target + ':selectionchange')},function(ev){{"
            f"var detail=(ev&&ev.detail)||{{}};count.textContent=String(detail.count||0)+' seleccionados';"
            f"}});"
            f"}})();</script>"
        )
        children = []
        if self.title:
            children.append(Text(self.title, style="font-size:14px;font-weight:700;color:var(--text)"))
        children.append(
            Row(
                gap=10,
                wrap=True,
                align="center",
                children=[input_widget, Button("Buscar", variant="secondary", on_click=search_js)] + ([Raw(count_html)] if count_html else []) + action_buttons,
            )
        )
        children.append(Raw(bind_js))
        return Column(gap=12, children=children, **self._props).render()


class ResourcePaginator(Widget):
    """
    Pagination controls bound to a ResourceTable.
    """

    def __init__(self, target, title=None, page_param="page", per_page_param="per_page", per_page_options=None, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.target = str(target or "").strip()
        self.title = title
        self.page_param = str(page_param or "page")
        self.per_page_param = str(per_page_param or "per_page")
        self.per_page_options = list(per_page_options or [5, 10, 20, 50])
        self.uid = f"resource_paginator_{_uuid.uuid4().hex[:8]}"

    def render(self):
        from .input import Button, Select
        from .layout import Column, Row
        from .special import Raw
        from .text import Text

        per_page_select = Select(
            id=f"{self.uid}_per_page",
            options=[(str(v), str(v)) for v in self.per_page_options],
            value=str(self.per_page_options[1] if len(self.per_page_options) > 1 else self.per_page_options[0]),
            width=110,
        )
        prev_js = (
            "(function(){"
            + f"var state=window[{_json.dumps(self.target + '_pageState')}]||{{page:1,per_page:10}};"
            + f"if(window[{_json.dumps(self.target + '_refresh')}])window[{_json.dumps(self.target + '_refresh')}]({{{_json.dumps(self.page_param)}:Math.max(1,(state.page||1)-1),{_json.dumps(self.per_page_param)}:state.per_page||10}});"
            + "})()"
        )
        next_js = (
            "(function(){"
            + f"var state=window[{_json.dumps(self.target + '_pageState')}]||{{page:1,pages:1,per_page:10}};"
            + f"if(window[{_json.dumps(self.target + '_refresh')}])window[{_json.dumps(self.target + '_refresh')}]({{{_json.dumps(self.page_param)}:Math.min(state.pages||1,(state.page||1)+1),{_json.dumps(self.per_page_param)}:state.per_page||10}});"
            + "})()"
        )
        bind_js = (
            f"<script>(function(){{"
            f"var label=document.getElementById({_json.dumps(self.uid + '_label')});"
            f"var perPage=document.getElementById({_json.dumps(self.uid + '_per_page_val')})||document.getElementById({_json.dumps(self.uid + '_per_page')});"
            f"function sync(detail){{if(label)label.textContent='Página '+String(detail.page||1)+' de '+String(detail.pages||1)+' · '+String(detail.total||0)+' registros'; if(perPage)perPage.value=String(detail.per_page||perPage.value||10);}}"
            f"window.addEventListener({_json.dumps(self.target + ':pagedata')},function(ev){{sync((ev&&ev.detail)||{{}});}});"
            f"if(perPage)perPage.addEventListener('change',function(){{if(window[{_json.dumps(self.target + '_refresh')}])window[{_json.dumps(self.target + '_refresh')}]({{{_json.dumps(self.page_param)}:1,{_json.dumps(self.per_page_param)}:this.value||10}});}});"
            f"}})();</script>"
        )
        children = []
        if self.title:
            children.append(Text(self.title, style="font-size:14px;font-weight:700;color:var(--text)"))
        children.append(Row(gap=10, wrap=True, align="center", children=[
            Button("Anterior", variant="secondary", on_click=prev_js),
            Raw(f'<span id="{self.uid}_label" style="font-size:13px;color:var(--text-muted)">Página 1 de 1 · 0 registros</span>'),
            Button("Siguiente", variant="secondary", on_click=next_js),
            Raw('<span style="font-size:13px;color:var(--text-muted)">Por página</span>'),
            per_page_select,
        ]))
        children.append(Raw(bind_js))
        return Column(gap=12, children=children, **self._props).render()


class ResourceCreateButton(Widget):
    """
    Quick create button for a resource using convention-based save endpoints.
    """

    def __init__(
        self,
        resource,
        body=None,
        label="Crear",
        endpoint=None,
        target=None,
        variant="primary",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.resource = str(resource or "").strip() or "resource"
        self.body = body or {}
        self.label = str(label or "Crear")
        self.endpoint = endpoint or f"/api/resources/{self.resource}/save"
        self.target = target
        self.variant = str(variant or "primary")

    def render(self):
        from .input import Button
        from ..backend.widgets import ApiCall

        return Button(
            self.label,
            variant=self.variant,
            on_click=ApiCall(self.endpoint, method="POST", body=self.body, target=self.target),
            **self._props,
        ).render()


class ResourceDuplicateButton(Widget):
    """
    Duplicate an existing resource record with small overrides.
    """

    def __init__(
        self,
        resource,
        record_id,
        body=None,
        label="Duplicar",
        endpoint=None,
        target=None,
        variant="secondary",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.resource = str(resource or "").strip() or "resource"
        self.record_id = str(record_id if record_id is not None else "").strip()
        self.body = body or {}
        self.label = str(label or "Duplicar")
        self.endpoint = endpoint or f"/api/resources/{self.resource}/duplicate"
        self.target = target
        self.variant = str(variant or "secondary")

    def render(self):
        from .input import Button
        from ..backend.widgets import ApiCall

        payload = {"id": self.record_id}
        if isinstance(self.body, dict):
            payload.update(self.body)
        return Button(
            self.label,
            variant=self.variant,
            on_click=ApiCall(self.endpoint, method="POST", body=payload, target=self.target),
            **self._props,
        ).render()


class ResourceDeleteButton(Widget):
    """
    Reusable delete action for convention-based resources.
    """

    def __init__(
        self,
        resource,
        record_id,
        label="Eliminar",
        endpoint=None,
        target=None,
        variant="danger",
        confirm_message="¿Eliminar este registro?",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.resource = str(resource or "").strip() or "resource"
        self.record_id = str(record_id if record_id is not None else "").strip()
        self.label = str(label or "Eliminar")
        self.endpoint = endpoint or f"/api/resources/{self.resource}/delete"
        self.target = target
        self.variant = str(variant or "danger")
        self.confirm_message = str(confirm_message or "¿Eliminar este registro?")

    def render(self):
        from .input import Button

        js = (
            "(function(){"
            + f"if(!confirm({_json.dumps(self.confirm_message)}))return;"
            + "fetch("
            + _json.dumps(self.endpoint)
            + ",{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:"
            + _json.dumps(self.record_id)
            + "})})"
            + ".then(function(res){return res.json().then(function(data){return {ok:res.ok,data:data};});})"
            + ".then(function(result){"
            + "if(result.data&&(result.data.toast||result.data._toast)&&window.__martinToastFromPayload){window.__martinToastFromPayload(result.data.toast||result.data._toast);}"
            + (
                "var box=document.getElementById(" + _json.dumps(self.target) + ");"
                "if(box){box.setAttribute('data-state',result.ok?'success':'error');box._martinData=result.data;box.dispatchEvent(new CustomEvent('martin:result',{detail:result.data}));}"
                if self.target
                else ""
            )
            + "})"
            + ".catch(function(err){if(window.__martinToastFromPayload){window.__martinToastFromPayload({message:err.message||'Error de red',variant:'error',position:'top-right'});}});"
            + "})()"
        )
        return Button(self.label, variant=self.variant, on_click=js, **self._props).render()


class ResourceKanban(Widget):
    """
    Kanban board grouped by a resource field.
    """

    def __init__(self, resource, endpoint=None, title=None, group_field="estado", columns=None, title_field="nombre", subtitle_field="email", badge_field="plan", empty_text="Sin registros", **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.resource = str(resource or "").strip() or "resource"
        self.endpoint = endpoint or f"/api/resources/{self.resource}/list?per_page=9999"
        self.title = title
        self.group_field = str(group_field or "estado")
        self.columns = list(columns or [])
        self.title_field = str(title_field or "nombre")
        self.subtitle_field = str(subtitle_field or "email")
        self.badge_field = str(badge_field or "plan")
        self.empty_text = str(empty_text or "Sin registros")
        self.uid = f"resource_kanban_{_uuid.uuid4().hex[:8]}"

    def render(self):
        extra = self._resolve_props("display:block")
        js = (
            f"<script>(function(){{"
            f"var board=document.getElementById({_json.dumps(self.uid + '_board')});if(!board)return;"
            f"var configured={_json.dumps(self.columns, ensure_ascii=False)};"
            f"fetch({_json.dumps(self.endpoint)}).then(function(res){{return res.json();}}).then(function(data){{"
            f"var rows=(data&&(data.rows||data.items||data.data))||[];"
            f"if(!rows.length){{board.innerHTML='<p style=\"margin:0;color:var(--text-muted)\">{self.empty_text}</p>';return;}}"
            f"var groups={{}};rows.forEach(function(row){{var key=String((row&&row[{_json.dumps(self.group_field)}])||'Sin grupo'); if(!groups[key])groups[key]=[]; groups[key].push(row);}});"
            f"var order=Array.isArray(configured)&&configured.length?configured:Object.keys(groups);"
            f"board.innerHTML=order.map(function(group){{var items=groups[group]||[];return '<section style=\"display:grid;gap:12px;align-content:start;padding:12px;border:1px solid var(--border);border-radius:16px;background:var(--surface-2,var(--surface))\"><div style=\"display:flex;align-items:center;justify-content:space-between;gap:8px\"><strong style=\"color:var(--text)\">'+group+'</strong><span style=\"font-size:12px;color:var(--text-muted)\">'+String(items.length)+'</span></div>'+(items.length?items.map(function(item){{var title=item[{_json.dumps(self.title_field)}]||'Item';var subtitle=item[{_json.dumps(self.subtitle_field)}]||'';var badge=item[{_json.dumps(self.badge_field)}]||'';return '<article style=\"display:grid;gap:8px;padding:12px;border:1px solid var(--border);border-radius:14px;background:var(--surface)\"><div style=\"display:flex;align-items:center;justify-content:space-between;gap:8px\"><strong style=\"font-size:14px;color:var(--text)\">'+title+'</strong>'+(badge?'<span style=\"display:inline-flex;padding:4px 8px;border-radius:999px;background:var(--accent);color:#fff;font-size:11px;font-weight:700\">'+badge+'</span>':'')+'</div>'+(subtitle?'<div style=\"font-size:12px;color:var(--text-muted)\">'+subtitle+'</div>':'')+'</article>';}}).join(''):'<p style=\"margin:0;color:var(--text-muted)\">{self.empty_text}</p>')+'</section>';}}).join('');"
            f"}}).catch(function(err){{board.innerHTML='<p style=\"margin:0;color:var(--danger,#ef4444)\">'+(err.message||'Error')+'</p>';}});"
            f"}})();</script>"
        )
        title_html = f'<div style="font-size:16px;font-weight:700;color:var(--text);margin-bottom:12px">{self.title}</div>' if self.title else ""
        return f'<div style="{extra}">{title_html}<div id="{self.uid}_board" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:12px"></div>{js}</div>'


class ResourceView(Widget):
    """
    Composite resource view: filters + actions + table + optional details/cards.
    """

    _slots = {
        "view_sections": {"desc": "Extra sections in the resource view"},
    }

    def __init__(
        self,
        resource,
        columns=None,
        form_fields=None,
        filters=None,
        actions=None,
        toolbar_actions=None,
        bulk_actions=None,
        detail_fields=None,
        show_stats=False,
        stats_metrics=None,
        show_paginator=False,
        show_kanban=False,
        show_form=True,
        show_table=True,
        show_toolbar=True,
        show_bulk_actions=False,
        show_details=True,
        show_cards=False,
        table_id=None,
        title=None,
        helper_text="",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.resource = str(resource or "").strip() or "resource"
        self.columns = list(columns or [])
        self.form_fields = list(form_fields or [])
        self.filters = list(filters or [])
        self.actions = list(actions or [])
        self.toolbar_actions = list(toolbar_actions or [])
        self.bulk_actions = list(bulk_actions or [])
        self.detail_fields = list(detail_fields or [])
        self.show_stats = bool(show_stats)
        self.stats_metrics = list(stats_metrics or [])
        self.show_paginator = bool(show_paginator)
        self.show_kanban = bool(show_kanban)
        self.show_form = bool(show_form)
        self.show_table = bool(show_table)
        self.show_toolbar = bool(show_toolbar)
        self.show_bulk_actions = bool(show_bulk_actions)
        self.show_details = bool(show_details)
        self.show_cards = bool(show_cards)
        self.table_id = str(table_id or f"{self.resource}_table")
        self.title = title
        self.helper_text = str(helper_text or "")

    def render(self):
        from .layout import Column
        from .text import Text, Paragraph

        blocks = []
        if self.title:
            blocks.append(Text(self.title, style="font-size:18px;font-weight:700;color:var(--text)"))
        if self.helper_text:
            blocks.append(Paragraph(self.helper_text, style="font-size:13px;color:var(--text-muted);line-height:1.6"))
        if self.show_stats:
            blocks.append(ResourceStats(resource=self.resource, title="Resumen", metrics=self.stats_metrics))
        if self.show_form and self.form_fields:
            blocks.append(
                ResourceForm(
                    resource=self.resource,
                    title="Nuevo registro",
                    fields=self.form_fields,
                )
            )
        if self.show_toolbar:
            blocks.append(
                ResourceToolbar(
                    target=self.table_id,
                    title="Toolbar",
                    actions=self.toolbar_actions,
                )
            )
        if self.actions:
            blocks.append(ResourceActions(title="Acciones", actions=self.actions))
        if self.filters:
            blocks.append(ResourceFilters(target=self.table_id, title="Filtros", filters=self.filters))
        if self.show_bulk_actions and self.bulk_actions:
            blocks.append(ResourceBulkActions(target=self.table_id, title="Acciones masivas", actions=self.bulk_actions))
        if self.show_table:
            blocks.append(
                ResourceTable(
                    id=self.table_id,
                    resource=self.resource,
                    title="Registros",
                    columns=self.columns,
                    selectable=self.show_bulk_actions and bool(self.bulk_actions),
                )
            )
        if self.show_paginator:
            blocks.append(ResourcePaginator(target=self.table_id, title="Paginación"))
        if self.show_details:
            blocks.append(
                ResourceDetails(
                    resource=self.resource,
                    title="Detalle",
                    record_id="1",
                    fields=self.detail_fields or [],
                )
            )
        if self.show_cards:
            blocks.append(
                ResourceCardList(
                    resource=self.resource,
                    title="Tarjetas",
                    subtitle_field="email",
                    badge_field="estado",
                )
            )
        if self.show_kanban:
            blocks.append(
                ResourceKanban(
                    resource=self.resource,
                    title="Kanban",
                )
            )
        return Column(gap=14, children=blocks, **self._props).render()


class JSWidgetAdapter(Widget):
    """
    Generic JavaScript adapter with Python API.
    """

    def __init__(
        self,
        init_js,
        data=None,
        scripts=None,
        stylesheets=None,
        height=260,
        id=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.init_js = str(init_js or "")
        self.data = data if data is not None else {}
        self.scripts = list(scripts or [])
        self.stylesheets = list(stylesheets or [])
        self.height = max(80, int(height))
        self.uid = id or f"jsa_{_uuid.uuid4().hex[:8]}"

    def render(self):
        uid = self.uid
        extra = self._resolve_props(
            f"height:{self.height}px;border:1px solid var(--border);border-radius:12px;background:var(--surface);overflow:hidden;position:relative"
        )
        data_js = _json.dumps(self.data, ensure_ascii=False)
        scripts_js = _json.dumps(self.scripts, ensure_ascii=False)
        styles_js = _json.dumps(self.stylesheets, ensure_ascii=False)
        init_js = _json.dumps(self.init_js, ensure_ascii=False)
        return (
            f'<div id="{uid}" style="{extra}"></div>'
            + "<script>(function(){"
            + f"var uid='{uid}',el=document.getElementById(uid);if(!el)return;"
            + f"var data={data_js},scripts={scripts_js},styles={styles_js},code={init_js};"
            + "window._mnLoadCss=window._mnLoadCss||function(href){"
            + "  return new Promise(function(ok){"
            + "    if(document.querySelector('link[data-mn=\"'+href+'\"]'))return ok();"
            + "    var l=document.createElement('link');l.rel='stylesheet';l.href=href;l.setAttribute('data-mn',href);"
            + "    l.onload=function(){ok();};l.onerror=function(){ok();};document.head.appendChild(l);"
            + "  });"
            + "};"
            + "window._mnLoadScript=window._mnLoadScript||function(src){"
            + "  return new Promise(function(ok){"
            + "    if(document.querySelector('script[data-mn=\"'+src+'\"]'))return ok();"
            + "    var s=document.createElement('script');s.src=src;s.async=true;s.setAttribute('data-mn',src);"
            + "    s.onload=function(){ok();};s.onerror=function(){ok();};document.head.appendChild(s);"
            + "  });"
            + "};"
            + "Promise.all(styles.map(window._mnLoadCss)).then(function(){"
            + "  return Promise.all(scripts.map(window._mnLoadScript));"
            + "}).then(function(){"
            + "  if(el.dataset.martinJsReady)return;"
            + "  el.dataset.martinJsReady='1';"
            + "  try{(new Function('el','data',code))(el,data);}catch(e){console.error(e);el.innerHTML='<pre style=\"padding:12px;color:var(--danger,#ef4444)\">JS adapter error</pre>';}"
            + "});"
            + "})();</script>"
        )
