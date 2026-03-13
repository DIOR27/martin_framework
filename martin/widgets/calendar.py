"""
Martin — Calendar Widgets

Auto-extracted from former compound module.
"""

from ..widget import Widget

__all__ = ["CalendarEvent", "Calendar"]


class CalendarEvent:
    """
    Evento del calendario.

        CalendarEvent(
            title="Reunión de equipo",
            date="2025-03-15",
            start_time="10:00",
            end_time="11:30",
            color="#6366f1",
            description="Sala B, edificio central",
            all_day=False,
            url="/eventos/123",
        )
    """

    def __init__(
        self,
        title,
        date,
        start_time=None,
        end_time=None,
        color=None,
        description=None,
        all_day=False,
        url=None,
    ):
        self.title = title
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.color = color
        self.description = description
        self.all_day = all_day
        self.url = url

class Calendar(Widget):
    """
    Calendario interactivo completo con vistas mes, semana y día.
    Soporta gestión de eventos (crear, editar, eliminar) con modal integrado.

    Uso básico:
        Calendar(events=[
            CalendarEvent("Reunión", "2025-03-15", start_time="10:00", color="#6366f1"),
            CalendarEvent("Entrega", "2025-03-20", color="#ef4444"),
            CalendarEvent("Vacaciones", "2025-03-22", all_day=True, color="#34d399"),
        ])

        # Con edición habilitada:
        Calendar(events=[...], editable=True)

    Parámetros:
        events             list[CalendarEvent]
        initial_view       "month" | "week" | "day"  (default: "month")
        initial_date       "YYYY-MM-DD"  (default: hoy)
        range_select       bool  — selección de rango en vista mes (default: False)
        editable           bool  — habilita crear/editar/eliminar (default: False)
        on_date_click      str   — JS fn(dateStr) al hacer clic en fecha
        on_event_click     str   — JS fn(event) al hacer clic en evento
        on_event_create    str   — JS fn(event) al crear evento
        on_event_update    str   — JS fn(newEvent, oldEvent) al editar
        on_event_delete    str   — JS fn(event) al eliminar
        show_views         bool  (default: True)
        show_today         bool  (default: True)
        first_day          int   0=domingo, 1=lunes (default: 1)
        locale             "es" | "en"  (default: "es")
        height             int px (default: 600)
        accent             str color de acento (default: "var(--accent)")
        event_colors       list[str] paleta para el picker de color
    """

    _id_counter = 0

    MONTHS_ES = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]
    DAYS_ES = ["Dom", "Lun", "Mar", "Mi\u00e9", "Jue", "Vie", "S\u00e1b"]
    MONTHS_EN = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    DAYS_EN = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    DEFAULT_COLORS = [
        "#6366f1",
        "#3b82f6",
        "#06b6d4",
        "#10b981",
        "#84cc16",
        "#f59e0b",
        "#ef4444",
        "#ec4899",
        "#8b5cf6",
        "#64748b",
    ]

    def __init__(
        self,
        events=None,
        initial_view="month",
        initial_date=None,
        range_select=False,
        editable=False,
        on_date_click=None,
        on_event_click=None,
        on_event_create=None,
        on_event_update=None,
        on_event_delete=None,
        show_views=True,
        show_today=True,
        first_day=1,
        locale="es",
        height=600,
        accent="var(--accent)",
        event_colors=None,
        **kwargs,
    ):
        self._props = Widget._extract_props(kwargs)
        self.events = events or []
        self.initial_view = initial_view
        self.initial_date = initial_date
        self.range_select = range_select
        self.editable = editable
        self.on_date_click = on_date_click
        self.on_event_click = on_event_click
        self.on_event_create = on_event_create
        self.on_event_update = on_event_update
        self.on_event_delete = on_event_delete
        self.show_views = show_views
        self.show_today = show_today
        self.first_day = first_day
        self.locale = locale
        self.height = height
        self.accent = accent
        self.event_colors = event_colors or self.DEFAULT_COLORS
        Calendar._id_counter += 1
        self.uid = f"cal_{Calendar._id_counter}"

    def _serialize_events(self):
        import json as _j

        return _j.dumps(
            [
                {
                    "title": ev.title,
                    "date": ev.date,
                    "start_time": ev.start_time or "",
                    "end_time": ev.end_time or "",
                    "color": ev.color or "",
                    "description": ev.description or "",
                    "all_day": ev.all_day,
                    "url": ev.url or "",
                }
                for ev in self.events
            ]
        )

    def render(self):
        import json as _j

        uid = self.uid
        extra = self._resolve_props()
        height = self.height

        months = _j.dumps(self.MONTHS_ES if self.locale == "es" else self.MONTHS_EN)
        days = _j.dumps(self.DAYS_ES if self.locale == "es" else self.DAYS_EN)
        events_js = self._serialize_events()
        first_day = self.first_day
        init_view = _j.dumps(self.initial_view)
        init_date = _j.dumps(self.initial_date or "")
        range_sel = _j.dumps(self.range_select)
        editable = _j.dumps(self.editable)
        accent = _j.dumps(self.accent)
        colors_js = _j.dumps(self.event_colors)
        cb_date = _j.dumps(self.on_date_click or "")
        cb_click = _j.dumps(self.on_event_click or "")
        cb_create = _j.dumps(self.on_event_create or "")
        cb_update = _j.dumps(self.on_event_update or "")
        cb_delete = _j.dumps(self.on_event_delete or "")

        if self.locale == "es":
            lbl = dict(
                new_event="Nuevo evento",
                edit_event="Editar evento",
                title_lbl="T\u00edtulo",
                title_ph="T\u00edtulo del evento",
                date_lbl="Fecha",
                start_lbl="Inicio",
                end_lbl="Fin",
                desc_lbl="Descripci\u00f3n",
                desc_ph="Descripci\u00f3n (opcional)",
                color_lbl="Color",
                allday_lbl="Todo el d\u00eda",
                save="Guardar",
                cancel="Cancelar",
                delete="Eliminar",
                confirm_del="\u00bfEliminar este evento?",
                no_events="No hay eventos.",
                add_tip="Clic en una hora para crear un evento",
                today_lbl="Hoy",
                mas="m\u00e1s",
            )
        else:
            lbl = dict(
                new_event="New event",
                edit_event="Edit event",
                title_lbl="Title",
                title_ph="Event title",
                date_lbl="Date",
                start_lbl="Start",
                end_lbl="End",
                desc_lbl="Description",
                desc_ph="Description (optional)",
                color_lbl="Color",
                allday_lbl="All day",
                save="Save",
                cancel="Cancel",
                delete="Delete",
                confirm_del="Delete this event?",
                no_events="No events.",
                add_tip="Click a time slot to create an event",
                today_lbl="Today",
                mas="more",
            )
        lbl_js = _j.dumps(lbl)

        wrapper_style = (
            f"background:var(--surface);border:1px solid var(--border);"
            f"border-radius:16px;overflow:hidden;display:flex;"
            f"flex-direction:column;height:{height}px;{extra}"
        )

        # ─────────────────────────────────────────────────────────────────
        # JS ARCHITECTURE
        # All dynamic data (date, event id, hour) is passed via data-* attrs.
        # onclick handlers only call:  UID_handler(this)
        # Handlers read: el.dataset.date / el.dataset.eid / el.dataset.hour
        # This completely avoids quote-escaping issues in generated HTML strings.
        #
        # Python f-string rules:
        #   {{ }}  →  { }  in output (JS braces)
        #   {var}  →  interpolated Python variable
        # ─────────────────────────────────────────────────────────────────
        js = f"""
<script>
(function(){{
  var U={_j.dumps(uid)};
  var MONTHS={months};
  var DAYS={days};
  var ACCENT={accent};
  var FD={first_day};
  var RANGE={range_sel};
  var EDIT={editable};
  var COLORS={colors_js};
  var LBL={lbl_js};
  var CB_DATE={cb_date};
  var CB_CLICK={cb_click};
  var CB_CREATE={cb_create};
  var CB_UPDATE={cb_update};
  var CB_DELETE={cb_delete};

  /* ── accent resolver ──────────────────────────────── */
  function A(){{
    if(!ACCENT||ACCENT.indexOf("var(")<0)return ACCENT||"#6366f1";
    var p=ACCENT.replace(/^var\(/,"").replace(/\)$/,"").split(",")[0].trim();
    return(getComputedStyle(document.documentElement).getPropertyValue(p)||"").trim()||"#6366f1";
  }}

  /* ── event store ──────────────────────────────────── */
  var EVTS={events_js}.map(function(e,i){{return Object.assign({{_id:i}},e);}});
  var NID=EVTS.length;
  var EBD={{}};
  function idx(){{
    EBD={{}};
    EVTS.forEach(function(e){{if(!EBD[e.date])EBD[e.date]=[];EBD[e.date].push(e);}});
  }}
  idx();

  /* ── state ────────────────────────────────────────── */
  var NOW=new Date();
  var _id={init_date}?new Date({init_date}):new Date();
  var CY=_id.getFullYear(),CM=_id.getMonth(),CD=_id.getDate();
  var VIEW={init_view};
  var RS=null,RE=null;

  /* ── helpers ──────────────────────────────────────── */
  function pad(n){{return n<10?"0"+n:""+n;}}
  function ds(y,m,d){{return y+"-"+pad(m+1)+"-"+pad(d);}}
  function isToday(y,m,d){{return y===NOW.getFullYear()&&m===NOW.getMonth()&&d===NOW.getDate();}}
  function esc(s){{
    return(s||"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
                 .replace(/'/g,"&#39;");
  }}
  function G(id){{return document.getElementById(U+"_"+id);}}
  function getEv(id){{for(var i=0;i<EVTS.length;i++)if(EVTS[i]._id===id)return EVTS[i];return null;}}
  function callCb(name,args){{
    if(!name)return;
    try{{
      var f=window[name]||eval("("+name+")");
      if(typeof f=="function")f.apply(null,args);
    }}catch(e){{console.warn("Calendar cb error:",e);}}
  }}

  /* ── layout ───────────────────────────────────────── */
  function layout(){{
    var g=G("grid"),dn=G("daynames");
    if(!g)return;
    if(VIEW==="month"){{
      if(dn)dn.style.display="grid";
      g.style.display="grid";
      g.style.gridTemplateColumns="repeat(7,1fr)";
      g.style.overflowY="auto";
    }}else{{
      if(dn)dn.style.display="none";
      g.style.display="block";
      g.style.gridTemplateColumns="unset";
      g.style.overflowY="hidden";
    }}
  }}

  function renderHeader(){{
    var t="";
    if(VIEW==="month")t=MONTHS[CM]+" "+CY;
    else if(VIEW==="week"){{
      var w=weekDays(CY,CM,CD);
      t=MONTHS[w[0].getMonth()]+" "+w[0].getDate()+
        " \u2013 "+MONTHS[w[6].getMonth()]+" "+w[6].getDate()+", "+w[0].getFullYear();
    }}else t=MONTHS[CM]+" "+CD+", "+CY;
    var h=G("title");if(h)h.textContent=t;
  }}

  function syncBtns(){{
    ["month","week","day"].forEach(function(v){{
      var b=document.getElementById(U+"_vbtn_"+v);if(!b)return;
      var a=A();
      b.style.background=v===VIEW?a:"var(--surface-2,var(--surface))";
      b.style.color=v===VIEW?"#fff":"var(--text)";
      b.style.borderColor=v===VIEW?a:"var(--border)";
    }});
  }}

  /* ══════════════════════════════════════════════════
     MONTH VIEW
     onclick passes data via data-* attributes — no quote issues
  ══════════════════════════════════════════════════ */
  function fdo(y,m){{return((new Date(y,m,1).getDay()-FD)+7)%7;}}

  function renderMonth(){{
    var g=G("grid");if(!g)return;
    var a=A(),off=fdo(CY,CM);
    var dim=new Date(CY,CM+1,0).getDate(),dip=new Date(CY,CM,0).getDate();
    var total=Math.ceil((off+dim)/7)*7,h="";

    for(var i=0;i<total;i++){{
      var cy=CY,cm=CM,cd,out=false;
      if(i<off){{cd=dip-(off-1-i);cm=CM-1;if(cm<0){{cm=11;cy--;}}out=true;}}
      else if(i>=off+dim){{cd=i-off-dim+1;cm=CM+1;if(cm>11){{cm=0;cy++;}}out=true;}}
      else cd=i-off+1;

      var date=ds(cy,cm,cd),evs=EBD[date]||[];
      var isTod=isToday(cy,cm,cd),isRS=date===RS,isRE=date===RE;
      var inR=RS&&RE&&date>=RS&&date<=RE;
      var bg="transparent";
      if(isTod)bg="rgba(99,102,241,.12)";
      if(inR)bg="rgba(99,102,241,.07)";
      if(isRS||isRE)bg=a;
      var dc=(isRS||isRE)?"#fff":(out?"var(--text-muted)":"var(--text)");
      var fw=isTod?"700":"400",br=(isRS||isRE)?"border-radius:8px":"";

      /* event pills */
      var ep="",mx=Math.min(evs.length,3);
      for(var ei=0;ei<mx;ei++){{
        var ec=evs[ei].color||a;
        /* data-eid passed via data attribute — no quote escaping needed */
        ep+="<div onclick='"+U+"_evClick(this)' data-eid='"+evs[ei]._id+"'"
           +" style='font-size:10px;background:"+ec+";color:#fff;border-radius:3px;"
           +"padding:1px 5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
           +"margin-top:2px;cursor:pointer'>"+esc(evs[ei].title)+"</div>";
      }}
      if(evs.length>3)ep+="<div style='font-size:10px;color:var(--text-muted);margin-top:2px'>+"+(evs.length-3)+" "+LBL.mas+"</div>";

      /* add button (editable) — date via data attribute */
      var ab=EDIT
        ?"<div onclick='event.stopPropagation();"+U+"_openCreate(this)'"
         +" data-date='"+date+"' data-hour=''"
         +" class='"+U+"_ab'"
         +" style='font-size:16px;color:var(--text-muted);opacity:0;transition:opacity .15s;"
         +"cursor:pointer;text-align:center;margin-top:2px'>+</div>"
        :"";

      /* cell — date via data attribute */
      h+="<div onclick='"+U+"_dayClick(this)' data-date='"+date+"'"
        +" onmouseenter='"+U+"_cellHover(1)'"
        +" onmouseleave='"+U+"_cellHover(0)'"
        +" style='border:1px solid var(--border);padding:6px 8px;min-height:80px;"
        +"cursor:pointer;background:"+bg+";"+br+";transition:background .15s;box-sizing:border-box'>"
        +"<div style='font-size:13px;font-weight:"+fw+";color:"+dc+"'>"+cd+"</div>"
        +(isTod?"<div style='width:4px;height:4px;border-radius:50%;background:"+a+";margin:1px auto'></div>":"")
        +ep+ab+"</div>";
    }}
    g.innerHTML=h;
  }}

  /* ══════════════════════════════════════════════════
     WEEK VIEW
  ══════════════════════════════════════════════════ */
  function weekDays(y,m,d){{
    var dt=new Date(y,m,d),diff=((dt.getDay()-FD)+7)%7;
    var s=new Date(dt);s.setDate(dt.getDate()-diff);
    var r=[];
    for(var i=0;i<7;i++){{var x=new Date(s);x.setDate(s.getDate()+i);r.push(x);}}
    return r;
  }}
  var HRS=[];for(var _h=0;_h<24;_h++)HRS.push(pad(_h)+":00");

  function renderWeek(){{
    var g=G("grid");if(!g)return;
    var wd=weekDays(CY,CM,CD),a=A();
    var h="<div style='display:grid;grid-template-columns:56px repeat(7,minmax(120px,1fr));"
          +"height:100%;overflow:auto;min-width:860px'>";

    /* header row */
    h+="<div style='background:var(--surface-2,var(--surface));border-bottom:1px solid var(--border)'></div>";
    for(var wi=0;wi<wd.length;wi++){{
      var dt2=wd[wi],tod=isToday(dt2.getFullYear(),dt2.getMonth(),dt2.getDate()),dn=dt2.getDate();
      var dnH=tod
        ?"<span style='background:"+a+";color:#fff;border-radius:50%;width:28px;height:28px;"
          +"display:inline-flex;align-items:center;justify-content:center'>"+dn+"</span>"
        :dn;
      h+="<div style='border-bottom:1px solid var(--border);border-left:1px solid var(--border);"
        +"padding:8px 4px;text-align:center;background:var(--surface-2,var(--surface));"
        +(tod?"color:"+a+";font-weight:700":"color:var(--text-muted)")+";font-size:12px'>"
        +DAYS[dt2.getDay()]+"<br>"
        +"<span style='font-size:18px;font-weight:700'>"+dnH+"</span></div>";
    }}

    /* hour rows */
    for(var hi=0;hi<HRS.length;hi++){{
      var hStr=HRS[hi],hour=parseInt(hStr,10);
      h+="<div style='border-bottom:1px solid var(--border);padding:4px 6px;"
        +"font-size:11px;color:var(--text-muted);text-align:right;white-space:nowrap'>"+hStr+"</div>";
      for(var wi2=0;wi2<wd.length;wi2++){{
        var dt3=wd[wi2],d3=ds(dt3.getFullYear(),dt3.getMonth(),dt3.getDate());
        var dl=EBD[d3]||[],slEv="";
        for(var di=0;di<dl.length;di++){{
          var ev=dl[di];
          if(!ev.start_time||parseInt(ev.start_time.split(":")[0],10)!==hour)continue;
          var ec=ev.color||a;
          slEv+="<div onclick='event.stopPropagation();"+U+"_evClick(this)' data-eid='"+ev._id+"'"
               +" style='background:"+ec+";color:#fff;font-size:11px;border-radius:4px;"
               +"padding:2px 6px;margin-bottom:2px;cursor:pointer;overflow:hidden;"
               +"white-space:nowrap;text-overflow:ellipsis'>"
               +esc(ev.title)+(ev.end_time?" "+ev.start_time+"-"+ev.end_time:"")+"</div>";
        }}
        /* slot cell — date and hour via data attributes */
        h+="<div onclick='"+U+"_dayClick(this)' data-date='"+d3+"' data-hour='"+hStr+"'"
          +" style='border-bottom:1px solid var(--border);border-left:1px solid var(--border);"
          +"padding:2px;min-height:40px;box-sizing:border-box;cursor:pointer'>"+slEv+"</div>";
      }}
    }}
    h+="</div>";
    g.innerHTML=h;
  }}

  /* ══════════════════════════════════════════════════
     DAY VIEW
  ══════════════════════════════════════════════════ */
  function renderDay(){{
    var g=G("grid");if(!g)return;
    var date=ds(CY,CM,CD),dl=EBD[date]||[],a=A(),tod=isToday(CY,CM,CD);
    var h="<div style='overflow-y:auto;height:100%'>";

    h+="<div style='padding:12px 16px;border-bottom:1px solid var(--border);"
      +"background:var(--surface-2,var(--surface));font-size:15px;font-weight:700;color:var(--text)'>"
      +MONTHS[CM]+" "+CD+", "+CY
      +(tod?"<span style='background:"+a+";color:#fff;font-size:11px;"
        +"padding:2px 8px;border-radius:999px;margin-left:8px'>"+LBL.today_lbl+"</span>":"")
      +"</div>";

    if(!dl.length)
      h+="<div style='padding:10px 16px;font-size:12px;color:var(--text-muted)'>"
        +(EDIT?LBL.add_tip:LBL.no_events)+"</div>";

    /* all-day events */
    var ada=[];for(var i=0;i<dl.length;i++)if(dl[i].all_day)ada.push(dl[i]);
    if(ada.length){{
      h+="<div style='padding:8px 16px;border-bottom:1px solid var(--border)'>";
      for(var i=0;i<ada.length;i++){{
        var ec=ada[i].color||a;
        h+="<div onclick='"+U+"_evClick(this)' data-eid='"+ada[i]._id+"'"
          +" style='background:"+ec+";color:#fff;border-radius:6px;padding:6px 12px;"
          +"margin-bottom:4px;font-size:13px;cursor:pointer'>"+esc(ada[i].title)+"</div>";
      }}
      h+="</div>";
    }}

    /* hour slots */
    for(var hi=0;hi<HRS.length;hi++){{
      var hStr=HRS[hi],hour=parseInt(hStr,10),slEv="";
      for(var di=0;di<dl.length;di++){{
        var ev=dl[di];
        if(!ev.start_time||parseInt(ev.start_time.split(":")[0],10)!==hour)continue;
        var ec=ev.color||a;
        slEv+="<div onclick='event.stopPropagation();"+U+"_evClick(this)' data-eid='"+ev._id+"'"
             +" style='background:"+ec+";color:#fff;border-radius:6px;"
             +"padding:8px 12px;margin-bottom:4px;cursor:pointer'>"
             +"<div style='font-weight:600;font-size:13px'>"+esc(ev.title)+"</div>"
             +(ev.start_time?"<div style='font-size:11px;opacity:.85'>"+ev.start_time
               +(ev.end_time?" \u2013 "+ev.end_time:"")+"</div>":"")
             +(ev.description?"<div style='font-size:12px;margin-top:4px;opacity:.85'>"
               +esc(ev.description)+"</div>":"")
             +"</div>";
      }}
      h+="<div style='display:grid;grid-template-columns:64px 1fr;"
        +"border-bottom:1px solid var(--border);min-height:56px'>"
        +"<div style='padding:8px 10px;font-size:12px;color:var(--text-muted);text-align:right'>"+hStr+"</div>"
        +"<div onclick='"+U+"_dayClick(this)' data-date='"+date+"' data-hour='"+hStr+"'"
        +" style='padding:4px 8px;cursor:pointer'>"+slEv+"</div>"
        +"</div>";
    }}
    h+="</div>";
    g.innerHTML=h;
  }}

  /* ══════════════════════════════════════════════════
     MODAL — appended to document.body to escape overflow:hidden
  ══════════════════════════════════════════════════ */
  function rmOv(){{
    var o=document.getElementById(U+"_ov");
    if(o&&o.parentNode)o.parentNode.removeChild(o);
  }}

  function mkOv(inner){{
    rmOv();
    var o=document.createElement("div");
    o.id=U+"_ov";
    o.style.cssText="position:fixed;inset:0;z-index:9999;background:rgba(2,6,23,.68);"
      +"backdrop-filter:blur(4px);-webkit-backdrop-filter:blur(4px);"
      +"display:flex;align-items:center;justify-content:center;"
      +"padding:16px;box-sizing:border-box";
    o.onclick=function(e){{if(e.target===o)rmOv();}};
    var box=document.createElement("div");
    box.style.cssText="background:var(--dropdown-bg,var(--surface));color:var(--text);"
      +"border:1px solid var(--border);border-radius:16px;padding:24px;"
      +"width:100%;max-width:460px;box-shadow:0 24px 64px rgba(0,0,0,.4);"
      +"max-height:90vh;overflow-y:auto;box-sizing:border-box";
    box.innerHTML=inner;
    o.appendChild(box);
    document.body.appendChild(o);
    setTimeout(function(){{
      var inp=o.querySelector("input[type=text],input[type=date]");
      if(inp)inp.focus();
    }},40);
  }}

  /* ── Info modal ─────────────────────────────────── */
  function showInfo(ev){{
    var a=A(),ec=ev.color||a;
    /* close button uses data-uid to avoid quote issues */
    var h="<div style='display:flex;align-items:center;gap:10px;margin-bottom:16px'>"
      +"<div style='width:12px;height:12px;border-radius:50%;background:"+ec+";flex-shrink:0'></div>"
      +"<span style='font-size:17px;font-weight:700;color:var(--text)'>"+esc(ev.title)+"</span>"
      +"<button onclick='"+U+"_closeOv()' style='margin-left:auto;background:none;border:none;"
      +"font-size:22px;cursor:pointer;color:var(--text-muted);line-height:1'>\u00d7</button>"
      +"</div>"
      +(ev.date?"<div style='font-size:13px;color:var(--text-muted);margin-bottom:6px'>&#128197; "+esc(ev.date)+"</div>":"")
      +(ev.start_time?"<div style='font-size:13px;color:var(--text-muted);margin-bottom:6px'>&#128336; "
        +ev.start_time+(ev.end_time?" \u2013 "+ev.end_time:"")+"</div>":"")
      +(ev.description?"<div style='font-size:13px;color:var(--text);margin-top:8px;line-height:1.6'>"
        +esc(ev.description)+"</div>":"");
    mkOv(h);
  }}

  /* ── Form modal ─────────────────────────────────── */
  function showForm(ev,date,hourStr){{
    var isNew=!ev,a=A(),defColor=isNew?(COLORS[0]||a):(ev.color||a);
    var eid=isNew?null:ev._id;

    /* color swatches */
    var sw="";
    for(var ci=0;ci<COLORS.length;ci++){{
      var c=COLORS[ci],sel=c===defColor?"3px solid var(--text)":"2px solid transparent";
      /* data-color attribute — no quote issues */
      sw+="<div onclick='"+U+"_pickColor(this)' data-color='"+c+"'"
        +" style='display:inline-block;width:22px;height:22px;border-radius:50%;"
        +"background:"+c+";cursor:pointer;outline:"+sel+";transition:outline .1s'></div>";
    }}

    var IS="width:100%;box-sizing:border-box;padding:9px 12px;border:1px solid var(--border);"
          +"border-radius:8px;font-size:14px;background:var(--surface);color:var(--text);outline:none";
    var LS="font-size:12px;font-weight:600;color:var(--text-muted);display:block;margin-bottom:4px";
    var tdDisplay=(ev&&ev.all_day)?"none":"grid";
    var eidJson=isNew?"null":String(eid);

    var h=
      "<div style='display:flex;align-items:center;margin-bottom:20px'>"
      +"<span style='font-size:17px;font-weight:700;color:var(--text)'>"+(isNew?LBL.new_event:LBL.edit_event)+"</span>"
      +"<button onclick='"+U+"_closeOv()' style='margin-left:auto;background:none;border:none;"
      +"font-size:22px;cursor:pointer;color:var(--text-muted);line-height:1'>\u00d7</button>"
      +"</div>"

      +"<div style='margin-bottom:14px'>"
      +"<label style='"+LS+"'>"+LBL.title_lbl+"</label>"
      +"<input id='"+U+"_ft' type='text' placeholder='"+LBL.title_ph+"' value='"+esc(ev?ev.title:"")+"'"
      +" style='"+IS+"'/></div>"

      +"<div style='margin-bottom:14px'>"
      +"<label style='"+LS+"'>"+LBL.date_lbl+"</label>"
      +"<input id='"+U+"_fd' type='date' value='"+(date||"")+"' style='"+IS+"'/></div>"

      +"<div style='margin-bottom:14px;display:flex;align-items:center;gap:8px'>"
      +"<input type='checkbox' id='"+U+"_fad'"+(ev&&ev.all_day?" checked":"")
      +" onchange='"+U+"_toggleAllDay(this)'"
      +" style='width:16px;height:16px;cursor:pointer'/>"
      +"<label for='"+U+"_fad' style='font-size:13px;color:var(--text);cursor:pointer'>"+LBL.allday_lbl+"</label>"
      +"</div>"

      +"<div id='"+U+"_ftimes' style='display:"+tdDisplay+";grid-template-columns:1fr 1fr;gap:12px;margin-bottom:14px'>"
      +"<div><label style='"+LS+"'>"+LBL.start_lbl+"</label>"
      +"<input id='"+U+"_fs' type='time' value='"+(ev?esc(ev.start_time):(hourStr||""))+"' style='"+IS+"'/></div>"
      +"<div><label style='"+LS+"'>"+LBL.end_lbl+"</label>"
      +"<input id='"+U+"_fe' type='time' value='"+(ev?esc(ev.end_time):"")+"' style='"+IS+"'/></div>"
      +"</div>"

      +"<div style='margin-bottom:14px'>"
      +"<label style='"+LS+"'>"+LBL.desc_lbl+"</label>"
      +"<textarea id='"+U+"_fde' rows='2' placeholder='"+LBL.desc_ph+"'"
      +" style='"+IS+";resize:vertical'>"+esc(ev?ev.description:"")+"</textarea></div>"

      +"<div style='margin-bottom:20px'>"
      +"<label style='"+LS+"'>"+LBL.color_lbl+"</label>"
      +"<input type='hidden' id='"+U+"_fc' value='"+defColor+"'/>"
      +"<div id='"+U+"_swatches' style='display:flex;flex-wrap:wrap;gap:8px'>"+sw+"</div></div>"

      +"<div style='display:flex;gap:8px;justify-content:flex-end;align-items:center'>"
      +(!isNew
        ?"<button onclick='"+U+"_evDel(this)' data-eid='"+eid+"'"
         +" style='padding:9px 18px;border-radius:8px;border:1px solid #ef4444;"
         +"background:transparent;color:#ef4444;font-size:13px;font-weight:600;"
         +"cursor:pointer;margin-right:auto'>"+LBL.delete+"</button>"
        :"")
      +"<button onclick='"+U+"_closeOv()'"
      +" style='padding:9px 18px;border-radius:8px;border:1px solid var(--border);"
      +"background:transparent;color:var(--text);font-size:13px;font-weight:600;cursor:pointer'>"+LBL.cancel+"</button>"
      +"<button onclick='"+U+"_evSave(this)' data-eid='"+eidJson+"'"
      +" style='padding:9px 18px;border-radius:8px;border:none;"
      +"background:"+a+";color:#fff;font-size:13px;font-weight:600;cursor:pointer'>"+LBL.save+"</button>"
      +"</div>";

    mkOv(h);
  }}

  /* ══════════════════════════════════════════════════
     PUBLIC API — all registered on window
  ══════════════════════════════════════════════════ */

  /* close overlay */
  window[U+"_closeOv"]=function(){{rmOv();}};

  /* hover on month cells — show/hide + buttons */
  window[U+"_cellHover"]=function(show){{
    var g=G("grid");if(!g)return;
    var ab=g.getElementsByClassName(U+"_ab");
    for(var i=0;i<ab.length;i++)ab[i].style.opacity=show?"1":"0";
  }};

  /* color swatch picker */
  window[U+"_pickColor"]=function(el){{
    var fc=document.getElementById(U+"_fc");
    if(fc)fc.value=el.dataset.color;
    var sw=document.getElementById(U+"_swatches");
    if(sw){{
      var items=sw.children;
      for(var i=0;i<items.length;i++)items[i].style.outline="2px solid transparent";
    }}
    el.style.outline="3px solid var(--text)";
  }};

  /* toggle all-day checkbox */
  window[U+"_toggleAllDay"]=function(el){{
    var td=document.getElementById(U+"_ftimes");
    if(td)td.style.display=el.checked?"none":"grid";
  }};

  /* event click — el has data-eid */
  window[U+"_evClick"]=function(el){{
    var eid=parseInt(el.dataset.eid,10),ev=getEv(eid);
    if(!ev)return;
    if(EDIT){{showForm(ev,ev.date,ev.start_time||"");return;}}
    if(CB_CLICK){{callCb(CB_CLICK,[ev]);return;}}
    if(ev.url){{window.location.href=ev.url;return;}}
    showInfo(ev);
  }};

  /* open create form — el has data-date, data-hour */
  window[U+"_openCreate"]=function(el){{
    if(!EDIT)return;
    showForm(null,el.dataset.date||ds(CY,CM,CD),el.dataset.hour||"");
  }};

  /* day/slot click — el has data-date, optional data-hour */
  window[U+"_dayClick"]=function(el){{
    var date=el.dataset.date,hourStr=el.dataset.hour||"";
    var p=date.split("-");
    CY=parseInt(p[0],10);CM=parseInt(p[1],10)-1;CD=parseInt(p[2],10);

    if(RANGE&&VIEW==="month"){{
      if(!RS||RE){{RS=date;RE=null;}}
      else{{RE=date<RS?RS:date;if(date<RS)RS=date;}}
    }}else if(VIEW!=="day"){{
      VIEW="day";syncBtns();
    }}

    if(EDIT&&VIEW==="day"&&hourStr){{
      /* pass a fake element with dataset */
      window[U+"_openCreate"]({{dataset:{{date:date,hour:hourStr}}}});
      return;
    }}
    if(CB_DATE)callCb(CB_DATE,[hourStr?(date+"T"+hourStr):date]);
    refresh();
  }};

  /* save form — el has data-eid */
  window[U+"_evSave"]=function(el){{
    var eidRaw=el.dataset.eid;
    var tel=document.getElementById(U+"_ft");
    var title=(tel?tel.value:"").trim();
    if(!title){{if(tel){{tel.style.borderColor="#ef4444";tel.focus();}}return;}}
    var date=(document.getElementById(U+"_fd")||{{}}).value||"";
    var allDay=!!(document.getElementById(U+"_fad")||{{}}).checked;
    var start=allDay?"":(document.getElementById(U+"_fs")||{{}}).value||"";
    var end=allDay?"":(document.getElementById(U+"_fe")||{{}}).value||"";
    var desc=(document.getElementById(U+"_fde")||{{}}).value||"";
    var color=(document.getElementById(U+"_fc")||{{}}).value||"";

    if(eidRaw==="null"||eidRaw===null||eidRaw===undefined){{
      var nev={{_id:NID++,title:title,date:date,start_time:start,end_time:end,
               description:desc,color:color,all_day:allDay,url:""}};
      EVTS.push(nev);idx();rmOv();refresh();
      callCb(CB_CREATE,[nev]);
    }}else{{
      var eid=parseInt(eidRaw,10);
      for(var i=0;i<EVTS.length;i++){{
        if(EVTS[i]._id===eid){{
          var old=Object.assign({{}},EVTS[i]);
          Object.assign(EVTS[i],{{title:title,date:date,start_time:start,end_time:end,
            description:desc,color:color,all_day:allDay}});
          idx();rmOv();refresh();
          callCb(CB_UPDATE,[EVTS[i],old]);
          break;
        }}
      }}
    }}
  }};

  /* delete event — el has data-eid */
  window[U+"_evDel"]=function(el){{
    var eid=parseInt(el.dataset.eid,10),ev=getEv(eid);
    if(!ev)return;
    if(!confirm(LBL.confirm_del+" ("+ev.title+")"))return;
    EVTS=EVTS.filter(function(e){{return e._id!==eid;}});
    idx();rmOv();refresh();
    callCb(CB_DELETE,[ev]);
  }};

  /* navigation */
  window[U+"_prev"]=function(){{
    if(VIEW==="month"){{CM--;if(CM<0){{CM=11;CY--;}}}}
    else if(VIEW==="week"){{var d=new Date(CY,CM,CD-7);CY=d.getFullYear();CM=d.getMonth();CD=d.getDate();}}
    else{{var d=new Date(CY,CM,CD-1);CY=d.getFullYear();CM=d.getMonth();CD=d.getDate();}}
    refresh();
  }};
  window[U+"_next"]=function(){{
    if(VIEW==="month"){{CM++;if(CM>11){{CM=0;CY++;}}}}
    else if(VIEW==="week"){{var d=new Date(CY,CM,CD+7);CY=d.getFullYear();CM=d.getMonth();CD=d.getDate();}}
    else{{var d=new Date(CY,CM,CD+1);CY=d.getFullYear();CM=d.getMonth();CD=d.getDate();}}
    refresh();
  }};
  window[U+"_today"]=function(){{
    CY=NOW.getFullYear();CM=NOW.getMonth();CD=NOW.getDate();refresh();
  }};
  window[U+"_setView"]=function(v){{VIEW=v;syncBtns();refresh();}};

  document.addEventListener("keydown",function(e){{if(e.key==="Escape")rmOv();}});

  function refresh(){{
    layout();renderHeader();
    if(VIEW==="month")renderMonth();
    else if(VIEW==="week")renderWeek();
    else renderDay();
    syncBtns();
  }}
  refresh();
}})();
</script>
"""

        # ── toolbar ────────────────────────────────────────────
        view_btns = ""
        if self.show_views:
            vmap = (
                [("month", "Mes"), ("week", "Semana"), ("day", "D\u00eda")]
                if self.locale == "es"
                else [("month", "Month"), ("week", "Week"), ("day", "Day")]
            )
            for vk, vl in vmap:
                act = vk == self.initial_view
                view_btns += (
                    f'<button id="{uid}_vbtn_{vk}" onclick="{uid}_setView(\'{vk}\')" '
                    f'style="padding:6px 14px;font-size:13px;border:1px solid var(--border);'
                    f"border-radius:6px;cursor:pointer;font-weight:500;"
                    f'background:{"var(--accent,#6366f1)" if act else "var(--surface-2,var(--surface))"};'
                    f'color:{"#fff" if act else "var(--text)"}">{vl}</button>'
                )

        today_lbl = "Hoy" if self.locale == "es" else "Today"
        today_btn = (
            (
                f'<button onclick="{uid}_today()" '
                f'style="padding:6px 14px;font-size:13px;border:1px solid var(--border);'
                f"border-radius:6px;cursor:pointer;background:var(--surface-2,var(--surface));"
                f'color:var(--text);font-weight:500">{today_lbl}</button>'
            )
            if self.show_today
            else ""
        )

        new_lbl = "\uff0b Nuevo evento" if self.locale == "es" else "\uff0b New event"
        new_btn = (
            (
                f'<button onclick="{uid}_openCreate(this)" data-date="" data-hour="" '
                f'style="padding:6px 14px;font-size:13px;border:none;'
                f"border-radius:6px;cursor:pointer;background:var(--accent,#6366f1);"
                f'color:#fff;font-weight:500">{new_lbl}</button>'
            )
            if self.editable
            else ""
        )

        # ── day names header ────────────────────────────────────
        day_data = self.DAYS_ES if self.locale == "es" else self.DAYS_EN
        ordered = day_data[self.first_day :] + day_data[: self.first_day]
        day_names_html = "".join(
            f'<div style="padding:8px 0;text-align:center;font-size:12px;'
            f'font-weight:600;color:var(--text-muted)">{dn}</div>'
            for dn in ordered
        )

        return (
            f'<div id="{uid}" style="{wrapper_style}">'
            + f'<div style="display:flex;align-items:center;gap:8px;padding:12px 16px;'
            f'border-bottom:1px solid var(--border);flex-shrink:0;flex-wrap:wrap">'
            + f'<button onclick="{uid}_prev()" style="width:32px;height:32px;display:flex;'
            f"align-items:center;justify-content:center;border:1px solid var(--border);"
            f"border-radius:6px;cursor:pointer;background:var(--surface-2,var(--surface));"
            f'color:var(--text);font-size:18px;line-height:1">&#8249;</button>'
            + f'<button onclick="{uid}_next()" style="width:32px;height:32px;display:flex;'
            f"align-items:center;justify-content:center;border:1px solid var(--border);"
            f"border-radius:6px;cursor:pointer;background:var(--surface-2,var(--surface));"
            f'color:var(--text);font-size:18px;line-height:1">&#8250;</button>'
            + f'<span id="{uid}_title" style="font-size:16px;font-weight:700;color:var(--text);flex:1"></span>'
            + today_btn
            + (
                f'<div style="display:flex;gap:4px">{view_btns}</div>'
                if self.show_views
                else ""
            )
            + new_btn
            + "</div>"
            + f'<div id="{uid}_daynames" style="display:grid;grid-template-columns:repeat(7,1fr);'
            f'border-bottom:1px solid var(--border);flex-shrink:0">{day_names_html}</div>'
            + f'<div id="{uid}_grid" style="flex:1;overflow:auto;'
            f'display:grid;grid-template-columns:repeat(7,1fr)"></div>' + "</div>" + js
        )

