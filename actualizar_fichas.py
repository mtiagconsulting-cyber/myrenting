#!/usr/bin/env python3
"""
actualizar_fichas.py — Regenera la seccion de comparador de las fichas de modelo
con el diseno v4 (Opcion A) y datos frescos (plazo/km), SIN romper el resto.

Fuente de datos: el bloque const _OFERTAS de index.html (verdad tras el inyector
seguro de la home). Solo toca fichas cuyo modelo tiene ofertas; las demas no se
tocan. Guardarrailes: valida marcadores clave por pagina o restaura backup.

Uso:
  python3 actualizar_fichas.py            # todas las fichas con datos
  python3 actualizar_fichas.py audi-a1 nissan-qashqai   # solo esos slugs (test)
"""
import re, json, sys, html as _h, shutil
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).resolve().parent
IDX = BASE / 'index.html'

GC = {'arval':'#C41E1E','ayvens':'#1E4DB7','alphabet':'#6D28D9','kinto':'#15803D',
      'quadis':'#B45309','kia armotors':'#B91C1C','leasys':'#0891B2','revel':'#0F766E',
      'm automoción':'#16224E','m automocion':'#16224E'}
MARKERS = ['compare-grid', 'abrirModalGestora', 'window._OFERTAS', 'car-header']

def clean(s): return re.sub(r'\s+', ' ', re.sub(r'[\x00-\x1f\x7f]', ' ', str(s or ''))).strip()
def esc(s): return _h.escape(str(s))
def kmf(k):
    try: return f"{int(k):,}".replace(',','.')
    except: return k
def ini(n): return ''.join(w[0] for w in str(n).split()[:2]).upper()
def slugify(s):
    s = s.lower()
    for a,b in [('á','a'),('é','e'),('í','i'),('ó','o'),('ú','u'),('ñ','n'),('ü','u')]:
        s = s.replace(a,b)
    return re.sub(r'-+','-', re.sub(r'[^a-z0-9]+','-', s)).strip('-')

