"""
Martin advanced widgets.
"""

import json as _json

from ..widget import Widget

__all__ = [
    "DataGridColumn",
    "DataGrid",
    "CommandPalette",
    "Drawer",
    "SplitPane",
    "Skeleton",
    "EmptyState",
    "ErrorState",
    "Form",
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

    _id_counter = 0

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
        DataGrid._id_counter += 1
        self.uid = f"dg_{DataGrid._id_counter}"

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


class CommandPalette(Widget):
    """
    Global command palette (Ctrl/Cmd+K).
    """

    _id_counter = 0

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
        CommandPalette._id_counter += 1
        self.uid = f"cmd_{CommandPalette._id_counter}"

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

    _id_counter = 0

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
        SplitPane._id_counter += 1
        self.uid = f"split_{SplitPane._id_counter}"

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
    _id_counter = 0

    def __init__(self, lines=3, avatar=False, animated=True, line_height=12, **kwargs):
        self._props = Widget._extract_props(kwargs)
        self.lines = max(1, int(lines))
        self.avatar = bool(avatar)
        self.animated = bool(animated)
        self.line_height = max(6, int(line_height))
        Skeleton._id_counter += 1
        self.uid = f"sk_{Skeleton._id_counter}"

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

    _id_counter = 0

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
        Form._id_counter += 1
        self.uid = id or f"form_{Form._id_counter}"

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


class JSWidgetAdapter(Widget):
    """
    Generic JavaScript adapter with Python API.
    """

    _id_counter = 0

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
        JSWidgetAdapter._id_counter += 1
        self.uid = id or f"jsa_{JSWidgetAdapter._id_counter}"

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
