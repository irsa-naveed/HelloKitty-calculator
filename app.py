"""
🎀 Kawaii Pink Scientific Calculator (Streamlit)

    pip install -r requirements.txt
    streamlit run app.py

The calculator runs fully in the browser (HTML/JS inside a Streamlit component),
so typing and button presses are instant and never trigger a Streamlit rerun.
"""

import base64
import io
import mimetypes
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

BASE = Path(__file__).parent
ASSETS = BASE / "assets"
BG_DIR = ASSETS / "background"
BG_EXTS = ("jpg", "jpeg", "png", "webp", "gif")

st.set_page_config(
    page_title="Irsa's Calculator",
    page_icon="🎀",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ----------------------------------------------------------------- helpers
def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def shrink_image(raw: bytes, mime: str) -> str:
    """Resize big pictures (max 1920px wide) so the page stays fast."""
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(raw))
        if getattr(img, "is_animated", False):
            raise ValueError("animated")
        img.thumbnail((1920, 1920))
        buf = io.BytesIO()
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
            img.save(buf, format="PNG", optimize=True)
            mime = "image/png"
        else:
            img.convert("RGB").save(buf, format="JPEG", quality=84, optimize=True)
            mime = "image/jpeg"
        raw = buf.getvalue()
    except Exception:
        pass
    return f"data:{mime};base64," + base64.b64encode(raw).decode()


def find_background(uploaded):
    if uploaded is not None:
        return shrink_image(uploaded.getvalue(), uploaded.type or "image/jpeg")
    if BG_DIR.exists():
        for ext in BG_EXTS:
            for p in sorted(BG_DIR.glob(f"*.{ext}")):
                return shrink_image(p.read_bytes(), mimetypes.guess_type(p.name)[0] or "image/jpeg")
    return None


ICONS = {
    "__ICON_BUBBLE_BABY__": data_uri(ASSETS / "icons" / "bubble_baby.svg"),
    "__ICON_BUBBLE_HOT__": data_uri(ASSETS / "icons" / "bubble_hot.svg"),
    "__ICON_HEART__": data_uri(ASSETS / "icons" / "heart.svg"),
    "__ICON_STAR__": data_uri(ASSETS / "icons" / "star.svg"),
    "__ICON_SPARKLE__": data_uri(ASSETS / "icons" / "sparkle.svg"),
    "__ICON_BOW__": data_uri(ASSETS / "icons" / "bow.svg"),
    "__MASCOT__": data_uri(ASSETS / "mascot.jpg"),
}

# ----------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown("### 🎀 Background")
    uploaded = st.file_uploader(
        "Upload your own background picture",
        type=list(BG_EXTS),
        help="Use an image you have the rights to. You can also drop background.jpg into assets/background/",
    )
    veil = st.slider("Pink veil", 0, 80, 20, help="How much pink tint covers your picture")
    st.caption("Tip: landscape pictures around 1920×1080 look best.")

bg_uri = find_background(uploaded)