NEW_CSS = """
    /* ===== FICHA v4 ===== */
    .search-bar{display:none !important;}
    .sub-bar{background:#fff;border-bottom:1px solid var(--border);}
    .sub-inner{max-width:1080px;margin:0 auto;padding:14px 32px;display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap;}
    .crumb{font-size:13px;color:var(--ink-4);display:flex;align-items:center;gap:7px;flex-wrap:wrap;}
    .crumb a{color:var(--ink-4);text-decoration:none;}.crumb a:hover{color:var(--accent);}
    .crumb .sep{color:var(--ink-5);}.crumb .cur{color:var(--ink);font-weight:700;}
    .mini-search{display:flex;align-items:center;gap:8px;background:var(--surface-2,#f5f2ef);border:1.5px solid var(--border);border-radius:12px;padding:7px 8px 7px 14px;min-width:320px;}
    .mini-search svg{color:var(--ink-5);flex-shrink:0;}
    .mini-search input{flex:1;border:none;background:transparent;font-family:inherit;font-size:14px;color:var(--ink);outline:none;font-weight:500;}
    .mini-search button{background:var(--accent);color:#fff;border:none;border-radius:9px;padding:8px 16px;font-size:13px;font-weight:700;font-family:inherit;cursor:pointer;white-space:nowrap;}
    .ch-wrap{max-width:1080px;margin:0 auto;padding:26px 32px 8px;}
    .car-header{background:#fff;border-radius:20px;border:1px solid var(--border);padding:28px 30px;display:flex;gap:30px;align-items:center;box-shadow:0 8px 30px rgba(30,20,15,.06);}
    .car-img-wrap{width:250px;height:160px;flex-shrink:0;background:radial-gradient(circle at 50% 40%,#f6f3f0,#eceae6);border-radius:16px;display:flex;align-items:center;justify-content:center;padding:14px;}
    .car-img-wrap img{width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 10px 14px rgba(0,0,0,.14));}
    .car-info{flex:1;min-width:0;}
    .car-brand{font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:1.5px;color:var(--accent);margin-bottom:5px;}
    .car-name{font-size:32px;font-weight:850;letter-spacing:-1px;margin-bottom:16px;line-height:1;}
    .car-specs{display:flex;gap:10px;flex-wrap:wrap;}
    .spec-item{display:flex;flex-direction:column;gap:3px;background:var(--surface-2,#f5f2ef);border:1px solid var(--border);border-radius:11px;padding:9px 14px;}
    .spec-label{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--ink-5);}
    .spec-val{font-size:14px;font-weight:700;color:var(--ink-2,#2a2320);}
    .car-price-hero{text-align:right;flex-shrink:0;padding-left:26px;border-left:1px solid var(--border);}
    .price-desde{font-size:12px;color:var(--ink-4);font-weight:600;}
    .price-big{font-size:46px;font-weight:850;color:var(--accent);letter-spacing:-2.5px;line-height:.95;}
    .price-unit{font-size:13px;color:var(--ink-4);margin-top:2px;}
    .price-badge{background:#ecfdf3;color:#15803d;font-size:11.5px;font-weight:700;padding:5px 12px;border-radius:99px;margin-top:12px;display:inline-block;border:1px solid #bbf7d0;}
    .comparador-section{max-width:1080px;margin:14px auto 0;padding:0 32px;}
    .compare-title{font-size:19px;font-weight:820;letter-spacing:-.4px;color:var(--ink);margin-bottom:14px;text-transform:none;}
    .cmp-cond{font-size:13.5px;color:var(--ink-3,#4a423d);margin-bottom:14px;font-weight:600;display:flex;align-items:center;gap:8px;flex-wrap:wrap;}
    .cmp-cond select{font-family:inherit;font-size:13px;font-weight:700;color:var(--accent);border:1.5px solid var(--border);border-radius:8px;padding:5px 8px;background:#fff;cursor:pointer;}
    .filters{background:#fff;border-radius:14px;border:1px solid var(--border);padding:14px 16px;margin-bottom:18px;display:flex;gap:12px;flex-wrap:wrap;align-items:flex-end;box-shadow:0 2px 14px rgba(0,0,0,.05);}
    .f-group{display:flex;flex-direction:column;gap:4px;flex:1;min-width:150px;}
    .f-label{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:var(--ink-5);}
    .f-select{border:1.5px solid var(--border);border-radius:9px;padding:9px 11px;font-size:13.5px;font-family:inherit;background:#fff;color:var(--ink);cursor:pointer;}
    .f-count{font-size:12px;color:var(--ink-4);align-self:flex-end;padding-bottom:10px;white-space:nowrap;}
    .compare-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:16px;margin-top:4px;}
    .offer-card{background:#fff;border:1.5px solid var(--border);border-radius:18px;padding:20px;display:flex;flex-direction:column;gap:13px;transition:box-shadow .18s,transform .18s;position:relative;}
    .offer-card:hover{box-shadow:0 12px 34px rgba(30,20,15,.11);transform:translateY(-3px);}
    .offer-card.best{border-color:var(--accent);box-shadow:0 10px 30px rgba(232,56,13,.13);}
    .oc-rank{position:absolute;top:-10px;right:16px;background:var(--accent);color:#fff;font-size:10.5px;font-weight:800;letter-spacing:.4px;padding:4px 11px;border-radius:99px;text-transform:uppercase;box-shadow:0 4px 12px rgba(232,56,13,.35);}
    .oc-top{display:flex;align-items:center;gap:12px;}
    .oc-logo{width:44px;height:44px;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:800;font-size:14px;flex-shrink:0;position:relative;overflow:hidden;}
    .oc-logo img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;padding:6px;display:none;}
    .oc-logo.has-logo{background:#fff!important;border:1px solid #ece5db;width:auto;min-width:44px;max-width:104px;padding:0 8px;}
    .oc-logo.has-logo>span{display:none;}
    .oc-logo.has-logo img{display:block;position:static;inset:auto;width:auto;max-width:88px;height:32px;padding:0;}
    .oc-name{font-size:16px;font-weight:800;}.oc-meta{font-size:12px;color:var(--ink-4);margin-top:1px;}
    .oc-version{font-size:12.5px;color:var(--ink-3,#4a423d);background:var(--surface-2,#f5f2ef);border-radius:9px;padding:9px 12px;line-height:1.4;min-height:38px;display:flex;align-items:center;}
    .oc-cond{display:flex;gap:8px;flex-wrap:wrap;}
    .oc-cond span{font-size:11.5px;font-weight:700;color:var(--ink-3,#4a423d);background:#fff;border:1.5px solid var(--border);border-radius:8px;padding:5px 9px;}
    .oc-bottom{display:flex;align-items:flex-end;justify-content:space-between;gap:8px;}
    .oc-price{display:flex;align-items:baseline;gap:3px;}
    .oc-desde{font-size:11px;color:var(--ink-4);font-weight:600;margin-right:3px;}
    .oc-price b{font-size:30px;font-weight:850;color:var(--ink);letter-spacing:-1.5px;}
    .oc-unit{font-size:13px;color:var(--ink-4);font-weight:600;}
    .oc-save{background:#ecfdf3;color:#15803d;font-size:12px;font-weight:800;padding:4px 10px;border-radius:8px;border:1px solid #bbf7d0;}
    .oc-cta{display:flex;gap:9px;margin-top:2px;}
    .btn-card-info{flex:0 0 auto;background:#fff;border:1.5px solid var(--border);color:var(--ink-2,#2a2320);border-radius:11px;padding:11px 15px;font-size:13px;font-weight:700;font-family:inherit;cursor:pointer;}
    .btn-card-ver{flex:1;background:var(--accent);color:#fff;border:none;border-radius:11px;padding:11px;font-size:13.5px;font-weight:800;font-family:inherit;cursor:pointer;}
    .hidden-card{display:none !important;}
    @media(max-width:820px){
      .car-header{flex-direction:column;align-items:stretch;gap:20px;text-align:center;}
      .car-img-wrap{width:100%;height:180px;}.car-specs{justify-content:center;}
      .car-price-hero{text-align:center;padding-left:0;border-left:none;border-top:1px solid var(--border);padding-top:18px;}
      .compare-grid{grid-template-columns:1fr;}
      .ch-wrap,.comparador-section,.sub-inner{padding-left:18px;padding-right:18px;}
      .mini-search{min-width:0;width:100%;}
    }
"""

