"""
Martin — Data Visualization Widgets

Auto-extracted from former compound module.
"""

import uuid as _uuid

from ..widget import Widget

__all__ = [
    "WordCloud",
    "Map",
    "Timeline",
    "TimelineItem",
    "ChartDataset",
    "Chart",
]


class WordCloud(Widget):
    """
    Nube de palabras interactiva, sin dependencias externas.

    WordCloud(words=["Python", "Martin", "Web"])
    WordCloud(words={"Python": 10, "JS": 4, "Rust": 7})
    WordCloud(words=[("Python", 10), ("JS", 4)], width=700, height=350)

    Opciones:
        width       int     ancho en px          (default: 600)
        height      int     alto en px           (default: 300)
        min_size    int     tamaño mínimo fuente (default: 14)
        max_size    int     tamaño máximo fuente (default: 64)
        colors      list    lista de colores CSS (default: paleta indigo/mint)
        font        str     fuente CSS           (default: "inherit")
        on_click    str     JS ejecutado al hacer click: usa `word` y `weight`.
    """

    def __init__(self, words=None, width=600, height=300,
                 min_size=12, max_size=72,
                 colors=None, font="inherit", on_click=None, **kwargs):
        self._props   = Widget._extract_props(kwargs)
        self.words    = words or []
        self.width    = width
        self.height   = height
        self.min_size = min_size
        self.max_size = max_size
        self.colors   = colors or [
            "#818cf8", "#34d399", "#fb923c",
            "#f472b6", "#38bdf8", "#a78bfa",
            "#4ade80", "#fbbf24",
        ]
        self.font     = font
        self.on_click = on_click
        self.uid = f"wc_{_uuid.uuid4().hex[:8]}"

    def _parse_words(self):
        w = self.words
        if isinstance(w, dict):
            return list(w.items())
        result = []
        for item in w:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                result.append((str(item[0]), float(item[1])))
            else:
                result.append((str(item), 1.0))
        return result

    def render(self):
        import json as _json

        uid      = self.uid
        pairs    = self._parse_words()
        extra    = self._resolve_props()
        w        = self.width
        h        = self.height

        words_js  = _json.dumps(pairs)
        colors_js = _json.dumps(self.colors)
        min_s     = self.min_size
        max_s     = self.max_size
        font_js   = _json.dumps(self.font)
        on_click  = self.on_click or ""

        wrapper_style = (
            "display:block;position:relative;width:100%;"
            f"max-width:{w}px"
        )
        if extra:
            wrapper_style += ";" + extra

        return (
            '<div style="' + wrapper_style + '">'
            '<canvas id="' + uid + '" width="' + str(w) + '" height="' + str(h) + '"'
            ' style="display:block;width:100%;height:auto;max-width:' + str(w) + 'px;'
            'aspect-ratio:' + str(w) + '/' + str(h) + ';border-radius:12px;cursor:default"></canvas>'
            # Tooltip div — positioned absolute over canvas
            '<div id="' + uid + '_tip"'
            ' style="display:none;position:absolute;pointer-events:none;'
            'padding:5px 10px;background:rgba(0,0,0,0.75);color:#fff;'
            'border-radius:6px;font-size:12px;white-space:nowrap;'
            'transform:translate(-50%,-100%);margin-top:-6px;z-index:99"></div>'
            '</div>'
            '<script>(function(){'
            'var canvas=document.getElementById(' + _json.dumps(uid) + ');'
            'var tip=document.getElementById(' + _json.dumps(uid + "_tip") + ');'
            'if(!canvas)return;'
            'var ctx=canvas.getContext("2d");'
            'var dpr=window.devicePixelRatio||1;'
            'var baseW=' + str(w) + ',baseH=' + str(h) + ';'
            'var W=baseW,H=baseH;'
            'canvas.width=W*dpr;canvas.height=H*dpr;'
            'canvas.style.width=W+"px";canvas.style.height="auto";canvas.style.aspectRatio=W+"/"+H;'
            'ctx.scale(dpr,dpr);'
            'var rawWords=' + words_js + ';'
            'var colors=' + colors_js + ';'
            'var minS=' + str(min_s) + ',maxS=' + str(max_s) + ';'
            'var baseMinS=minS,baseMaxS=maxS;'
            'var font=' + font_js + ';'
            'if(font==="inherit")font="Segoe UI, Trebuchet MS, Helvetica Neue, Arial, sans-serif";'
            'var hostW=Math.floor((canvas.parentElement&&canvas.parentElement.clientWidth)||0);'
            'if(!hostW&&canvas.getBoundingClientRect)hostW=Math.floor(canvas.getBoundingClientRect().width||0);'
            'if(!hostW&&canvas.parentElement&&canvas.parentElement.getBoundingClientRect)hostW=Math.floor(canvas.parentElement.getBoundingClientRect().width||0);'
            'if(!hostW&&window.innerWidth)hostW=Math.floor(Math.min(window.innerWidth-48,baseW));'
            'if(!hostW)hostW=Math.floor(baseW*0.8);'
            'var isMobile=!!(window.matchMedia&&window.matchMedia("(max-width:640px)").matches);'
            'W=Math.max(160,Math.min(baseW,hostW));'
            'var widthRatio=W/baseW;'
            'minS=Math.max(10,Math.round(minS*Math.max(widthRatio,0.9)));'
            'maxS=Math.max(minS+8,Math.round(maxS*Math.max(widthRatio,0.82)));'
            'if(isMobile){'
            '  H=Math.max(Math.round(baseH*1.5),Math.round(W*1.28),220);'
            '  minS=Math.max(12,Math.round(baseMinS*0.98));'
            '  maxS=Math.max(minS+12,Math.round(baseMaxS*0.78));'
            '}'
            'ctx.setTransform(1,0,0,1,0,0);'
            'canvas.width=W*dpr;canvas.height=H*dpr;'
            'canvas.style.width="100%";canvas.style.maxWidth=W+"px";canvas.style.height="auto";canvas.style.aspectRatio=W+"/"+H;'
            'ctx.scale(dpr,dpr);'
            'var hitPad=isMobile?8:4;'
            'var maxSteps=isMobile?760:420;'

            # Logarithmic scale for more visible size contrast
            'var weights=rawWords.map(function(p){return p[1];});'
            'var minW=Math.min.apply(null,weights);'
            'var maxW=Math.max.apply(null,weights);'
            'var logMin=Math.log(minW+1),logMax=Math.log(maxW+1),logRange=logMax-logMin||1;'
            'var words=rawWords.map(function(p,i){'
            '  var logNorm=(Math.log(p[1]+1)-logMin)/logRange;'
            '  var size=Math.round(minS+logNorm*(maxS-minS));'
            '  var col=colors[i%colors.length];'
            '  return {text:p[0],weight:p[1],size:size,color:col};'
            '});'

            'words.sort(function(a,b){return b.size-a.size;});'

            # Collision detection
            'var placed=[];'
            'function overlaps(r){'
            '  for(var i=0;i<placed.length;i++){'
            '    var p=placed[i];'
            '    if(r.x<p.x+p.w+hitPad&&r.x+r.w+hitPad>p.x&&r.y<p.y+p.h+hitPad&&r.y+r.h+hitPad>p.y)return true;'
            '  }'
            '  return false;'
            '}'
            'function tryPlace(word){'
            '  var size=word.size;'
            '  ctx.font="bold "+size+"px "+font;'
            '  var tw=ctx.measureText(word.text).width;'
            '  var maxWordW=W*(isMobile?0.62:0.58);'
            '  if(tw>maxWordW){'
            '    size=Math.max(minS,Math.floor(size*(maxWordW/tw)));'
            '    ctx.font="bold "+size+"px "+font;'
            '    tw=ctx.measureText(word.text).width;'
            '  }'
            '  var th=size*1.08;'
            '  var cx=W/2,cy=H/2;'
            '  for(var step=0;step<maxSteps;step++){'
            '    var angle=step*0.5;'
            '    var r=step*(isMobile?1.05:1.1);'
            '    var x=cx+r*Math.cos(angle)-tw/2;'
            '    var y=cy+r*Math.sin(angle)*0.55+th/2;'
            '    if(x<hitPad||y-th<hitPad||x+tw>W-hitPad||y>H-hitPad)continue;'
            '    var rect={x:x,y:y-th,w:tw,h:th};'
            '    if(!overlaps(rect)){word._drawSize=size;placed.push(rect);return {x:x,y:y,w:tw,h:th};}'
            '  }'
            '  return null;'
            '}'

            'var placedWords=[];'
            'words.forEach(function(word){'
            '  var pos=tryPlace(word);'
            '  if(pos)placedWords.push({word:word,pos:pos});'
            '});'

            # Draw function
            'function draw(hitItem){'
            '  ctx.clearRect(0,0,W,H);'
            '  placedWords.forEach(function(item){'
            '    var word=item.word,pos=item.pos;'
            '    var drawSize=word._drawSize||word.size;'
            '    var isHit=item===hitItem;'
            '    ctx.save();'
            '    ctx.globalAlpha=(hitItem&&!isHit)?0.35:1;'
            '    if(isHit){'
            '      ctx.shadowColor=word.color;'
            '      ctx.shadowBlur=14;'
            '      ctx.font="bold "+(drawSize+2)+"px "+font;'
            '    }else{'
            '      ctx.font="bold "+drawSize+"px "+font;'
            '    }'
            '    ctx.fillStyle=word.color;'
            '    ctx.fillText(word.text,pos.x,pos.y);'
            '    ctx.restore();'
            '  });'
            '}'
            'draw(null);'

            # Mousemove — hit detection + tooltip
            'canvas.addEventListener("mousemove",function(e){'
            '  var rect=canvas.getBoundingClientRect();'
            '  var scaleX=W/rect.width,scaleY=H/rect.height;'
            '  var mx=(e.clientX-rect.left)*scaleX;'
            '  var my=(e.clientY-rect.top)*scaleY;'
            '  var hit=null;'
            '  placedWords.forEach(function(item){'
            '    var p=item.pos;'
            '    if(mx>=p.x&&mx<=p.x+p.w&&my>=p.y-p.h&&my<=p.y)hit=item;'
            '  });'
            '  canvas.style.cursor=hit?"pointer":"default";'
            '  draw(hit);'
            '  if(hit&&tip){'
            '    var bRect=canvas.getBoundingClientRect();'
            '    var px=hit.pos.x+hit.pos.w/2;'
            '    var py=hit.pos.y-hit.pos.h;'
            '    var scX=bRect.width/W,scY=bRect.height/H;'
            '    tip.textContent=hit.word.text+" · peso: "+hit.word.weight;'
            '    tip.style.left=(px*scX)+"px";'
            '    tip.style.top=(py*scY)+"px";'
            '    tip.style.display="block";'
            '  }else if(tip){'
            '    tip.style.display="none";'
            '  }'
            '});'

            'canvas.addEventListener("mouseleave",function(){'
            '  draw(null);'
            '  if(tip)tip.style.display="none";'
            '});'

            # Click handler
            + (
                'canvas.addEventListener("click",function(e){'
                '  var rect=canvas.getBoundingClientRect();'
                '  var scaleX=W/rect.width,scaleY=H/rect.height;'
                '  var mx=(e.clientX-rect.left)*scaleX;'
                '  var my=(e.clientY-rect.top)*scaleY;'
                '  placedWords.forEach(function(item){'
                '    var p=item.pos;'
                '    if(mx>=p.x&&mx<=p.x+p.w&&my>=p.y-p.h&&my<=p.y){'
                '      var word=item.word.text;'
                '      var weight=item.word.weight;'
                '      ' + on_click +
                '    }'
                '  });'
                '});'
                if on_click else ""
            ) +
            '})()</script>'
        )