# ----------------------------------------------------------------- page CSS
PAGE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&display=swap');
html, body, [class*="st-"], .stApp {font-family: 'Fredoka', 'Comic Sans MS', cursive;}
#MainMenu, footer {visibility: hidden;}
[data-testid="stHeader"] {background: transparent;}
[data-testid="stToolbar"] {display: none;}
__BACKGROUND__
.block-container {padding-top: 0.6rem; padding-bottom: 0; max-width: 900px; position: relative; z-index: 2;}
[data-testid="stSidebar"] {background: #fff0f6; border-right: 4px solid #ff8fb7;}
[data-testid="stSidebar"] * {color: #8a2a56;}
iframe {border: none !important; background: transparent !important;}
</style>
"""

if bg_uri:
    alpha = veil / 100
    background_css = (
        ".stApp {background: linear-gradient(rgba(255,217,232,%s), rgba(255,160,205,%s)), "
        "url('%s') center / cover no-repeat fixed;}" % (alpha, alpha, bg_uri)
    )
else:
    mascot = ICONS["__MASCOT__"]
    background_css = (
        ".stApp {background-color: #ffd9e8;"
        "background-image: radial-gradient(#ffffff 18%, transparent 20%), radial-gradient(#ffffff 18%, transparent 20%),"
        "linear-gradient(160deg, #ffe9f2 0%, #ffc3dc 100%);"
        "background-size: 46px 46px, 46px 46px, 100% 100%;"
        "background-position: 0 0, 23px 23px, 0 0;}"
        ".stApp::before, .stApp::after {content: ''; position: fixed; top: 50%; width: min(23vw, 430px); aspect-ratio: 580 / 497;"
        "background: url('__MASCOT_URI__') center / cover no-repeat; border: 7px solid #fff; border-radius: 32px;"
        "box-shadow: 0 0 0 5px #ff7ab8, 0 20px 34px rgba(216,27,124,.38); pointer-events: none; z-index: 1;}"
        ".stApp::before {left: 1.5vw; transform: translateY(-50%) rotate(-4deg);}"
        ".stApp::after {right: 1.5vw; transform: translateY(-50%) rotate(4deg);}"
        "@media (max-width: 1200px) {.stApp::before, .stApp::after {display: none;}}"
    ).replace("__MASCOT_URI__", mascot)

st.markdown(PAGE_CSS.replace("__BACKGROUND__", background_css), unsafe_allow_html=True)

# ----------------------------------------------------------------- calculator
CALCULATOR_HTML = r'''
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root{
    --baby:#ffd9e8; --baby2:#ffeef5; --baby3:#fff7fb;
    --hot:#ff3d95; --hot-d:#c2186a; --hot-l:#ff7ab8; --rose:#d81b7c; --ink:#7a2150; --soft:#ffb3d4;
  }
  *{box-sizing:border-box; -webkit-tap-highlight-color:transparent;}
  html,body{margin:0; background:transparent; font-family:'Fredoka','Comic Sans MS',cursive; color:var(--ink);}
  body{padding:0 8px 20px; overflow-x:hidden;}

  /* floating bubbles */
  #bubbles{position:fixed; inset:0; pointer-events:none; overflow:hidden; z-index:0;}
  #bubbles img{position:absolute; bottom:-90px; opacity:0; animation:rise linear infinite; will-change:transform,opacity;}
  @keyframes rise{
    0%{transform:translate(0,0) rotate(0deg) scale(.8); opacity:0}
    10%{opacity:.85}
    50%{transform:translate(18px,-55vh) rotate(12deg) scale(1)}
    100%{transform:translate(-14px,-118vh) rotate(-10deg) scale(1.08); opacity:0}
  }
  @media (prefers-reduced-motion:reduce){#bubbles img{animation:none; opacity:.5; bottom:auto}}

  
.wrap{position:relative; z-index:1; max-width:780px; margin:0 auto; padding-top:46px;}

.bow{position:absolute; top:0; left:50%; width:118px; transform:translateX(-50%) rotate(-3deg); z-index:4;
     filter:drop-shadow(0 4px 0 rgba(194,24,106,.3)); animation:wiggle 3.6s ease-in-out infinite;}

@keyframes wiggle{0%,100%{transform:translateX(-50%) rotate(-4deg)}50%{transform:translateX(-50%) rotate(4deg)}}

.mascot{position:absolute; left:4px; top:-8px; width:108px; z-index:4; transform:rotate(-8deg);
        filter:drop-shadow(0 5px 0 rgba(194,24,106,.25)); animation:bob 4s ease-in-out infinite;}

.mascot{top:8px; left:10px; width:92px; height:auto; border:4px solid #fff; border-radius:20px; box-shadow:0 0 0 3px var(--hot-l), 0 8px 14px rgba(216,27,124,.35);}

@keyframes bob{0%,100%{transform:rotate(-8deg) translateY(0)}50%{transform:rotate(-4deg) translateY(-6px)}}


  .calc{
    position:relative; border-radius:46px; padding:52px 22px 22px;
    background:linear-gradient(160deg,rgba(255,255,255,.96) 0%, rgba(255,238,245,.96) 55%, rgba(255,217,232,.96) 100%);
    border:6px solid var(--hot-l);
    box-shadow:0 0 0 6px #fff, 0 0 0 11px var(--baby), 0 24px 44px rgba(216,27,124,.35);
  }
  .calc::before{content:""; position:absolute; inset:0; border-radius:38px; pointer-events:none; opacity:.6;
    background-image:radial-gradient(var(--baby) 22%, transparent 24%); background-size:26px 26px;}
  .title{position:relative; display:flex; align-items:center; justify-content:center; gap:10px; font-weight:700; font-size:22px;
         color:var(--rose); margin:-32px 0 14px; text-shadow:0 2px 0 #fff;}
  .title img{width:24px; height:24px;}
  .sound{position:absolute; right:6px; top:-34px; z-index:3; font-size:17px; width:38px; height:38px; border-radius:50%; cursor:pointer;
         border:3px solid var(--hot-l); background:#fff; box-shadow:0 3px 0 var(--hot-d);}
  .sound.on{background:var(--baby);}

  /* screen */
  .screen{position:relative; background:var(--baby3); border:5px solid var(--hot); border-radius:28px; padding:10px 18px 12px;
    box-shadow:inset 0 6px 14px rgba(255,61,149,.22), 0 5px 0 var(--hot-d); min-height:152px;
    display:flex; flex-direction:column; justify-content:space-between; overflow:hidden;}
  .screen .deco{position:absolute; width:20px; height:20px; opacity:.8; pointer-events:none;}
  .chips{display:flex; gap:8px; height:24px; align-items:center;}
  .chip{font-size:12px; font-weight:600; padding:1px 10px; border-radius:999px; background:var(--baby); color:var(--rose); border:2px solid var(--hot-l);}
  .chip.off{display:none;}
  #expr{width:100%; border:0; outline:0; background:transparent; text-align:right; font-family:inherit; font-size:25px; font-weight:500;
        color:#a0457a; caret-color:var(--hot); padding:4px 0; min-height:38px;}
  #expr::placeholder{color:#e8a9c8; font-weight:400;}
  .res{font-size:52px; font-weight:700; text-align:right; line-height:1.1; min-height:58px; color:var(--rose);
       white-space:nowrap; overflow-x:auto; scrollbar-width:none;}
  .res::-webkit-scrollbar{display:none;}
  .res.mid{font-size:38px;} .res.small{font-size:27px;}
  .res.preview{color:#e08ab6; font-weight:500;}
  .res.err{color:var(--hot-d); font-size:28px;}

  /* keys */
  .panels{position:relative; display:grid; grid-template-columns:5fr 4fr; gap:16px; margin-top:18px;}
  .grid{display:grid; gap:10px; grid-auto-rows:1fr;}
  .sci{grid-template-columns:repeat(5,1fr);}
  .pad{grid-template-columns:repeat(4,1fr);}
  button.k{font-family:inherit; font-weight:600; font-size:18px; min-height:46px; border-radius:18px; cursor:pointer;
    border:3px solid; transition:transform .06s, box-shadow .06s, filter .15s; user-select:none; padding:0;}
  button.k:hover{filter:brightness(1.05);}
  button.k:active, button.k.flash{transform:translateY(4px) scale(.97);}
  button.num{background:linear-gradient(#fff,#fff0f6); border-color:var(--hot-l); color:var(--ink); box-shadow:0 5px 0 var(--hot-d); font-size:23px; min-height:54px;}
  button.num:active,button.num.flash{box-shadow:0 1px 0 var(--hot-d);}
  button.op{background:linear-gradient(#ff8cc3,var(--hot)); border-color:var(--hot-d); color:#fff; box-shadow:0 5px 0 #96104f; font-size:25px; min-height:54px; text-shadow:0 2px 0 rgba(130,10,70,.4);}
  button.op:active,button.op.flash{box-shadow:0 1px 0 #96104f;}
  button.fn{background:linear-gradient(#fff6fa,var(--baby)); border-color:var(--soft); color:var(--rose); box-shadow:0 4px 0 #f08db8; font-size:15px; min-height:44px;}
  button.fn:active,button.fn.flash{box-shadow:0 0 0 #f08db8;}
  button.mem{background:linear-gradient(#ffe0ee,var(--soft)); border-color:var(--hot-l); color:var(--hot-d); box-shadow:0 4px 0 #e36aa3; font-size:14px; min-height:44px;}
  button.mem:active,button.mem.flash{box-shadow:0 0 0 #e36aa3;}
  button.clr{background:linear-gradient(#ff6fb0,#e0207a); border-color:var(--hot-d); color:#fff; box-shadow:0 5px 0 #96104f; font-size:20px; min-height:54px;}
  button.clr:active,button.clr.flash{box-shadow:0 1px 0 #96104f;}
  button.eq{background:linear-gradient(#ff4fa0,#d4106f); border-color:#96104f; color:#fff; box-shadow:0 5px 0 #6e0838; font-size:32px; min-height:54px; text-shadow:0 2px 0 rgba(0,0,0,.25);}
  button.eq:active,button.eq.flash{box-shadow:0 1px 0 #6e0838;}

  /* history */
  .hist-toggle{position:relative; display:flex; align-items:center; gap:8px; margin:20px auto 0; font-family:inherit; font-weight:600; font-size:15px;
     background:#fff; color:var(--rose); border:3px solid var(--hot-l); border-radius:999px; padding:6px 20px; cursor:pointer; box-shadow:0 4px 0 var(--hot-d);}
  .hist-toggle img{width:18px; height:18px;}
  .hist{position:relative; display:none; margin-top:14px; background:var(--baby3); border:4px dashed var(--hot-l); border-radius:22px; padding:10px 14px; max-height:200px; overflow:auto;}
  .hist.open{display:block;}
  .hist .empty{text-align:center; color:#e08ab6; padding:10px;}
  .hist .row{display:flex; justify-content:space-between; gap:12px; padding:6px 8px; border-radius:12px; cursor:pointer;}
  .hist .row:hover{background:var(--baby);}
  .hist .e{color:#a0457a; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;}
  .hist .r{font-weight:700; color:var(--rose); white-space:nowrap;}
  .hist .clear{display:block; margin:8px auto 0; font-family:inherit; border:2px solid var(--hot); background:#fff; color:var(--hot-d); border-radius:999px; padding:3px 14px; cursor:pointer; font-weight:600;}
  .hint{position:relative; text-align:center; font-size:12px; color:#b0558a; margin-top:14px; line-height:1.5;}

  @media (max-width:640px){
    .panels{grid-template-columns:1fr;}
    .res{font-size:40px;}
    .mascot{width:76px; top:2px;}
  }
</style>
</head>
<body>
<div id="bubbles"></div>

<div class="wrap">
  <img class="mascot" src="__MASCOT__" alt="">
  <img class="bow" src="__ICON_BOW__" alt="">

  <div class="calc">
    <button class="sound" id="soundBtn" type="button" title="Bubble pop sound">🔔</button>
    <div class="title"><img src="__ICON_HEART__" alt=""> Irsa's Pretty Calculator <img src="__ICON_HEART__" alt=""></div>

    <div class="screen">
      <img class="deco" style="left:10px; bottom:8px" src="__ICON_BUBBLE_BABY__" alt="">
      <img class="deco" style="left:34px; bottom:18px; width:13px; height:13px" src="__ICON_BUBBLE_HOT__" alt="">
      <img class="deco" style="right:12px; top:8px; width:16px; height:16px" src="__ICON_SPARKLE__" alt="">
      <div class="chips"><span class="chip" id="chipMode">DEG</span><span class="chip off" id="chipMem">M</span></div>
      <input id="expr" type="text" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" inputmode="none"
             placeholder="type or tap ✿" aria-label="Expression">
      <div class="res" id="res">0</div>
    </div>

    <div class="panels">
      <div class="grid sci" id="sci"></div>
      <div class="grid pad" id="pad"></div>
    </div>

    <button class="hist-toggle" id="histBtn" type="button"><img src="__ICON_STAR__" alt="">History</button>
    <div class="hist" id="hist"></div>
    <div class="hint">Just type: <b>sin(30)+2^3</b> &nbsp; <b>sqrt(16)</b> &nbsp; <b>5!</b> &nbsp; <b>pi*2</b> &nbsp; <b>nCr(5,2)</b><br>
      Enter = &nbsp;•&nbsp; Esc clear &nbsp;•&nbsp; ↑ ↓ history &nbsp;•&nbsp; an operator after a result continues from Ans</div>
  </div>
</div>

<script>
/* ======================= helpers ======================= */
const $ = id => document.getElementById(id);
const store = {
  get(k, d){ try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch(e){ return d; } },
  set(k, v){ try { localStorage.setItem(k, JSON.stringify(v)); } catch(e){} }
};
const state = {
  ans: 0, mem: store.get('kc_mem', 0), hasMem: store.get('kc_hasmem', false),
  deg: store.get('kc_deg', true), done: false, err: null,
  history: store.get('kc_hist', []), hidx: -1, sound: store.get('kc_sound', false)
};

/* ======================= floating bubbles ======================= */
(function(){
  const icons = ['__ICON_BUBBLE_BABY__','__ICON_BUBBLE_HOT__','__ICON_BUBBLE_BABY__','__ICON_HEART__','__ICON_BUBBLE_HOT__','__ICON_SPARKLE__','__ICON_STAR__','__ICON_BUBBLE_BABY__'];
  const host = $('bubbles');
  for (let i = 0; i < 20; i++){
    const im = document.createElement('img');
    im.src = icons[i % icons.length]; im.alt = '';
    const size = 16 + Math.random() * 46;
    im.style.cssText = 'width:' + size + 'px;height:' + size + 'px;left:' + (Math.random() * 96) + '%;animation-duration:' + (10 + Math.random() * 12) + 's;animation-delay:-' + (Math.random() * 20) + 's';
    host.appendChild(im);
  }
})();

/* ======================= math ======================= */
const G_COEF = [0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313,
  -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7];
function gamma(z){
  if (z < 0.5) return Math.PI / (Math.sin(Math.PI * z) * gamma(1 - z));
  z -= 1; let x = G_COEF[0];
  for (let i = 1; i < 9; i++) x += G_COEF[i] / (z + i);
  const t = z + 7.5;
  return Math.sqrt(2 * Math.PI) * Math.pow(t, z + 0.5) * Math.exp(-t) * x;
}
function fact(n){
  if (Number.isInteger(n)){
    if (n < 0) return NaN;
    if (n > 170) return Infinity;
    let r = 1; for (let i = 2; i <= n; i++) r *= i; return r;
  }
  return gamma(n + 1);
}
function ncr(n, k){
  if (!Number.isInteger(n) || !Number.isInteger(k) || n < 0 || k < 0 || k > n) return NaN;
  k = Math.min(k, n - k); let r = 1;
  for (let i = 1; i <= k; i++) r = r * (n - k + i) / i;
  return Math.round(r);
}
function npr(n, k){
  if (!Number.isInteger(n) || !Number.isInteger(k) || n < 0 || k < 0 || k > n) return NaN;
  let r = 1; for (let i = 0; i < k; i++) r *= (n - i); return r;
}
const toRad = x => state.deg ? x * Math.PI / 180 : x;
const toDeg = x => state.deg ? x * 180 / Math.PI : x;
const clean = x => Math.abs(x) < 1e-14 ? 0 : x;

const FUNCS = {
  sin: x => clean(Math.sin(toRad(x))),
  cos: x => clean(Math.cos(toRad(x))),
  tan: x => (state.deg && Math.abs((x - 90) % 180) < 1e-12) ? NaN : clean(Math.tan(toRad(x))),
  asin: x => toDeg(Math.asin(x)), acos: x => toDeg(Math.acos(x)), atan: x => toDeg(Math.atan(x)),
  sinh: x => Math.sinh(x), cosh: x => Math.cosh(x), tanh: x => Math.tanh(x),
  ln: x => Math.log(x), log: x => Math.log10(x), log2: x => Math.log2(x),
  sqrt: x => Math.sqrt(x), cbrt: x => Math.cbrt(x), abs: x => Math.abs(x), exp: x => Math.exp(x),
  fact: fact,
  ncr: ncr, npr: npr,
  mod: (a, b) => b === 0 ? NaN : ((a % b) + b) % b,
  root: (x, n) => (n % 2 !== 0 && x < 0) ? -Math.pow(-x, 1 / n) : Math.pow(x, 1 / n)
};
const ARITY = {ncr: 2, npr: 2, mod: 2, root: 2};

function evaluate(src){
  let s = src.replace(/×/g, '*').replace(/÷/g, '/').replace(/−/g, '-')
             .replace(/π/g, 'pi').replace(/√/g, 'sqrt').replace(/∛/g, 'cbrt');
  const open = (s.match(/\(/g) || []).length, close = (s.match(/\)/g) || []).length;
  if (open > close) s += ')'.repeat(open - close);

  const toks = []; let i = 0, m;
  while (i < s.length){
    const rest = s.slice(i);
    if (/^\s/.test(rest)) { i++; continue; }
    if ((m = /^(\d+\.?\d*|\.\d+)(e[+-]?\d+)?/i.exec(rest))) { toks.push({t: 'num', v: parseFloat(m[0])}); i += m[0].length; continue; }
    if ((m = /^[a-z][a-z0-9]*/i.exec(rest))) { toks.push({t: 'id', v: m[0].toLowerCase()}); i += m[0].length; continue; }
    if ('+-*/^%!(),'.indexOf(rest[0]) >= 0) { toks.push({t: 'op', v: rest[0]}); i++; continue; }
    throw new Error('Syntax Error');
  }
  if (!toks.length) throw new Error('Syntax Error');

  let p = 0;
  const peek = () => toks[p];
  const isOp = v => peek() && peek().t === 'op' && peek().v === v;
  const startsPrimary = () => { const k = peek(); return k && (k.t === 'num' || k.t === 'id' || (k.t === 'op' && k.v === '(')); };

  function parseExpr(){
    let v = parseTerm();
    while (isOp('+') || isOp('-')){ const o = toks[p++].v; const r = parseTerm(); v = (o === '+') ? v + r : v - r; }
    return v;
  }
  function parseTerm(){
    let v = parseUnary();
    for (;;){
      if (isOp('*')) { p++; v *= parseUnary(); }
      else if (isOp('/')) { p++; v /= parseUnary(); }
      else if (startsPrimary()) { v *= parseUnary(); }
      else break;
    }
    return v;
  }
  function parseUnary(){
    if (isOp('-')) { p++; return -parseUnary(); }
    if (isOp('+')) { p++; return parseUnary(); }
    return parsePower();
  }
  function parsePower(){
    const b = parsePostfix();
    if (isOp('^')) { p++; return Math.pow(b, parseUnary()); }
    return b;
  }
  function parsePostfix(){
    let v = parsePrimary();
    while (isOp('!') || isOp('%')){
      const o = toks[p++].v;
      v = (o === '!') ? fact(v) : v / 100;
    }
    return v;
  }
  function parseArgs(){
    const args = [];
    if (!isOp('(')) throw new Error('Syntax Error');
    p++;
    if (isOp(')')) { p++; return args; }
    args.push(parseExpr());
    while (isOp(',')) { p++; args.push(parseExpr()); }
    if (!isOp(')')) throw new Error('Syntax Error');
    p++;
    return args;
  }
  function parsePrimary(){
    const k = toks[p++];
    if (!k) throw new Error('Syntax Error');
    if (k.t === 'num') return k.v;
    if (k.t === 'op' && k.v === '('){
      const v = parseExpr();
      if (!isOp(')')) throw new Error('Syntax Error');
      p++; return v;
    }
    if (k.t === 'id'){
      if (k.v === 'pi') return Math.PI;
      if (k.v === 'e') return Math.E;
      if (k.v === 'ans') return state.ans;
      if (k.v === 'rand'){ if (isOp('(')) parseArgs(); return Math.random(); }
      if (FUNCS[k.v]){
        const args = parseArgs();
        if (args.length !== (ARITY[k.v] || 1)) throw new Error('Syntax Error');
        return FUNCS[k.v].apply(null, args);
      }
    }
    throw new Error('Syntax Error');
  }

  const v = parseExpr();
  if (p < toks.length) throw new Error('Syntax Error');
  if (Number.isNaN(v)) throw new Error('Math Error');
  if (!Number.isFinite(v)) throw new Error('Cannot divide by 0');
  return v;
}

function fmt(v){
  const n = parseFloat(v.toPrecision(12));
  const a = Math.abs(n);
  if (a !== 0 && (a >= 1e12 || a < 1e-9)) return n.toExponential(8).replace(/\.?0+e/, 'e');
  return String(n);
}

/* ======================= actions ======================= */
const OPS = '+-*/^%!';
const SYMBOLS = {'*': '×', '/': '÷', '-': '−'};
const TOK_END = /(a?(sin|cos|tan)h?\(|ln\(|log2?\(|√\(|cbrt\(|abs\(|rand\(\)|nCr\(|nPr\(|mod\(|root\(|Ans)$/;

function caretEnd(el){ el.setSelectionRange(el.value.length, el.value.length); }

function insert(txt, kind){
  const el = $('expr');
  el.focus({preventScroll: true});
  if (state.done){
    el.value = (kind === 'op' && !state.err) ? 'Ans' : '';
    state.done = false; state.err = null; caretEnd(el);
  }
  el.setRangeText(txt, el.selectionStart, el.selectionEnd, 'end');
  state.hidx = -1;
  update();
}
function equals(){
  const el = $('expr'), src = el.value.trim();
  if (!src || state.done) return;
  try {
    const v = evaluate(src);
    state.history.unshift({e: src, r: fmt(v)});
    if (state.history.length > 40) state.history.pop();
    store.set('kc_hist', state.history);
    state.ans = v; state.err = null;
  } catch (e) { state.err = e.message || 'Error'; }
  state.done = true; state.hidx = -1;
  update();
}
function clearAll(){
  const el = $('expr'); el.value = ''; state.done = false; state.err = null; state.hidx = -1;
  el.focus({preventScroll: true}); update();
}
function backspace(){
  const el = $('expr'); el.focus({preventScroll: true});
  state.done = false; state.err = null;
  const s = el.selectionStart, e = el.selectionEnd;
  if (s !== e) el.setRangeText('', s, e, 'end');
  else if (s > 0){
    const m = TOK_END.exec(el.value.slice(0, s));
    el.setRangeText('', s - (m ? m[0].length : 1), s, 'end');
  }
  update();
}
function toggleMode(){ state.deg = !state.deg; store.set('kc_deg', state.deg); update(); }
function currentValue(){
  if (state.done && !state.err) return state.ans;
  const src = $('expr').value.trim();
  return src ? evaluate(src) : 0;
}
function memory(op){
  try {
    if (op === 'c'){ state.mem = 0; state.hasMem = false; }
    else if (op === 'r'){ if (state.hasMem) insert(fmt(state.mem), 'digit'); return; }
    else {
      const v = currentValue();
      state.mem = (op === 'p') ? state.mem + v : state.mem - v;
      state.hasMem = true;
    }
    store.set('kc_mem', state.mem); store.set('kc_hasmem', state.hasMem);
  } catch (e) { state.err = e.message; state.done = true; }
  update();
}
function inverse(){
  const el = $('expr');
  el.focus({preventScroll: true});
  if (state.done){ el.value = state.err ? '' : 'Ans'; state.done = false; state.err = null; }
  el.value = el.value ? '1÷(' + el.value + ')' : '1÷(';
  caretEnd(el); update();
}
function recall(d){
  if (!state.history.length) return;
  state.hidx = Math.min(state.history.length - 1, Math.max(-1, state.hidx + d));
  const el = $('expr');
  el.value = state.hidx < 0 ? '' : state.history[state.hidx].e;
  state.done = false; state.err = null; caretEnd(el); update();
}

/* ======================= sound ======================= */
let audio = null;
function pop(){
  if (!state.sound) return;
  try {
    audio = audio || new (window.AudioContext || window.webkitAudioContext)();
    const o = audio.createOscillator(), g = audio.createGain();
    o.type = 'sine'; o.frequency.setValueAtTime(520, audio.currentTime);
    o.frequency.exponentialRampToValueAtTime(980, audio.currentTime + 0.07);
    g.gain.setValueAtTime(0.06, audio.currentTime);
    g.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + 0.09);
    o.connect(g); g.connect(audio.destination); o.start(); o.stop(audio.currentTime + 0.1);
  } catch (e) {}
}

/* ======================= keypad ======================= */
const ins = (t, k) => () => insert(t, k);
const SCI = [
  [['mode','DEG','mem',toggleMode], ['mc','MC','mem',()=>memory('c')], ['mr','MR','mem',()=>memory('r')], ['mp','M+','mem',()=>memory('p')], ['mm','M−','mem',()=>memory('m')]],
  [['sin','sin','fn',ins('sin(','f')], ['cos','cos','fn',ins('cos(','f')], ['tan','tan','fn',ins('tan(','f')], ['pi','π','fn',ins('π','f')], ['e','e','fn',ins('e','f')]],
  [['asin','sin⁻¹','fn',ins('asin(','f')], ['acos','cos⁻¹','fn',ins('acos(','f')], ['atan','tan⁻¹','fn',ins('atan(','f')], ['sq','x²','fn',ins('^2','op')], ['cube','x³','fn',ins('^3','op')]],
  [['sinh','sinh','fn',ins('sinh(','f')], ['cosh','cosh','fn',ins('cosh(','f')], ['tanh','tanh','fn',ins('tanh(','f')], ['pow','xʸ','fn',ins('^','op')], ['sqrt','√x','fn',ins('√(','f')]],
  [['ln','ln','fn',ins('ln(','f')], ['log','log','fn',ins('log(','f')], ['tenx','10ˣ','fn',ins('10^(','f')], ['ex','eˣ','fn',ins('e^(','f')], ['cbrt','∛x','fn',ins('cbrt(','f')]],
  [['fact','n!','fn',ins('!','op')], ['inv','1/x','fn',inverse], ['abs','|x|','fn',ins('abs(','f')], ['ncr','nCr','fn',ins('nCr(','f')], ['npr','nPr','fn',ins('nPr(','f')]],
  [['mod','mod','fn',ins('mod(','f')], ['comma',',','fn',ins(',','op')], ['rand','Rand','fn',ins('rand()','f')], ['log2','log₂','fn',ins('log2(','f')], ['root','ʸ√x','fn',ins('root(','f')]]
];
const PAD = [
  [['ac','AC','clr',clearAll], ['bs','⌫','clr',backspace], ['lp','(','op',ins('(','f')], ['rp',')','op',ins(')','op')]],
  [['d7','7','num',ins('7','d')], ['d8','8','num',ins('8','d')], ['d9','9','num',ins('9','d')], ['div','÷','op',ins('÷','op')]],
  [['d4','4','num',ins('4','d')], ['d5','5','num',ins('5','d')], ['d6','6','num',ins('6','d')], ['mul','×','op',ins('×','op')]],
  [['d1','1','num',ins('1','d')], ['d2','2','num',ins('2','d')], ['d3','3','num',ins('3','d')], ['sub','−','op',ins('−','op')]],
  [['d0','0','num',ins('0','d')], ['dot','.','num',ins('.','d')], ['pct','%','op',ins('%','op')], ['add','+','op',ins('+','op')]],
  [['ans','Ans','fn',ins('Ans','f')], ['exp','EXP','fn',ins('×10^(','op')], ['eq','=','eq',equals,2]]
];
function build(host, rows){
  rows.forEach(row => row.forEach(spec => {
    const b = document.createElement('button');
    b.className = 'k ' + spec[2]; b.textContent = spec[1]; b.dataset.id = spec[0]; b.type = 'button';
    if (spec[4]) b.style.gridColumn = 'span ' + spec[4];
    b.addEventListener('mousedown', e => e.preventDefault());   /* keep typing focus in the display */
    b.addEventListener('click', () => { pop(); spec[3](); });
    host.appendChild(b);
  }));
}
build($('sci'), SCI); build($('pad'), PAD);

/* ======================= render ======================= */
function update(){
  const el = $('expr'), res = $('res'), src = el.value;
  let text = '', cls = 'res';
  if (state.done){
    if (state.err){ text = state.err; cls += ' err'; } else text = fmt(state.ans);
  } else if (src.trim()){
    try { text = fmt(evaluate(src)); cls += ' preview'; } catch (e) { text = ''; }
  } else text = '0';
  if (!state.err){ if (text.length > 18) cls += ' small'; else if (text.length > 11) cls += ' mid'; }
  res.className = cls; res.textContent = text || ' ';
  res.scrollLeft = res.scrollWidth;
  const label = state.deg ? 'DEG' : 'RAD';
  $('chipMode').textContent = label;
  document.querySelector('[data-id="mode"]').textContent = label;
  $('chipMem').classList.toggle('off', !state.hasMem);
  $('soundBtn').classList.toggle('on', state.sound);
  $('soundBtn').textContent = state.sound ? '🔔' : '🔕';
  renderHistory();
}
let histKey = '';
function renderHistory(){
  const key = JSON.stringify(state.history);
  if (key === histKey) return; histKey = key;
  const h = $('hist'); h.innerHTML = '';
  if (!state.history.length){ h.innerHTML = '<div class="empty">No calculations yet ♡</div>'; return; }
  state.history.forEach(item => {
    const row = document.createElement('div'); row.className = 'row';
    const e = document.createElement('span'); e.className = 'e'; e.textContent = item.e + ' =';
    const r = document.createElement('span'); r.className = 'r'; r.textContent = item.r;
    row.append(e, r);
    row.addEventListener('click', () => { const el = $('expr'); el.value = item.e; state.done = false; state.err = null; caretEnd(el); el.focus({preventScroll: true}); update(); });
    h.appendChild(row);
  });
  const c = document.createElement('button'); c.className = 'clear'; c.type = 'button'; c.textContent = 'Clear history';
  c.addEventListener('click', () => { state.history = []; store.set('kc_hist', []); update(); });
  h.appendChild(c);
}
$('histBtn').addEventListener('click', () => $('hist').classList.toggle('open'));
$('soundBtn').addEventListener('click', () => { state.sound = !state.sound; store.set('kc_sound', state.sound); update(); pop(); });

/* ======================= keyboard ======================= */
const KEYFLASH = {'+':'add', '-':'sub', '*':'mul', '/':'div', '.':'dot', '(':'lp', ')':'rp', '%':'pct', '!':'fact', '^':'pow', ',':'comma',
                  'Backspace':'bs', 'Enter':'eq', '=':'eq', 'Escape':'ac'};
function flash(key){
  const id = /^[0-9]$/.test(key) ? 'd' + key : KEYFLASH[key];
  if (!id) return;
  const b = document.querySelector('[data-id="' + id + '"]');
  if (!b) return;
  b.classList.add('flash'); setTimeout(() => b.classList.remove('flash'), 110);
}
const expr = $('expr');
expr.addEventListener('input', () => {   /* typed * / - become × ÷ − */
  const pos = expr.selectionStart;
  const v = expr.value.replace(/[*\/-]/g, c => SYMBOLS[c]);
  if (v !== expr.value){ expr.value = v; expr.setSelectionRange(pos, pos); }
  state.done = false; state.err = null; state.hidx = -1; update();
});

function onKey(ev){
  if (ev.ctrlKey || ev.metaKey || ev.altKey || ev.isComposing) return;
  const k = ev.key, t = ev.target;
  if (t === expr){
    if (k === 'Enter'){ ev.preventDefault(); flash(k); pop(); equals(); return; }
    if (k === 'Escape'){ ev.preventDefault(); flash(k); clearAll(); return; }
    if (k === 'ArrowUp' || k === 'ArrowDown'){ ev.preventDefault(); recall(k === 'ArrowUp' ? 1 : -1); return; }
    if (state.done){
      if (k.length === 1){ expr.value = (OPS.indexOf(k) >= 0 && !state.err) ? 'Ans' : ''; state.done = false; state.err = null; caretEnd(expr); }
      else if (k === 'Backspace' || k === 'Delete'){ state.done = false; state.err = null; update(); }
    }
    if (k.length === 1 || k === 'Backspace') flash(k);
    return;
  }
  /* focus is elsewhere (page body, or the Streamlit page around the calculator) */
  if (t && t.closest && t.closest('input,textarea,select,button,summary,a,[contenteditable="true"],[role="button"],[role="slider"],[role="combobox"]')) return;
  let handled = true;
  if (k === 'Enter' || k === '='){ flash(k); pop(); equals(); }
  else if (k === 'Escape'){ flash(k); clearAll(); }
  else if (k === 'Backspace'){ flash(k); backspace(); }
  else if (k === 'ArrowUp' || k === 'ArrowDown'){ recall(k === 'ArrowUp' ? 1 : -1); }
  else if (k.length === 1 && /[0-9a-zA-Z.+\-*\/^()%!,]/.test(k)){
    flash(k); pop();
    insert(SYMBOLS[k] || k, OPS.indexOf(k) >= 0 ? 'op' : 'd');
  } else handled = false;
  if (handled){ ev.preventDefault(); ev.stopPropagation(); ev.stopImmediatePropagation(); }
}
window.addEventListener('keydown', onKey, true);
try {   /* also catch keys pressed on the Streamlit page itself (and stop its r / c shortcuts) */
  const P = window.parent;
  if (P.__kawaiiKey) P.document.removeEventListener('keydown', P.__kawaiiKey, true);
  P.__kawaiiKey = onKey;
  P.document.addEventListener('keydown', onKey, true);
} catch (err) {}

update();
try { expr.focus({preventScroll: true}); } catch (e) {}
</script>
</body>
</html>
'''

html = CALCULATOR_HTML
for token, uri in ICONS.items():
    html = html.replace(token, uri)

components.html(html, height=1010, scrolling=False)