# JS: render dinamico segun condiciones (plazo/km/cliente/gestora)
JS_RENDER = r"""
<script>
(function(){
  var GC={arval:'#C41E1E',ayvens:'#1E4DB7',alphabet:'#6D28D9',kinto:'#15803D',quadis:'#B45309','kia armotors':'#B91C1C',leasys:'#0891B2',revel:'#0F766E','m automoción':'#16224E','m automocion':'#16224E'};
  function ini(n){return (n||'').split(' ').slice(0,2).map(function(w){return w[0]||'';}).join('').toUpperCase();}
  function gslug(n){return (n||'').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-').replace(/^-+|-+$/g,'');}
  function ocLogo(fuente,gestora,color){return '<div class="oc-logo" style="background:'+color+'"><span>'+ini(gestora)+'</span><img src="/img/gestoras/'+gslug(fuente)+'.png" alt="'+esc(gestora)+'" loading="lazy" onload="this.parentNode.classList.add(\'has-logo\')" onerror="this.remove()"></div>';}
  function kmf(k){k=parseInt(k);return isNaN(k)?'—':(''+k).replace(/\B(?=(\d{3})+(?!\d))/g,'.');}
  function esc(s){return (''+s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
  function val(id){var e=document.getElementById(id);return e?e.value:'';}
  window.renderComparador=function(){
    var data=window._OFERTAS||{};
    var plazo=val('cond-plazo'),km=val('cond-km'),tipo=val('f-tipo'),fuente=val('f-fuente');
    var vehiculo=(document.querySelector('.car-name')||{}).textContent||'';
    var groups=[];
    Object.keys(data).forEach(function(f){
      if(fuente&&f!==fuente)return;
      var offs=data[f].filter(function(o){
        if(plazo&&String(o.plazo)!==plazo)return false;
        if(km&&String(o.km)!==km)return false;
        if(tipo&&o.tipo!==tipo)return false;
        return true;
      });
      if(!offs.length)return;
      offs.sort(function(a,b){return parseFloat(a.price)-parseFloat(b.price);});
      groups.push({fuente:f,best:offs[0],n:offs.length,tipos:offs.map(function(o){return o.tipo;})});
    });
    groups.sort(function(a,b){return parseFloat(a.best.price)-parseFloat(b.best.price);});
    var grid=document.getElementById('compare-grid');
    var nr=document.getElementById('no-results-msg');
    if(!groups.length){if(grid)grid.innerHTML='';if(nr)nr.style.display='block';setCount(0);return;}
    if(nr)nr.style.display='none';
    var prices=groups.map(function(g){return parseFloat(g.best.price);});
    var media=prices.reduce(function(a,b){return a+b;},0)/prices.length;
    grid.innerHTML=groups.map(function(g,i){
      var o=g.best,best=i===0,color=GC[g.fuente]||'#6a615b';
      var save=Math.round((media-parseFloat(o.price))/media*100);
      var savehtml=(best&&save>=3)?'<div class="oc-save">&#8722;'+save+'%</div>':'<div></div>';
      var rank=best?'<div class="oc-rank">&#9733; Mejor precio</div>':'';
      var tset={};g.tipos.forEach(function(t){if(t)tset[t]=1;});
      var meta=Object.keys(tset).map(cap).join(', ')+' &middot; '+g.n+' oferta'+(g.n!==1?'s':'');
      var cond='';
      if(o.plazo&&o.plazo!=='—')cond+='<span>&#128337; '+o.plazo+' meses</span>';
      if(o.km&&o.km!=='—')cond+='<span>&#128663; '+kmf(o.km)+' km/año</span>';
      var gn=o.gestora.replace(/'/g,"\\'"),vj=vehiculo.replace(/'/g,"\\'");
      return '<div class="offer-card'+(best?' best':'')+'">'+rank
        +'<div class="oc-top">'+ocLogo(g.fuente,o.gestora,color)
        +'<div><div class="oc-name">'+esc(o.gestora)+'</div><div class="oc-meta">'+meta+'</div></div></div>'
        +'<div class="oc-version">'+esc(o.version||'Versión estándar')+'</div>'
        +(cond?'<div class="oc-cond">'+cond+'</div>':'')
        +'<div class="oc-bottom"><div class="oc-price"><span class="oc-desde">desde</span><b>'+parseInt(o.price)+'</b><span class="oc-unit">&euro;/mes</span></div>'+savehtml+'</div>'
        +'<div class="oc-cta"><button class="btn-card-info" onclick="abrirModal(\''+gn+'\',\''+vj+'\');return false;">Solicitar info</button>'
        +'<button class="btn-card-ver" onclick="abrirModalGestora(\''+g.fuente+'\',\''+gn+'\',\''+vj+'\');return false;">Ver ofertas &rarr;</button></div></div>';
    }).join('');
    setCount(groups.length);
    var ph=document.querySelector('.price-big');
    if(ph)ph.innerHTML=parseInt(prices[0])+'<sup style="font-size:20px">&#8364;</sup>';
  };
  function cap(s){return s?s.charAt(0).toUpperCase()+s.slice(1):s;}
  function setCount(n){var e=document.getElementById('filter-count');if(e)e.textContent=n+' gestora'+(n!==1?'s':'');}
  window.filtrarTabla=window.renderComparador;
  window.resetFiltros=function(){['cond-plazo','cond-km','f-tipo','f-fuente'].forEach(function(id){var e=document.getElementById(id);if(e)e.value='';});renderComparador();};
})();
</script>
"""