class Map(Widget):
    """
    Mapa interactivo con Leaflet + OpenStreetMap. Sin API key.

    Basico:
        Map(center=(-2.897, -79.004), zoom=14)   # Cuenca, Ecuador

    Con marcadores (dict o tupla):
        Map(markers=[
            {"lat": -2.897, "lon": -79.004, "title": "Cuenca", "icon": "GG"},
            (-0.220,  -78.512, "Quito"),
            (-2.897, -79.004, "Cuenca", "Popup HTML", "#6366f1", "CC"),
        ])

    Parametros:
        center          (lat, lon)    centro del mapa
        zoom            int           nivel de zoom 1-19 (default 13)
        height          int           alto en px (default 480)
        markers         list          marcadores como dict o tupla
        search          bool          barra de busqueda (default True)
        geolocation     bool          boton mi-ubicacion (default True)
        route           bool          linea entre markers (default False)
        route_color     str           color ruta (default "#6366f1")
        route_weight    int           grosor ruta px (default 4)
        tile            str           "osm"|"dark"|"topo"|"cycle" (default "osm")
        on_marker_click str           JS al hacer click en un marker

    Marcador completo (dict):
        {"lat": float, "lon": float,
         "title": str, "popup": str,
         "color": str, "icon": str}
    """

    _TILES = {
        "osm":   ("https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                  "&copy; <a href='https://www.openstreetmap.org/copyright'>OpenStreetMap</a>"),
        "dark":  ("https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png",
                  "&copy; Stadia Maps, &copy; OpenStreetMap"),
        "topo":  ("https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
                  "&copy; OpenTopoMap"),
        "cycle": ("https://{s}.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png",
                  "&copy; CyclOSM"),
    }

    def __init__(self, center=None, zoom=13, height=480,
                 markers=None, search=True, geolocation=True,
                 route=False, route_color="#6366f1", route_weight=4,
                 tile="osm", on_marker_click=None, **kwargs):
        self._props          = Widget._extract_props(kwargs)
        self.center          = center
        self.zoom            = zoom
        self.height          = height
        self.markers         = markers or []
        self.search          = search
        self.geolocation     = geolocation
        self.route           = route
        self.route_color     = route_color
        self.route_weight    = route_weight
        self.tile            = tile
        self.on_marker_click = on_marker_click
        self.uid = "map_" + _uuid.uuid4().hex[:8]

    def _normalize_markers(self):
        result = []
        for m in self.markers:
            if isinstance(m, dict):
                result.append(m)
            elif isinstance(m, (list, tuple)):
                d = {"lat": float(m[0]), "lon": float(m[1])}
                if len(m) > 2: d["title"]  = str(m[2])
                if len(m) > 3: d["popup"]  = str(m[3])
                if len(m) > 4: d["color"]  = str(m[4])
                if len(m) > 5: d["icon"]   = str(m[5])
                result.append(d)
        return result

    def render(self):
        import json as _j
        uid  = self.uid
        J    = _j.dumps
        mkrs = self._normalize_markers()
        h    = str(self.height)
        extra = self._resolve_props()

        tile_url, tile_attr = self._TILES.get(self.tile, self._TILES["osm"])
        if self.tile not in self._TILES:
            tile_url, tile_attr = self.tile, "&copy; Map contributors"

        # center
        if self.center:
            center_js = J(list(self.center))
        elif mkrs:
            lats = [m["lat"] for m in mkrs]
            lons = [m["lon"] for m in mkrs]
            center_js = J([sum(lats)/len(lats), sum(lons)/len(lons)])
        else:
            center_js = "[40.4168,-3.7038]"

        wrapper_style = (
            "position:relative;border-radius:12px;overflow:hidden;"
            "width:100%;height:" + h + "px;box-shadow:0 4px 24px rgba(0,0,0,0.12);"
            "z-index:0;isolation:isolate;contain:paint"
        )
        if extra:
            wrapper_style += ";" + extra

        # Search bar HTML (over the map, top-center)
        search_html = ""
        if self.search:
            search_html = (
                '<div id="' + uid + '_sbar" style="'
                'position:absolute;top:10px;left:50%;transform:translateX(-50%);'
                'z-index:30;display:flex;gap:0;width:min(340px,78%);'
                'box-shadow:0 2px 14px rgba(0,0,0,0.22);border-radius:9px;overflow:hidden">'
                '<input id="' + uid + '_q" type="text" placeholder="Buscar lugar..." '
                'autocomplete="off" '
                'style="flex:1;padding:9px 13px;border:none;font-size:14px;'
                'color:#111;background:#fff;outline:none;min-width:0"/>'
                '<button id="' + uid + '_sbtn" title="Buscar" '
                'style="padding:9px 14px;background:#6366f1;color:#fff;'
                'border:none;cursor:pointer;font-size:17px;line-height:1;'
                'flex-shrink:0;transition:background .2s" '
                'onmouseover="this.style.background=\'#4f46e5\'" '
                'onmouseout="this.style.background=\'#6366f1\'">&#128269;</button>'
                '</div>'
            )

        # Geolocation button (bottom-right, above Leaflet zoom)
        geo_html = ""
        if self.geolocation:
            geo_html = (
                '<button id="' + uid + '_geo" title="Mi ubicaci\u00f3n actual" '
                'style="position:absolute;bottom:86px;right:10px;z-index:30;'
                'width:34px;height:34px;background:#fff;'
                'border:2px solid rgba(0,0,0,0.25);border-radius:4px;cursor:pointer;'
                'font-size:16px;display:flex;align-items:center;justify-content:center;'
                'box-shadow:0 1px 5px rgba(0,0,0,0.22);transition:background .15s" '
                'onmouseover="this.style.background=\'#f0f0f0\'" '
                'onmouseout="this.style.background=\'#fff\'">'
                '&#x1f3af;</button>'
            )

        # ── JavaScript ────────────────────────────────────────────────────────
        icon_fn = (
            "function _mkIcon(color,icon){"
            "var d=document.createElement('div');"
            "d.style.cssText='width:30px;height:30px;background:'+color+';'"
            "+'border-radius:50% 50% 50% 0;border:3px solid #fff;'"
            "+'box-shadow:0 2px 8px rgba(0,0,0,0.35);transform:rotate(-45deg);'"
            "+'display:flex;align-items:center;justify-content:center;box-sizing:border-box';"
            "if(icon){"
            "var s=document.createElement('span');"
            "s.style.cssText='transform:rotate(45deg);font-size:12px;line-height:1;user-select:none';"
            "s.textContent=icon;d.appendChild(s);}"
            "return d.outerHTML;}"
        )

        search_js = ""
        if self.search:
            search_js = (
                "var _sq=document.getElementById(" + J(uid+"_q") + ");"
                "var _sb=document.getElementById(" + J(uid+"_sbtn") + ");"
                "var _sm=null;"
                "function _doSearch(){"
                "  var q=_sq.value.trim();if(!q)return;"
                "  _sb.disabled=true;_sb.style.opacity='0.6';"
                # Use Nominatim — add User-Agent header is NOT sent by browsers (CORS), 
                # so we use the referer approach which is fine for client-side calls
                "  fetch('https://nominatim.openstreetmap.org/search'+"
                "    '?format=json&limit=1&addressdetails=1&q='+encodeURIComponent(q))"
                "  .then(function(r){return r.json();})"
                "  .then(function(data){"
                "    _sb.disabled=false;_sb.style.opacity='1';"
                "    if(!data||!data.length){"
                "      _sq.style.boxShadow='inset 0 0 0 2px #ef4444';"
                "      setTimeout(function(){_sq.style.boxShadow='';},2500);"
                "      return;"
                "    }"
                "    var r=data[0];"
                "    var lat=parseFloat(r.lat),lon=parseFloat(r.lon);"
                "    if(_sm){_map.removeLayer(_sm);}"
                "    var parts=r.display_name.split(',');"
                "    var name=parts.slice(0,Math.min(2,parts.length)).join(', ');"
                "    _sm=L.marker([lat,lon]).addTo(_map)"
                "      .bindPopup('<b>'+name+'</b><br><small style=\"color:#666\">'+(r.display_name||'')+'</small>')"
                "      .openPopup();"
                "    _map.flyTo([lat,lon],15,{animate:true,duration:1.0});"
                "  })"
                "  .catch(function(e){"
                "    _sb.disabled=false;_sb.style.opacity='1';"
                "    console.warn('Map search error:',e);"
                "  });"
                "}"
                "_sb.addEventListener('click',_doSearch);"
                "_sq.addEventListener('keydown',function(e){"
                "  if(e.key==='Enter'){e.preventDefault();_doSearch();}"
                "});"
            )

        geo_js = ""
        if self.geolocation:
            geo_js = (
                "var _gb=document.getElementById(" + J(uid+"_geo") + ");"
                "var _gLayers=[];"
                # Use Leaflet's built-in map.locate() — more reliable than raw geolocation API
                # It fires locationfound/locationerror events, handles everything cleanly.
                "_gb.addEventListener('click',function(){"
                "  _gb.textContent='\u23f3';_gb.disabled=true;"
                "  _map.locate({"
                "    setView:false,"
                "    enableHighAccuracy:true,"
                "    timeout:15000,"
                "    maximumAge:0"
                "  });"
                "});"
                "_map.on('locationfound',function(e){"
                "  _gb.textContent='\U0001f3af';_gb.disabled=false;"
                "  _gLayers.forEach(function(l){_map.removeLayer(l);});"
                "  _gLayers=[];"
                "  var lat=e.latlng.lat,lon=e.latlng.lng;"
                "  var acc=Math.round(e.accuracy);"
                # accuracy circle
                "  var circle=L.circle(e.latlng,{"
                "    radius:e.accuracy,"
                "    color:'#6366f1',fillColor:'#6366f1',"
                "    fillOpacity:0.08,weight:1.5,opacity:0.35"
                "  }).addTo(_map);"
                # position dot
                "  var dot=L.circleMarker(e.latlng,{"
                "    radius:8,fillColor:'#6366f1',color:'#fff',weight:3,fillOpacity:1"
                "  }).addTo(_map)"
                "   .bindPopup('<b>Tu ubicaci\u00f3n</b><br><small style=\"color:#888\">Precisi\u00f3n: ±'+acc+' m</small>')"
                "   .openPopup();"
                "  _gLayers.push(circle,dot);"
                "  _map.flyTo(e.latlng,16,{animate:true,duration:1.2});"
                "});"
                "_map.on('locationerror',function(e){"
                "  _gb.textContent='\U0001f3af';_gb.disabled=false;"
                "  var msg='No se pudo obtener tu ubicaci\u00f3n.';"
                "  if(e.message&&e.message.indexOf('denied')>=0)"
                "    msg='Permiso denegado. Habilita la ubicaci\u00f3n en tu navegador.';"
                "  else if(e.message&&e.message.indexOf('timeout')>=0)"
                "    msg='Tiempo de espera agotado. Intenta de nuevo.';"
                "  alert(msg);"
                "});"
            )

        click_fn = click_bind = ""
        if self.on_marker_click:
            click_fn   = "function _onMk(marker){" + self.on_marker_click + "}"
            click_bind = "_mk.on('click',function(){_onMk(m);});"

        route_js = ""
        if self.route:
            route_js = (
                "if(_lls.length>1){"
                "  L.polyline(_lls,{"
                "    color:" + J(self.route_color) + ","
                "    weight:" + str(self.route_weight) + ","
                "    opacity:0.85,lineJoin:'round',dashArray:null"
                "  }).addTo(_map);"
                "}"
            )

        autofit = ""
        if not self.center and len(mkrs) > 1:
            autofit = "if(_lls.length>1){_map.fitBounds(_lls,{padding:[48,48]});}"

        init_js = (
            "(function _im(){"
            "if(typeof L==='undefined'){setTimeout(_im,80);return;}"
            "var el=document.getElementById(" + J(uid) + ");"
            "if(!el||el._mi)return;"
            "el._mi=true;"
            # Explicitly set height in case CSS hasn't loaded
            "el.style.height='" + h + "px';"
            "var _map=L.map(el,{"
            "  zoomControl:true,"
            "  scrollWheelZoom:true,"
            "  attributionControl:true"
            "}).setView(" + center_js + "," + str(self.zoom) + ");"
            "L.tileLayer(" + J(tile_url) + ",{"
            "  attribution:" + J(tile_attr) + ","
            "  maxZoom:19,"
            "  crossOrigin:true"
            "}).addTo(_map);"
            + icon_fn
            + click_fn +
            "var _markers=" + J(mkrs) + ";"
            "var _lls=[];"
            "_markers.forEach(function(m){"
            "  var color=m.color||'#6366f1';"
            "  var icon=m.icon||'';"
            "  var _lIcon=L.divIcon({"
            "    html:_mkIcon(color,icon),"
            "    className:'',"
            "    iconSize:[30,30],"
            "    iconAnchor:[15,30],"
            "    popupAnchor:[0,-34]"
            "  });"
            "  var _mk=L.marker([m.lat,m.lon],{icon:_lIcon}).addTo(_map);"
            "  var _ph='';"
            "  if(m.title)_ph+='<b style=\"font-size:13px\">'+m.title+'</b>';"
            "  if(m.popup)_ph+=(m.title?'<br>':'')+m.popup;"
            "  if(_ph)_mk.bindPopup(_ph);"
            + click_bind +
            "  _lls.push([m.lat,m.lon]);"
            "});"
            + route_js
            + autofit
            + search_js
            + geo_js +
            "})();"
        )

        return (
            '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin=""/>'
            + '<div style="' + wrapper_style + '">'
            + '<div id="' + uid + '" style="position:relative;z-index:1;width:100%;height:' + h + 'px"></div>'
            + search_html
            + geo_html
            + '</div>'
            + '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>'
            + '<script>' + init_js + '</script>'
        )

class Timeline(Widget):
    """
    Widget de línea de tiempo vertical.

    Uso básico:
        Timeline(items=[
            TimelineItem(
                title="Lanzamiento v1.0",
                date="Enero 2024",
                description="Primera versión pública del framework.",
                icon="🚀",
                color="#6366f1",
            ),
            TimelineItem(
                title="Nuevo widget Map",
                date="Marzo 2024",
                description="Integración con Leaflet y OpenStreetMap.",
                image="/assets/map.png",
                icon="🗺️",
                color="#34d399",
            ),
        ])

    Opciones Timeline:
        items       list[TimelineItem]   elementos de la línea de tiempo
        line_color  str                  color de la línea vertical  (default: var(--border))
        alt         bool                 alterna lados izq/der en desktop (default: False)

    Opciones TimelineItem:
        title       str     título del evento              (requerido)
        date        str     fecha o período                (opcional)
        description str     texto descriptivo              (opcional)
        icon        str     emoji o texto para el nodo     (default: "●")
        image       str     URL de imagen                  (opcional)
        color       str     color del nodo y acento        (default: var(--accent))
        tag         str     etiqueta pequeña sobre título  (opcional)
    """

    def __init__(self, items=None, line_color=None, alt=False, **kwargs):
        self._props    = Widget._extract_props(kwargs)
        self.items     = items or []
        self.line_color = line_color or "var(--border)"
        self.alt       = alt

    def render(self):
        extra = self._resolve_props()
        line_color = self.line_color
        alt  = self.alt

        # Wrapper CSS
        wrapper_style = (
            f"position:relative;display:flex;flex-direction:column;gap:0;"
            f"{extra}"
        )

        # Línea vertical central (o izquierda si no es alt)
        line_left = "50%" if alt else "20px"
        line_html = (
            f'<div style="position:absolute;top:0;bottom:0;left:{line_left};'
            f'width:2px;background:{line_color};transform:translateX(-50%);z-index:0;'
            f'border-radius:2px"></div>'
        )

        items_html = ""
        for i, item in enumerate(self.items):
            if not isinstance(item, TimelineItem):
                continue
            items_html += item._render(index=i, alt=alt, line_color=line_color)

        return (
            f'<div style="{wrapper_style}">'
            + line_html
            + items_html
            + '</div>'
        )

class TimelineItem:
    """Elemento individual de un Timeline. Ver Timeline para documentación."""

    def __init__(self, title, date=None, description=None,
                 icon="●", image=None, color=None, tag=None):
        self.title       = title
        self.date        = date
        self.description = description
        self.icon        = icon
        self.image       = image
        self.color       = color or "var(--accent)"
        self.tag         = tag

    def _render(self, index=0, alt=False, line_color="var(--border)"):
        import json as _json
        color = self.color
        # En modo alt, los pares van a la derecha, impares a la izquierda
        go_right = (not alt) or (index % 2 == 0)

        # ── Nodo (círculo en la línea) ──────────────────────────────────────
        node_left = "50%" if alt else "20px"
        node_html = (
            f'<div style="position:absolute;left:{node_left};top:24px;'
            f'transform:translate(-50%,-0%);z-index:1;'
            f'width:36px;height:36px;border-radius:50%;'
            f'background:{color};'
            f'border:3px solid var(--bg);'
            f'box-shadow:0 0 0 2px {color},0 2px 8px rgba(0,0,0,0.15);'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:16px;line-height:1;flex-shrink:0;">'
            f'{self.icon}</div>'
        )

        # ── Tarjeta de contenido ────────────────────────────────────────────
        if alt:
            if go_right:
                card_margin = "margin-left:calc(50% + 28px);margin-right:0;"
            else:
                card_margin = "margin-right:calc(50% + 28px);margin-left:0;text-align:right;"
        else:
            card_margin = "margin-left:52px;margin-right:0;"

        # Imagen — acepta string URL o widget Image (o cualquier Widget con .render())
        img_html = ""
        if self.image is not None:
            if hasattr(self.image, "render"):
                # Widget (Image, Container, etc.) — se renderiza directamente
                img_html = (
                    '<div style="margin-bottom:12px;border-radius:8px;overflow:hidden;">'
                    + self.image.render()
                    + '</div>'
                )
            else:
                # String URL — comportamiento por defecto
                img_html = (
                    f'<img src="{self.image}" alt="{self.title}" '
                    f'style="width:100%;max-height:180px;object-fit:cover;'
                    f'border-radius:8px;margin-bottom:12px;display:block;">'
                )

        # Tag
        tag_html = ""
        if self.tag:
            tag_html = (
                f'<span style="display:inline-block;font-size:10px;font-weight:700;'
                f'letter-spacing:1px;text-transform:uppercase;'
                f'color:{color};background:rgba(99,102,241,0.10);'
                f'padding:2px 8px;border-radius:999px;margin-bottom:6px;">'
                f'{self.tag}</span><br>'
            )

        # Fecha
        date_html = ""
        if self.date:
            date_html = (
                f'<span style="font-size:12px;font-weight:600;'
                f'color:{color};opacity:0.9;margin-bottom:4px;display:block;">'
                f'{self.date}</span>'
            )

        # Título
        title_html = (
            f'<div style="font-size:15px;font-weight:700;'
            f'color:var(--text);margin-bottom:6px;line-height:1.3;">'
            f'{self.title}</div>'
        )

        # Descripción
        desc_html = ""
        if self.description:
            desc_html = (
                f'<div style="font-size:13px;color:var(--text-muted);'
                f'line-height:1.6;">{self.description}</div>'
            )

        card_html = (
            f'<div style="{card_margin}flex:1;'
            f'background:var(--surface);border:1px solid var(--border);'
            f'border-radius:12px;padding:16px;'
            f'box-shadow:0 2px 8px rgba(0,0,0,0.06);'
            f'border-left:3px solid {color};">'
            + img_html
            + tag_html
            + date_html
            + title_html
            + desc_html
            + '</div>'
        )

        # ── Fila completa ───────────────────────────────────────────────────
        return (
            f'<div style="position:relative;display:flex;'
            f'align-items:flex-start;padding-bottom:24px;min-height:64px;">'
            + node_html
            + card_html
            + '</div>'
        )


# ══════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════

class ChartDataset:
    """
    Dataset de datos para Chart.

        ChartDataset(
            label="Ventas 2024",
            data=[120, 190, 80, 250, 300],
            color="#6366f1",          # color de línea/barras (o lista de colores para pastel)
            fill=False,               # área bajo la línea (para line/area)
        )
    """
    def __init__(self, label, data, color=None, fill=False,
                 border_width=2, point_radius=4,
                 background_color=None):
        self.label            = label
        self.data             = data
        self.color            = color
        self.fill             = fill
        self.border_width     = border_width
        self.point_radius     = point_radius
        self.background_color = background_color  # None = auto

class Chart(Widget):
    """
    Gráfico interactivo usando Chart.js (cargado desde CDN).

    Tipos soportados:
        "bar"        — barras verticales
        "bar_h"      — barras horizontales
        "line"       — líneas
        "area"       — área (línea con fill)
        "pie"        — pastel
        "doughnut"   — dona
        "radar"      — radar / araña
        "scatter"    — dispersión (data = [{x,y},...])
        "bubble"     — burbuja (data = [{x,y,r},...])

    Uso básico:
        Chart(
            type="bar",
            labels=["Ene","Feb","Mar","Abr","May"],
            datasets=[
                ChartDataset("Ventas", [120,190,80,250,300], color="#6366f1"),
                ChartDataset("Gastos", [80,100,70,150,200], color="#f472b6"),
            ],
            title="Resumen mensual",
        )

        # Pastel:
        Chart(
            type="pie",
            labels=["Python","JS","Rust","Go"],
            datasets=[ChartDataset("Uso", [45,30,15,10])],
        )

    Parámetros:
        type         str    tipo de gráfico (ver arriba)
        labels       list   etiquetas del eje X (o sectores para pie/doughnut)
        datasets     list[ChartDataset]
        title        str    título del gráfico
        height       int    altura en px (default: 350)
        legend       bool   mostrar leyenda (default: True)
        grid         bool   mostrar cuadrícula (default: True)
        animated     bool   animación de entrada (default: True)
        responsive   bool   ancho responsive (default: True)
        x_label      str    etiqueta eje X
        y_label      str    etiqueta eje Y
        stacked      bool   barras apiladas (default: False)
        colors       list   paleta de colores por defecto
        tooltip_mode str    "index" | "point" | "nearest"
        download     bool   botón descargar PNG (default: False)
    """

    DEFAULT_COLORS = [
        "#6366f1", "#f472b6", "#34d399", "#fb923c",
        "#38bdf8", "#a78bfa", "#4ade80", "#fbbf24",
        "#f87171", "#2dd4bf",
    ]

    def __init__(self, type="bar", labels=None, datasets=None,
                 title=None, height=350, legend=True, grid=True,
                 animated=True, responsive=True,
                 x_label=None, y_label=None, stacked=False,
                 colors=None, tooltip_mode="index",
                 download=False, text_color=None, muted_text_color=None, **kwargs):
        self._props       = Widget._extract_props(kwargs)
        self.chart_type   = type
        self.labels       = labels or []
        self.datasets     = datasets or []
        self.title        = title
        self.height       = height
        self.legend       = legend
        self.grid         = grid
        self.animated     = animated
        self.responsive   = responsive
        self.x_label      = x_label
        self.y_label      = y_label
        self.stacked      = stacked
        self.colors       = colors or self.DEFAULT_COLORS
        self.tooltip_mode = tooltip_mode
        self.download     = download
        self.text_color   = text_color
        self.muted_text_color = muted_text_color
        self.uid = f"chart_{_uuid.uuid4().hex[:8]}"

    def _resolve_type(self):
        """Map internal type to Chart.js type."""
        if self.chart_type == "bar_h":
            return "bar"
        if self.chart_type == "area":
            return "line"
        return self.chart_type

    def _build_datasets_js(self):
        import json as _json

        def _to_rgba(c, alpha):
            if not isinstance(c, str):
                return c
            s = c.strip()
            if s.startswith(("rgba(", "rgb(", "hsl(", "hsla(")):
                return s
            if s.startswith("#"):
                h = s[1:]
                if len(h) == 3:
                    h = "".join(ch * 2 for ch in h)
                if len(h) == 6:
                    try:
                        r = int(h[0:2], 16)
                        g = int(h[2:4], 16)
                        b = int(h[4:6], 16)
                        return f"rgba({r},{g},{b},{alpha})"
                    except ValueError:
                        return s
            return s

        result = []
        is_pie_like = self.chart_type in ("pie", "doughnut")

        for idx, ds in enumerate(self.datasets):
            color = ds.color or self.colors[idx % len(self.colors)]

            if is_pie_like:
                # Pie: each slice gets its own color
                bg_colors = [self.colors[i % len(self.colors)] for i in range(len(ds.data))]
                d = {
                    "label": ds.label,
                    "data": ds.data,
                    "backgroundColor": bg_colors,
                    "borderWidth": 2,
                    "borderColor": "#060818",
                }
            else:
                fill_val = ds.fill or (self.chart_type == "area")
                # Convert color to rgba for background
                bg_opacity = 0.15 if fill_val else 0.7
                d = {
                    "label": ds.label,
                    "data": ds.data,
                    "borderColor": color,
                    "backgroundColor": (
                        ds.background_color
                        if ds.background_color
                        else _to_rgba(color, bg_opacity)
                    ),
                    "borderWidth": ds.border_width,
                    "pointRadius": ds.point_radius,
                    "fill": fill_val,
                    "tension": 0.4,
                }
                # For bar charts: use color directly as background
                if self.chart_type in ("bar", "bar_h"):
                    d["backgroundColor"] = color

            result.append(d)

        return _json.dumps(result)

    def render(self):
        import json as _json
        uid        = self.uid
        extra      = self._resolve_props()
        cjs_type   = self._resolve_type()
        datasets_js = self._build_datasets_js()
        labels_js  = _json.dumps(self.labels)
        height     = self.height
        text_color_js = _json.dumps(self.text_color or "")
        muted_color_js = _json.dumps(self.muted_text_color or "")

        # Options
        is_horizontal = (self.chart_type == "bar_h")
        is_pie_like   = self.chart_type in ("pie", "doughnut")

        scales_config = "scales:{}" if is_pie_like else (
            f"scales:{{"
            f"  x:{{"
            f"    {'stacked:true,' if self.stacked else ''}"
            f"    grid:{{display:{'true' if self.grid else 'false'},color:'rgba(128,128,128,0.1)'}},"
            f"    ticks:{{color:'var(--text-muted)'}},"
            + (f"    title:{{display:true,text:{_json.dumps(self.x_label or '')},color:'var(--text-muted)'}}" if self.x_label else "")
            + f"  }},"
            f"  y:{{"
            f"    {'stacked:true,' if self.stacked else ''}"
            f"    grid:{{display:{'true' if self.grid else 'false'},color:'rgba(128,128,128,0.1)'}},"
            f"    ticks:{{color:'var(--text-muted)'}},"
            + (f"    title:{{display:true,text:{_json.dumps(self.y_label or '')},color:'var(--text-muted)'}}" if self.y_label else "")
            + f"  }}"
            f"}}"
        )

        indexAxis = '"x"' if not is_horizontal else '"y"'

        options_js = (
            f"{{"
            f"  responsive:{str(self.responsive).lower()},"
            f"  maintainAspectRatio:false,"
            f"  indexAxis:{indexAxis},"
            f"  animation:{{duration:{'800' if self.animated else '0'}}},"
            f"  plugins:{{"
            f"    legend:{{display:{'true' if self.legend else 'false'},"
            f"             labels:{{color:'var(--text)',font:{{size:13}}}}}},"
            f"    tooltip:{{mode:{_json.dumps(self.tooltip_mode)},intersect:false}},"
            + (f"    title:{{display:true,text:{_json.dumps(self.title or '')},color:'var(--text)',"
               f"            font:{{size:15,weight:'600'}},padding:{{bottom:16}}}}" if self.title else "")
            + f"  }},"
            f"  {scales_config}"
            f"}}"
        )

        download_btn = ""
        if self.download:
            download_btn = (
                f'<button onclick="(function(){{var a=document.createElement(\'a\');'
                f'a.download=\'chart.png\';a.href=window[\'_chart_{uid}\'].toBase64Image();'
                f'a.click();}})()" '
                f'style="position:absolute;top:8px;right:8px;background:var(--surface-2);'
                f'border:1px solid var(--border);border-radius:6px;padding:6px 12px;'
                f'font-size:12px;cursor:pointer;color:var(--text)">&#11015; PNG</button>'
            )

        wrapper_style = f"position:relative;{'height:'+str(height)+'px'};width:100%;{extra}"

        js = f"""
<script>
(function(){{
  var cdnUrl="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js";
  var customText={text_color_js};
  var customMuted={muted_color_js};

  function cssVar(name, fallback){{
    var raw=(getComputedStyle(document.documentElement).getPropertyValue(name)||"").trim();
    return raw || fallback;
  }}

  function applyThemeColors(chart){{
    var textColor=customText || cssVar("--text", "#111827");
    var mutedColor=customMuted || cssVar("--text-muted", "#6b7280");
    var gridColor=cssVar("--border", "rgba(128,128,128,0.2)");
    var opts=chart.options||{{}};

    if(opts.plugins&&opts.plugins.legend&&opts.plugins.legend.labels){{
      opts.plugins.legend.labels.color=textColor;
    }}
    if(opts.plugins&&opts.plugins.title){{
      opts.plugins.title.color=textColor;
    }}

    if(opts.scales){{
      ["x","y","r"].forEach(function(axis){{
        var sc=opts.scales[axis];
        if(!sc)return;
        if(sc.ticks) sc.ticks.color=mutedColor;
        if(sc.title) sc.title.color=mutedColor;
        if(sc.grid && sc.grid.display!==false) sc.grid.color=gridColor;
      }});
    }}
  }}

  function init(){{
    var ctx=document.getElementById("{uid}_canvas").getContext("2d");
    var options={options_js};
    var chart=new Chart(ctx,{{
      type:{_json.dumps(cjs_type)},
      data:{{labels:{labels_js},datasets:{datasets_js}}},
      options:options
    }});
    applyThemeColors(chart);
    chart.update("none");

    var obs=new MutationObserver(function(muts){{
      for(var i=0;i<muts.length;i++){{
        if(muts[i].attributeName==="data-theme"){{
          applyThemeColors(chart);
          chart.update("none");
          break;
        }}
      }}
    }});
    obs.observe(document.documentElement,{{attributes:true,attributeFilter:["data-theme"]}});

    window["_chart_{uid}"]=chart;
  }}

  if(window.Chart){{init();}}
  else{{
    var s=document.createElement("script");
    s.src=cdnUrl;
    s.onload=function(){{init();}};
    document.head.appendChild(s);
  }}
}})();
</script>
"""

        return (
            f'<div style="{wrapper_style}">'
            + download_btn
            + f'<canvas id="{uid}_canvas" style="width:100%;height:100%"></canvas>'
            + f'</div>'
            + js
        )


# ══════════════════════════════════════════════════════════
# CALENDAR — Calendario completo con vistas mes/semana/día
# ══════════════════════════════════════════════════════════

