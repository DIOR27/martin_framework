"""
Martin — Data Widgets

Widgets para mostrar información estructurada.

    Table — tabla interactiva con sort, búsqueda, paginación y exportación
"""

import json as _j
import re as _re

from ..widget import Widget


# =============================================================================
# Table
# =============================================================================


class Table(Widget):
    """
    Tabla de datos interactiva con sort por columna, búsqueda, paginación y exportación.

    Uso básico:
        Table(
            headers=["Nombre", "Email", "Rol"],
            rows=[
                ["Ana García",   "ana@email.com",   "Admin"],
                ["Pedro López",  "pedro@email.com", "Editor"],
            ],
        )

    Con todas las funciones:
        Table(
            headers=[...], rows=[...],
            searchable=True,   # barra de búsqueda global + filtro por columna
            sortable=True,     # clic en cabecera para ordenar asc/desc
            page_size=10,      # paginación
            export_formats=["csv", "json", "excel", "pdf"],
        )

    Con widgets en celdas (funcionales; no participan en sort/search):
        Table(
            headers=["Usuario", "Estado", "Acción"],
            rows=[
                [Row([Avatar(initials="AG"), Text("Ana")]),
                 Badge("Activo"),
                 Button("Ver")],
            ],
        )

    Parámetros:
        headers    list        nombres de columna
        rows       list[list]  filas — cada celda puede ser str o Widget
        striped    bool        filas alternadas (default: True)
        bordered   bool        bordes en celdas (default: True)
        searchable bool        búsqueda global + filtros por columna (default: False)
        sortable   bool        ordenación al clic en encabezado (default: False)
        page_size  int | None  filas por página, None = sin paginación
        export_formats list    formatos de exportación: csv/json/excel/pdf
        export_filename str    nombre base del archivo exportado
        export_scope   str     "filtered" (default) o "page"
    """

    _id_counter = 0

    def __init__(
        self,
        headers=None,
        rows=None,
        striped=True,
        bordered=True,
        searchable=False,
        sortable=False,
        page_size=None,
        export_formats=None,
        export_filename="table_export",
        export_scope="filtered",
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.headers = headers or []
        self.rows = rows or []
        self.striped = striped
        self.bordered = bordered
        self.searchable = searchable
        self.sortable = sortable
        self.page_size = page_size
        self.export_formats = self._normalize_export_formats(export_formats)
        self.export_filename = str(export_filename or "table_export")
        self.export_scope = "page" if export_scope == "page" else "filtered"
        Table._id_counter += 1
        self.uid = f"tbl_{Table._id_counter}"

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_plain(cell):
        """Extrae texto plano de una celda (str o Widget) para sort/search."""
        if isinstance(cell, Widget):
            h = cell.render()
            t = _re.sub(r"<[^>]+>", " ", h)
            t = (
                t.replace("&amp;", "&")
                .replace("&lt;", "<")
                .replace("&gt;", ">")
                .replace("&nbsp;", " ")
            )
            return " ".join(t.split())
        return str(cell)

    @staticmethod
    def _normalize_export_formats(value):
        if value is True:
            value = ["csv", "json", "excel", "pdf"]
        if not value:
            return []
        allowed = {"csv", "json", "excel", "pdf"}
        out = []
        for item in value:
            fmt = str(item).strip().lower()
            if fmt in allowed and fmt not in out:
                out.append(fmt)
        return out

    # ------------------------------------------------------------------
    # render
    # ------------------------------------------------------------------

    def render(self):
        uid = self.uid
        border_cell = "border:1px solid var(--border);" if self.bordered else ""
        base = "width:100%;border-collapse:collapse;font-size:14px"
        extra = self._resolve_props()
        wrapper_style = "width:100%;overflow-x:auto"
        if extra:
            wrapper_style += ";" + extra

        ncols = len(self.headers)

        # ── thead ─────────────────────────────────────────────────────
        th_base = (
            f"{border_cell}padding:10px 16px;text-align:left;"
            f"background:var(--surface-2,var(--surface));"
            f"color:var(--text);font-weight:600;white-space:nowrap;"
            f"user-select:none"
        )
        if self.sortable:
            th_base += ";cursor:pointer;transition:background .15s"

        ths = ""
        for i, h in enumerate(self.headers):
            sort_attr = f' data-col="{i}"' if self.sortable else ""
            icon_span = (
                f'<span id="{uid}_si{i}" style="margin-left:5px;'
                f'font-size:10px;color:var(--text-muted)">⇅</span>'
                if self.sortable
                else ""
            )
            col_search = ""
            if self.searchable:
                col_search = (
                    f'<input type="text" placeholder="Filtrar..." '
                    f'data-col-search="{i}" '
                    f'oninput="{uid}_colFilter(this,{i})" '
                    f'onclick="event.stopPropagation()" '
                    f'style="display:block;margin-top:6px;width:100%;'
                    f"box-sizing:border-box;padding:4px 8px;font-size:12px;"
                    f"border:1px solid var(--border);border-radius:5px;"
                    f"background:var(--surface);color:var(--text);outline:none;"
                    f'font-weight:400"/>'
                )
            ths += (
                f'<th style="{th_base}"{sort_attr}>'
                f'<div style="display:flex;align-items:center">{h}{icon_span}</div>'
                f"{col_search}</th>"
            )

        thead = f"<thead><tr>{ths}</tr></thead>" if self.headers else ""

        # ── tbody ─────────────────────────────────────────────────────
        td_style = (
            f"{border_cell}padding:10px 16px;color:var(--text);vertical-align:middle"
        )
        rows_data = []  # list of (plain_texts[], html_cells[])

        for row in self.rows:
            plain, html = [], []
            for cell in row:
                plain.append(self._to_plain(cell))
                html.append(cell.render() if isinstance(cell, Widget) else str(cell))
            rows_data.append((plain, html))

        tbody_rows = ""
        for i, (plain, html_cells) in enumerate(rows_data):
            stripe = (
                "background:var(--surface-2,rgba(0,0,0,0.03))"
                if self.striped and i % 2 == 1
                else ""
            )
            cells = "".join(
                f'<td style="{td_style};{stripe}" data-v="{_j.dumps(plain[ci])}">'
                f"{html_cells[ci]}</td>"
                for ci in range(len(html_cells))
            )
            tbody_rows += f'<tr id="{uid}_r{i}">{cells}</tr>'

        tbody = f"<tbody id='{uid}_tbody'>{tbody_rows}</tbody>"

        rows_plain_js = _j.dumps([p for p, _ in rows_data])

        # ── toolbar (search + export) ─────────────────────────────────
        global_search = ""
        if self.searchable:
            global_search = (
                f'<div style="margin-bottom:10px">'
                f'<input id="{uid}_gsearch" type="text" placeholder="Buscar en toda la tabla..."'
                f' oninput="{uid}_globalFilter(this.value)"'
                f' style="padding:7px 12px;border:1px solid var(--border);border-radius:7px;'
                f"font-size:13px;width:100%;box-sizing:border-box;background:var(--surface);"
                f'color:var(--text);outline:none"/>'
                f"</div>"
            )

        export_buttons = ""
        if self.export_formats:
            labels = {
                "csv": "CSV",
                "json": "JSON",
                "excel": "EXCEL",
                "pdf": "PDF",
            }
            btn_style = (
                "padding:6px 10px;border:1px solid var(--border);border-radius:7px;"
                "background:var(--surface);color:var(--text);font-size:12px;cursor:pointer"
            )
            export_buttons = (
                f'<div style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px">'
                + "".join(
                    f'<button type="button" data-export="{fmt}" '
                    f'onclick="{uid}_export(\'{fmt}\')" style="{btn_style}">'
                    f"Exportar {labels[fmt]}</button>"
                    for fmt in self.export_formats
                )
                + "</div>"
            )

        # ── pagination bar ─────────────────────────────────────────────
        pagination_html = ""
        if self.page_size:
            pagination_html = (
                f'<div id="{uid}_pgbar" style="display:flex;align-items:center;'
                f'justify-content:space-between;margin-top:10px;gap:8px;flex-wrap:wrap">'
                f'<span id="{uid}_pginfo" style="font-size:12px;color:var(--text-muted)"></span>'
                f'<div style="display:flex;gap:4px">'
                f'<button onclick="{uid}_pg(-1)" id="{uid}_pgprev"'
                f' style="padding:4px 14px;border:1px solid var(--border);border-radius:6px;'
                f'background:var(--surface);color:var(--text);cursor:pointer;font-size:13px">&#8592;</button>'
                f'<button onclick="{uid}_pg(1)" id="{uid}_pgnext"'
                f' style="padding:4px 14px;border:1px solid var(--border);border-radius:6px;'
                f'background:var(--surface);color:var(--text);cursor:pointer;font-size:13px">&#8594;</button>'
                f"</div></div>"
            )

        # ── JavaScript ────────────────────────────────────────────────
        needs_js = (
            self.searchable
            or self.sortable
            or bool(self.page_size)
            or bool(self.export_formats)
        )
        js = ""

        if needs_js:
            n = len(rows_data)
            ps = self.page_size or n or 1
            headers_plain_js = _j.dumps([self._to_plain(h) for h in self.headers])
            export_formats_js = _j.dumps(self.export_formats)
            export_filename_js = _j.dumps(self.export_filename)
            export_scope_js = _j.dumps(self.export_scope)

            js = (
                f"<script>(function(){{"
                f"var uid={_j.dumps(uid)};"
                f"var _data={rows_plain_js};"
                f"var _headers={headers_plain_js};"
                f"var _n={n};"
                f"var _ps={ps};"
                f"var _page=0;"
                f"var _sortCol=-1,_sortAsc=true;"
                f'var _globalQ="";'
                f'var _colQ=new Array({ncols}).fill("");'
                f"var _order=[];"
                f"var _exportFormats={export_formats_js};"
                f"var _exportFilename={export_filename_js};"
                f"var _exportScope={export_scope_js};"
                f"for(var _i=0;_i<_n;_i++)_order.push(_i);"
                f"var _rowsEls=[];"
                f"for(var _ri=0;_ri<_n;_ri++)_rowsEls.push(document.getElementById(uid+\"_r\"+_ri));"
                f"function _fname(ext){{return _exportFilename + '.' + ext;}}"
                f"function _download(name,blob){{"
                f"  var a=document.createElement('a');"
                f"  var url=URL.createObjectURL(blob);"
                f"  a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();"
                f"  setTimeout(function(){{URL.revokeObjectURL(url);}},1000);"
                f"}}"
                f"function _csvEsc(v){{"
                f"  var s=String(v==null?'':v);"
                f"  if(s.indexOf('\"')>=0)s=s.replace(/\"/g,'\"\"');"
                f"  if(/[\",\\n]/.test(s))s='\"'+s+'\"';"
                f"  return s;"
                f"}}"
                f"function _htmlEsc(v){{"
                f"  return String(v==null?'':v)"
                f"    .replace(/&/g,'&amp;').replace(/</g,'&lt;')"
                f"    .replace(/>/g,'&gt;').replace(/\"/g,'&quot;');"
                f"}}"
                f"function _exportRows(){{"
                f"  if(_exportScope==='page'){{"
                f"    var s=_page*_ps,e=Math.min(s+_ps,_order.length);"
                f"    return _order.slice(s,e);"
                f"  }}"
                f"  return _order.slice();"
                f"}}"
                f"function _doCsv(){{"
                f"  var idxs=_exportRows();"
                f"  var lines=[];"
                f"  if(_headers.length)lines.push(_headers.map(_csvEsc).join(','));"
                f"  for(var i=0;i<idxs.length;i++)lines.push(_data[idxs[i]].map(_csvEsc).join(','));"
                f"  _download(_fname('csv'),new Blob([lines.join('\\n')],{{type:'text/csv;charset=utf-8;'}}));"
                f"}}"
                f"function _doJson(){{"
                f"  var idxs=_exportRows();"
                f"  var out=[];"
                f"  for(var i=0;i<idxs.length;i++){{"
                f"    var row=_data[idxs[i]],obj={{}};"
                f"    for(var c=0;c<row.length;c++){{"
                f"      var k=_headers[c]||('col_'+(c+1));"
                f"      obj[k]=row[c];"
                f"    }}"
                f"    out.push(obj);"
                f"  }}"
                f"  _download(_fname('json'),new Blob([JSON.stringify(out,null,2)],{{type:'application/json;charset=utf-8;'}}));"
                f"}}"
                f"function _doExcel(){{"
                f"  var idxs=_exportRows();"
                f"  var html='<table><thead><tr>';"
                f"  for(var c=0;c<_headers.length;c++)html+='<th>'+_htmlEsc(_headers[c])+'</th>';"
                f"  html+='</tr></thead><tbody>';"
                f"  for(var i=0;i<idxs.length;i++){{"
                f"    var row=_data[idxs[i]];"
                f"    html+='<tr>';"
                f"    for(var c=0;c<row.length;c++)html+='<td>'+_htmlEsc(row[c])+'</td>';"
                f"    html+='</tr>';"
                f"  }}"
                f"  html+='</tbody></table>';"
                f"  var doc='\\ufeff<html><head><meta charset=\"utf-8\"></head><body>'+html+'</body></html>';"
                f"  _download(_fname('xls'),new Blob([doc],{{type:'application/vnd.ms-excel;charset=utf-8;'}}));"
                f"}}"
                f"function _doPdf(){{"
                f"  var idxs=_exportRows();"
                f"  if(window.jspdf&&window.jspdf.jsPDF){{"
                f"    var pdf=new window.jspdf.jsPDF({{orientation:'landscape'}});"
                f"    var y=12,lh=7,maxW=270,maxY=pdf.internal.pageSize.getHeight()-10;"
                f"    if(_headers.length){{pdf.text(_headers.join(' | '),10,y);y+=lh;}}"
                f"    for(var i=0;i<idxs.length;i++){{"
                f"      var txt=_data[idxs[i]].join(' | ');"
                f"      var lines=pdf.splitTextToSize(txt,maxW);"
                f"      for(var j=0;j<lines.length;j++){{"
                f"        if(y>maxY){{pdf.addPage();y=12;}}"
                f"        pdf.text(lines[j],10,y);y+=lh;"
                f"      }}"
                f"    }}"
                f"    pdf.save(_fname('pdf'));"
                f"    return;"
                f"  }}"
                f"  var w=window.open('','_blank');"
                f"  if(!w)return;"
                f"  var html='<table border=\"1\" cellspacing=\"0\" cellpadding=\"6\"><thead><tr>';"
                f"  for(var c=0;c<_headers.length;c++)html+='<th>'+_htmlEsc(_headers[c])+'</th>';"
                f"  html+='</tr></thead><tbody>';"
                f"  for(var i=0;i<idxs.length;i++){{"
                f"    var row=_data[idxs[i]];"
                f"    html+='<tr>';"
                f"    for(var c=0;c<row.length;c++)html+='<td>'+_htmlEsc(row[c])+'</td>';"
                f"    html+='</tr>';"
                f"  }}"
                f"  html+='</tbody></table>';"
                f"  w.document.write('<html><head><title>'+_fname('pdf')+'</title></head><body>'+html+'</body></html>');"
                f"  w.document.close();w.focus();w.print();"
                f"}}"
                # match: row must pass global AND all active column filters
                f"function _match(idx){{"
                f"  var row=_data[idx];"
                f"  if(_globalQ){{"
                f"    var gq=_globalQ.toLowerCase();"
                f"    var found=false;"
                f"    for(var c=0;c<row.length;c++){{if(row[c].toLowerCase().indexOf(gq)>=0){{found=true;break;}}}}"
                f"    if(!found)return false;"
                f"  }}"
                f"  for(var c=0;c<_colQ.length;c++){{"
                f"    if(!_colQ[c])continue;"
                f'    var v=(row[c]||"").toLowerCase();'
                f"    if(v.indexOf(_colQ[c].toLowerCase())<0)return false;"
                f"  }}"
                f"  return true;"
                f"}}"
                # apply: filter + sort
                f"function _apply(){{"
                f"  var filtered=[];"
                f"  for(var i=0;i<_n;i++)if(_match(i))filtered.push(i);"
                f"  if(_sortCol>=0){{"
                f"    var asc=_sortAsc,col=_sortCol;"
                f"    filtered.sort(function(a,b){{"
                f'      var va=(_data[a][col]||"").trim();'
                f'      var vb=(_data[b][col]||"").trim();'
                f"      var na=Number(va),nb=Number(vb);"
                f'      if(va!==""&&vb!==""&&!isNaN(na)&&!isNaN(nb))return asc?na-nb:nb-na;'
                f'      return asc?va.localeCompare(vb,"es",{{sensitivity:"base"}}):'
                f'               vb.localeCompare(va,"es",{{sensitivity:"base"}});'
                f"    }});"
                f"  }}"
                f"  _order=filtered;"
                f"  _page=0;"
                f"  _render();"
                f"}}"
                # render visible slice
                f"function _render(){{"
                f'  var tbody=document.getElementById(uid+"_tbody");'
                f"  if(!tbody)return;"
                f"  var start=_page*_ps,end=Math.min(start+_ps,_order.length);"
                f"  var vis=[];"
                f'  tbody.innerHTML="";'
                f"  for(var i=start;i<end;i++){{"
                f"    var r=_rowsEls[_order[i]];"
                f'    if(r){{r.style.display="";tbody.appendChild(r);vis.push(r);}}'
                f"  }}"
            )

            if self.striped:
                js += (
                    f"  vis.forEach(function(r,idx){{"
                    f'    r.querySelectorAll("td").forEach(function(td){{'
                    f'      td.style.background=idx%2===1?"var(--surface-2,rgba(0,0,0,0.03))":"";'
                    f"    }});"
                    f"  }});"
                )

            if self.page_size:
                js += (
                    f'  var info=document.getElementById(uid+"_pginfo");'
                    f"  var total=_order.length;"
                    f'  if(info)info.textContent=total===0?"Sin resultados":'
                    f'    "Mostrando "+(start+1)+"\u2013"+end+" de "+total;'
                    f'  var prev=document.getElementById(uid+"_pgprev");'
                    f'  var next=document.getElementById(uid+"_pgnext");'
                    f"  if(prev)prev.disabled=_page===0;"
                    f"  if(next)next.disabled=end>=_order.length;"
                )

            if self.sortable:
                js += (
                    f"  for(var c=0;c<{ncols};c++){{"
                    f'    var si=document.getElementById(uid+"_si"+c);'
                    f"    if(!si)continue;"
                    f'    if(c===_sortCol){{si.textContent=_sortAsc?"\u25b2":"\u25bc";si.style.color="var(--accent)";}}'
                    f'    else{{si.textContent="\u21c5";si.style.color="var(--text-muted)";}}'
                    f"  }}"
                )

            js += f"}}"  # end _render

            # public APIs
            if self.searchable:
                js += (
                    f'window[uid+"_globalFilter"]=function(q){{_globalQ=q;_apply();}};'
                    f'window[uid+"_colFilter"]=function(el,c){{_colQ[c]=el.value;_apply();}};'
                )

            if self.page_size:
                js += (
                    f'window[uid+"_pg"]=function(d){{'
                    f"  var pages=Math.max(1,Math.ceil(_order.length/_ps));"
                    f"  _page=Math.max(0,Math.min(_page+d,pages-1));"
                    f"  _render();"
                    f"}};"
                )

            if self.sortable:
                js += (
                    f'var _thead=document.querySelector("#{uid}_tbody").closest("table").querySelector("thead");'
                    f'if(_thead)_thead.addEventListener("click",function(e){{'
                    f'  var th=e.target.closest("th[data-col]");'
                    f'  if(!th||e.target.tagName==="INPUT")return;'
                    f'  var col=parseInt(th.getAttribute("data-col"));'
                    f"  if(_sortCol===col)_sortAsc=!_sortAsc;"
                    f"  else{{_sortCol=col;_sortAsc=true;}}"
                    f"  _apply();"
                    f"}});"
                )

            if self.export_formats:
                js += (
                    f'window[uid+"_export"]=function(fmt){{'
                    f"  if(_exportFormats.indexOf(fmt)<0)return;"
                    f"  if(fmt==='csv')return _doCsv();"
                    f"  if(fmt==='json')return _doJson();"
                    f"  if(fmt==='excel')return _doExcel();"
                    f"  if(fmt==='pdf')return _doPdf();"
                    f"}};"
                )

            js += f"_apply();}})()</script>"

        return (
            f'<div style="{wrapper_style}">'
            + global_search
            + export_buttons
            + f'<table style="{base}">{thead}{tbody}</table>'
            + pagination_html
            + f"</div>"
            + js
        )