def build_offer_data(offers):
    """Agrupa ofertas por fuente -> lista de dicts para window._OFERTAS."""
    g = defaultdict(list)
    for o in offers:
        g[o['fuente'].lower()].append(o)
    data = {}
    for f, lst in g.items():
        lst.sort(key=lambda o: o['precio_desde'])
        def _norm(x):
            x = clean(x)
            return '' if x in ('—','-','None') else x
        data[f] = [dict(gestora=clean(o['fuente']), tipo=clean(o.get('tipo','')), fuel=clean(o.get('fuel','')),
                        plazo=_norm(o.get('duracion','')), km=_norm(o.get('km','')),
                        version=_norm(o.get('version','')), price=str(int(o['precio_desde'])))
                   for o in lst]
    return data


def static_cards(data, media, model):
    groups = []
    for f, lst in data.items():
        best = lst[0]
        groups.append((f, best, len(lst), sorted({o['tipo'] for o in lst if o['tipo']})))
    groups.sort(key=lambda x: float(x[1]['price']))
    out = []
    for i,(f,o,n,tipos) in enumerate(groups):
        best=i==0; color=GC.get(f,'#6a615b')
        save=round((media-float(o['price']))/media*100) if media else 0
        savehtml=f'<div class="oc-save">&#8722;{save}%</div>' if best and save>=3 else '<div></div>'
        rank='<div class="oc-rank">&#9733; Mejor precio</div>' if best else ''
        meta=f"{', '.join(t.capitalize() for t in tipos) or 'Empresa'} &middot; {n} oferta{'s' if n!=1 else ''}"
        cond=''
        if o['plazo'] and o['plazo']!='': cond+=f"<span>&#128337; {o['plazo']} meses</span>"
        if o['km'] and o['km']!='': cond+=f"<span>&#128663; {kmf(o['km'])} km/año</span>"
        nm=o['gestora'].replace("'","\\'"); mj=model.replace("'","\\'")
        out.append(f'''    <div class="offer-card{' best' if best else ''}">
      {rank}
      <div class="oc-top"><div class="oc-logo" style="background:{color}"><span>{ini(o['gestora'])}</span><img src="/img/gestoras/{slugify(f)}.png" alt="{esc(o['gestora'])}" loading="lazy" onload="this.parentNode.classList.add('has-logo')" onerror="this.remove()"></div><div><div class="oc-name">{esc(o['gestora'])}</div><div class="oc-meta">{meta}</div></div></div>
      <div class="oc-version">{esc(o['version'] or 'Versión estándar')}</div>
      {'<div class="oc-cond">'+cond+'</div>' if cond else ''}
      <div class="oc-bottom"><div class="oc-price"><span class="oc-desde">desde</span><b>{int(float(o['price']))}</b><span class="oc-unit">&euro;/mes</span></div>{savehtml}</div>
      <div class="oc-cta"><button class="btn-card-info" onclick="abrirModal('{nm}','{mj}');return false;">Solicitar info</button><button class="btn-card-ver" onclick="abrirModalGestora('{f}','{nm}','{mj}');return false;">Ver ofertas &rarr;</button></div>
    </div>''')
    return '\n'.join(out)


def transform(path, offers):
    c = path.read_text(encoding='utf-8')
    if 'compare-grid' not in c or 'car-header' not in c:
        return None, 'sin comparador'
    mm = re.search(r'class="car-name">([^<]+)</div>', c)
    bm = re.search(r'class="car-brand">([^<]+)</div>', c)
    im = re.search(r'class="car-img-wrap"><img src="([^"]+)"', c)
    if not (mm and bm and im): return None, 'sin cabecera'
    model, brand, img = mm.group(1), bm.group(1), im.group(1)
    dm = re.search(r'Actualizado</span><span class="spec-val">([^<]+)</span>', c)
    date = dm.group(1) if dm else '—'

    data = build_offer_data(offers)
    prices = [float(o['precio_desde']) for o in offers]
    gmin = int(min(prices)); media = sum(prices)/len(prices)
    n_off = len(offers); n_gest = len(data)
    plazos = sorted({str(o.get('duracion','')) for o in offers if o.get('duracion')}, key=lambda x:int(x) if x.isdigit() else 999)
    kms = sorted({str(o.get('km','')) for o in offers if o.get('km')}, key=lambda x:int(x) if x.isdigit() else 999)
    tipos = sorted({o.get('tipo','') for o in offers if o.get('tipo')})

    # 1) barra de busqueda nueva
    bslug = 'renting-' + slugify(brand)
    newnav = f'''<nav class="nav">
  <div class="nav-brand"><a class="nav-logo" href="/">My<span>Renting</span></a></div>
  <a href="/" class="nav-back">&larr; Todas las ofertas</a>
</nav>

<div class="sub-bar"><div class="sub-inner">
  <nav class="crumb"><a href="/">Inicio</a><span class="sep">&rsaquo;</span><a href="/{bslug}.html">{esc(brand)}</a><span class="sep">&rsaquo;</span><span class="cur">{esc(model)}</span></nav>
  <div class="mini-search">
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
    <input type="text" value="{esc(model)}" placeholder="Busca otro coche&hellip;" onkeydown="if(event.key==='Enter')window.location.href='/?q='+encodeURIComponent(this.value)">
    <button onclick="window.location.href='/?q='+encodeURIComponent(this.previousElementSibling.value)">Comparar &rarr;</button>
  </div>
</div></div>'''
    # Idempotente: quita TODAS las sub-bars previas (evita duplicados al regenerar)
    c = re.sub(r'\s*<div class="sub-bar">.*?Comparar &rarr;</button>\s*</div>\s*</div>\s*</div>', '', c, flags=re.DOTALL)
    # y sustituye el nav (con o sin vieja search-bar) por nav + UNA sub-bar
    c2 = re.sub(r'<nav class="nav">.*?</nav>\s*(?:<div class="search-bar">.*?</div>\s*</div>\s*</div>)?',
                lambda _: newnav + '\n\n', c, count=1, flags=re.DOTALL)
    if c2 == c:
        c2 = re.sub(r'<div class="search-bar">.*?</div>\s*</div>\s*</div>', '', c, count=1, flags=re.DOTALL)
    c = c2

    # 2) car-header
    header = f'''<div class="ch-wrap">
<div class="car-header">
  <div class="car-img-wrap"><img src="{img}" alt="{esc(model)}" loading="eager" onerror="this.style.display='none'"></div>
  <div class="car-info">
    <div class="car-brand">{esc(brand)}</div><div class="car-name">{esc(model)}</div>
    <div class="car-specs">
      <div class="spec-item"><span class="spec-label">Gestoras</span><span class="spec-val">{n_gest}</span></div>
      <div class="spec-item"><span class="spec-label">Ofertas</span><span class="spec-val">{n_off}</span></div>
      <div class="spec-item"><span class="spec-label">Actualizado</span><span class="spec-val">{date}</span></div>
    </div>
  </div>
  <div class="car-price-hero"><div class="price-desde">desde</div><div class="price-big">{gmin}<sup style="font-size:20px">&#8364;</sup></div><div class="price-unit">al mes</div><div class="price-badge">&#10003; {n_gest} gestoras comparadas</div></div>
</div></div>'''
    c = re.sub(r'<div class="ch-wrap">.*?</div>\s*</div>\s*</div>(?=\s*\n\s*<!-- COMPARADOR)', header, c, count=1, flags=re.DOTALL)

    # 3) seccion comparador (title + cond + filtros + grid)
    def opts(id_, label_all, values, unit=''):
        o = [f'<option value="">{label_all}</option>']
        for v in values:
            disp = f'{v} {unit}'.strip() if unit else v
            o.append(f'<option value="{v}">{disp}</option>')
        return f'<select class="f-select" id="{id_}" onchange="renderComparador()">' + ''.join(o) + '</select>'
    cond_plazo = f'<select id="cond-plazo" onchange="renderComparador()"><option value="">cualquier plazo</option>' + ''.join(f'<option value="{p}">{p} meses</option>' for p in plazos) + '</select>'
    cond_km = f'<select id="cond-km" onchange="renderComparador()"><option value="">cualquier km</option>' + ''.join(f'<option value="{k}">{kmf(k)} km/año</option>' for k in kms) + '</select>'
    tipo_opts = ''.join(f'<option value="{t}">{t.capitalize()}</option>' for t in tipos)
    fuente_opts = ''.join(f'<option value="{f}">{data[f][0]["gestora"]}</option>' for f in data)
    sec = f'''<div class="compare-title">Compara las {n_gest} gestoras disponibles</div>

  <div class="cmp-cond">Comparando a {cond_plazo} · {cond_km}</div>

  <div class="filters">
    <div class="f-group"><label class="f-label">Cliente</label><select class="f-select" id="f-tipo" onchange="renderComparador()"><option value="">Empresa y particular</option>{tipo_opts}</select></div>
    <div class="f-group"><label class="f-label">Gestora</label><select class="f-select" id="f-fuente" onchange="renderComparador()"><option value="">Todas las gestoras</option>{fuente_opts}</select></div>
    <span class="f-count" id="filter-count">{n_gest} gestoras</span>
    <button class="f-reset" id="btn-reset" onclick="resetFiltros()" style="display:none">&#x2715; Limpiar</button>
  </div>

  <div class="compare-grid" id="compare-grid">
{static_cards(data, media, model)}
  </div>'''
    c = re.sub(r'<div class="compare-title">.*?<div class="compare-grid" id="compare-grid">.*?</div>\s*(?=\n\s*<div class="no-results-cards")',
               sec + '\n\n  ', c, count=1, flags=re.DOTALL)

    # 4) window._OFERTAS con datos completos (plazo/km reales)
    blob = 'window._OFERTAS = ' + json.dumps(data, ensure_ascii=False) + ';'
    c = re.sub(r'window\._OFERTAS\s*=\s*\{.*?\};', blob, c, count=1, flags=re.DOTALL)

    # 5) CSS + JS render — reinyectar SIEMPRE (reemplaza la version previa
    #    para que cambios de plantilla lleguen a las fichas ya generadas)
    if 'FICHA v4' in c:
        c = re.sub(r'/\* ===== FICHA v4 ===== \*/.*?(?=\n?\s*</style>)',
                   lambda _: NEW_CSS.strip(), c, count=1, flags=re.DOTALL)
    else:
        c = c.replace('</style>', NEW_CSS + '\n  </style>', 1)
    if 'window.renderComparador' in c:
        c = re.sub(r'<script>(?:(?!</script>).)*?window\.renderComparador(?:(?!</script>).)*?</script>',
                   lambda _: JS_RENDER.strip(), c, count=1, flags=re.DOTALL)
    else:
        c = c.replace('</body>', JS_RENDER + '\n</body>', 1)

    return c, None


def _apply(path, offers):
    """Transforma y escribe con guardarrailes. Devuelve 'ok'|'skip'."""
    new, reason = transform(path, offers)
    if new is None:
        return 'skip'
    if any(mk not in new for mk in MARKERS):
        print(f'  SKIP {path.stem}: faltarian marcadores'); return 'skip'
    m = re.search(r'window\._OFERTAS\s*=\s*(\{.*?\});', new, re.DOTALL)
    if not m or not isinstance(json.loads(m.group(1)), dict):
        print(f'  SKIP {path.stem}: _OFERTAS no valida'); return 'skip'
    if len(new) < len(path.read_text(encoding='utf-8')) * 0.5:
        print(f'  SKIP {path.stem}: salida pequena'); return 'skip'
    shutil.copy2(path, str(path) + '.bak')
    path.write_text(new, encoding='utf-8')
    return 'ok'


def offers_from_page(content):
    """Extrae ofertas del propio window._OFERTAS de una ficha (formato interno)."""
    m = re.search(r'window\._OFERTAS\s*=\s*(\{.*?\});', content, re.DOTALL)
    if not m:
        return []
    try:
        pdata = json.loads(m.group(1))
    except Exception:
        return []
    ALLOWED = {'arval', 'ayvens', 'alphabet', 'm automoción', 'm automocion'}
    offers = []
    for fuente, lst in pdata.items():
        if fuente.lower() not in ALLOWED:      # Kinto/Quadis/KIA fuera del comparador
            continue
        for o in lst:
            try:
                price = float(str(o.get('price', '0')).replace(',', '.'))
            except Exception:
                continue
            if price <= 0:
                continue
            offers.append(dict(fuente=o.get('gestora', fuente), tipo=o.get('tipo', ''),
                               fuel=o.get('fuel', ''), duracion=o.get('plazo', ''),
                               km=o.get('km', ''), version=o.get('version', ''),
                               precio_desde=price))
    return offers


def main():
    idx = IDX.read_text(encoding='utf-8')
    allo = json.loads(re.search(r'const _OFERTAS\s*=\s*(\[.*?\]);', idx, re.DOTALL).group(1))
    by_model = defaultdict(list)
    for o in allo:
        by_model[(o['make'], o['model'])].append(o)

    only = [a.lower() for a in sys.argv[1:]]
    fixed = skip = err = 0
    done = set()

    # ── Pase 1: datos frescos del scrape (index.html) ──
    for (make, model), offers in by_model.items():
        slug = slugify(make + ' ' + model)
        if only and slug not in only:
            continue
        path = BASE / f'renting-{slug}.html'
        if not path.exists():
            continue
        try:
            r = _apply(path, offers)
            if r == 'ok': fixed += 1; done.add(path.name)
            else: skip += 1
        except Exception as e:
            err += 1
            if err <= 8: print(f'  ERR {slug}: {e}')

    # ── Pase 2: fichas restantes con el diseño nuevo usando SUS propios datos ──
    for path in sorted(BASE.glob('renting-*-*.html')):
        if path.name in done:
            continue
        if only and path.stem.replace('renting-', '') not in only:
            continue
        try:
            content = path.read_text(encoding='utf-8')
        except Exception:
            continue
        if 'compare-grid' not in content or 'window._OFERTAS' not in content or 'car-header' not in content:
            continue
        if 'FICHA v4' in content:
            continue
        offers = offers_from_page(content)
        if not offers:
            continue
        try:
            r = _apply(path, offers)
            if r == 'ok': fixed += 1
            else: skip += 1
        except Exception as e:
            err += 1
            if err <= 8: print(f'  ERR {path.stem}: {e}')

    print(f'Fichas actualizadas: {fixed} | Saltadas: {skip} | Errores: {err}')


if __name__ == '__main__':
    main()
