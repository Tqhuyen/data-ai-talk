"""Build the Data & AI talk deck (Swiss Modern style) from content/<lang>.json.

Usage:  python build.py            -> writes deck-vi.html and deck-en.html
Edit content/*.json (answers, speaker info), then rerun. An empty "answer": []
renders the question with a "answered live" placeholder.
"""
from __future__ import annotations

import html
import json
import pathlib

ROOT = pathlib.Path(__file__).parent
BASE_CSS = (ROOT / "viewport-base.css").read_text(encoding="utf-8")
FONTS = "family=Archivo:wght@500;700;800&family=Nunito:ital,wght@0,400;0,600;0,700;1,400&family=JetBrains+Mono:wght@500"

e = html.escape  # plain-text fields; *_html / "text" fields are trusted markup from content files


# =============================================================================
# THEME + LAYOUT CSS (authored at the fixed 1920x1080 stage size)
# =============================================================================
CSS = r"""
/* === THEME: Swiss Modern — white, ink, one red accent === */
:root{
  --stage-bg:#e9e9e6; --slide-bg:#fff;
  --ink:#0d0d0d; --red:#ff3300; --grey:#8c8c8c; --soft:#f3f2ef; --rule:#d9d9d6;
  --display:'Archivo',sans-serif; --body:'Nunito',sans-serif; --mono:'JetBrains Mono',monospace;
  --pad:160px; --ease:cubic-bezier(.16,1,.3,1);
}
.slide{font-family:var(--body);color:var(--ink)}
.slide em{font-style:normal;color:var(--red)}
.grid{position:absolute;inset:0;background-image:linear-gradient(90deg,rgba(0,0,0,.05) 1px,transparent 1px);background-size:160px 100%;pointer-events:none}
.redbar{position:absolute;left:0;top:0;width:24px;height:100%;background:var(--red);transform:scaleY(0);transform-origin:top;transition:transform 1s var(--ease)}
.visible .redbar{transform:scaleY(1)}
.d{font-family:var(--display)}

/* === CHROME: section label + page number on every slide === */
.chrome{position:absolute;left:var(--pad);right:var(--pad);top:64px;display:flex;justify-content:space-between;font:700 20px var(--display);letter-spacing:.14em;text-transform:uppercase;color:var(--grey)}
.chrome .sec{color:var(--ink)}
.chrome .pg b{color:var(--red)}

/* === REVEAL ANIMATIONS (staggered via --i) === */
.r{opacity:0;transform:translateY(36px);transition:opacity .7s var(--ease),transform .7s var(--ease);transition-delay:calc(var(--i,0) * 90ms + 80ms)}
.visible .r{opacity:1;transform:none}

/* === SHARED TEXT PIECES === */
.tag{font:800 28px var(--display);color:var(--red);letter-spacing:.04em}
.label{font:700 20px var(--display);letter-spacing:.14em;text-transform:uppercase;color:var(--grey)}
.h-q{font:800 60px/1.1 var(--display);letter-spacing:-.02em}
.h-xl{font:800 88px/1.02 var(--display);letter-spacing:-.03em}
.quote{font:italic 400 27px/1.45 var(--body);color:#555;border-left:4px solid var(--red);padding-left:24px}
.quote+.quote{margin-top:14px}
.statb{display:inline-flex;align-items:center;gap:14px;font:700 24px var(--display);background:var(--ink);color:#fff;padding:14px 22px;align-self:flex-start}
.statb::before{content:"";width:14px;height:14px;background:var(--red)}
.lesson{position:absolute;left:var(--pad);right:var(--pad);bottom:84px;background:var(--ink);color:#fff;padding:28px 36px;font:600 32px/1.35 var(--body);display:flex;gap:28px;align-items:baseline}
.lesson b{font:800 22px var(--display);letter-spacing:.14em;text-transform:uppercase;color:var(--red);white-space:nowrap}

/* === COVER === */
.cover .kick{position:absolute;left:var(--pad);top:150px;font:700 24px var(--display);letter-spacing:.12em;text-transform:uppercase}
.cover .kick span{color:var(--red)}
.cover h1{position:absolute;left:var(--pad);top:260px;width:1300px;font:800 150px/1.04 var(--display);letter-spacing:-.035em}
.cover .sub{position:absolute;left:var(--pad);top:640px;width:980px;font-size:36px;line-height:1.4;color:#333}
.foot{position:absolute;left:var(--pad);right:var(--pad);bottom:96px;display:flex;justify-content:space-between;align-items:flex-end;border-top:3px solid var(--ink);padding-top:28px;font:700 30px var(--display)}
.foot .label{display:block;margin-bottom:8px}
.circle{position:absolute;border-radius:50%;background:var(--red)}
.sq{position:absolute;border:6px solid var(--ink)}

/* === SPEAKER === */
.speaker .name{position:absolute;left:var(--pad);top:200px;font:800 120px/1 var(--display);letter-spacing:-.035em}
.speaker .role{position:absolute;left:var(--pad);top:350px;font:700 40px var(--display);color:var(--red)}
.facts{position:absolute;left:var(--pad);right:var(--pad);top:470px;display:grid;grid-template-columns:repeat(4,1fr);gap:40px}
.fact{border-top:3px solid var(--ink);padding-top:22px}
.fact .l{font:700 20px var(--display);letter-spacing:.14em;text-transform:uppercase;color:var(--grey)}
.fact .k{margin-top:12px;font:800 40px/1.1 var(--display);letter-spacing:-.02em}
.fact .k+.k{margin-top:8px}
.fact .v{margin-top:10px;font-size:27px;line-height:1.35;color:#444}
.pubs{position:absolute;left:var(--pad);right:var(--pad);bottom:84px;background:var(--soft);padding:26px 34px}
.pubs ul{list-style:none;margin-top:12px;display:flex;flex-direction:column;gap:10px}
.pubs li{display:grid;grid-template-columns:1fr auto;gap:32px;align-items:baseline;border-top:2px solid var(--rule);padding-top:10px}
.pubs .t{font:600 26px/1.35 var(--body)}
.pubs .v{font:700 20px var(--display);color:var(--grey);text-align:right;max-width:430px}

/* === AGENDA === */
.agenda h2{position:absolute;left:var(--pad);top:170px}
.ag{position:absolute;left:var(--pad);right:var(--pad);top:360px;display:grid;grid-template-columns:1fr 1fr;column-gap:96px;row-gap:44px}
.ag-i{border-top:3px solid var(--ink);padding-top:22px;display:grid;grid-template-columns:110px 1fr;row-gap:8px}
.ag-i .n{grid-row:span 2;font:800 52px/1 var(--display);color:var(--red)}
.ag-i .t{font:800 46px/1.05 var(--display);letter-spacing:-.02em}
.ag-i .dd{font-size:27px;color:#555}

/* === SECTION DIVIDER === */
.section .num{position:absolute;left:140px;top:110px;font:800 440px/1 var(--display);color:var(--red);letter-spacing:-.06em}
.section h2{position:absolute;left:var(--pad);top:600px;width:1300px;font:800 120px/1.02 var(--display);letter-spacing:-.035em}
.section .sub{position:absolute;left:var(--pad);bottom:110px;width:980px;font-size:34px;line-height:1.4;color:#444}
.qchips{position:absolute;right:var(--pad);bottom:110px;display:flex;gap:12px;flex-wrap:wrap;justify-content:flex-end;width:520px}
.qchips span{font:800 26px var(--display);border:3px solid var(--ink);padding:10px 18px}

/* === PIPELINE === */
.pipeline h2{position:absolute;left:var(--pad);top:170px}
.pipe{position:absolute;left:var(--pad);right:var(--pad);top:400px;display:grid;grid-template-columns:repeat(6,1fr);gap:24px}
.ps{border-top:6px solid var(--ink);padding-top:26px;position:relative}
.ps .n{font:800 120px/1 var(--display);color:var(--red);letter-spacing:-.04em}
.ps .t{margin-top:18px;font:800 36px/1.1 var(--display)}
.ps .dd{margin-top:14px;font-size:24px;line-height:1.4;color:#555}
.pipe .ps:not(:last-child) .n::after{content:"→";font:800 36px var(--display);color:var(--grey);margin-left:14px;vertical-align:middle}
.tools{position:absolute;left:var(--pad);right:var(--pad);bottom:110px;border-top:3px solid var(--ink);padding-top:26px;font:700 30px var(--display)}
.tools .label{margin-right:24px}

/* === CASE-STUDY STEP === */
.step .bign{position:absolute;left:120px;top:110px;font:800 560px/1 var(--display);color:var(--red);letter-spacing:-.06em}
.step .col{position:absolute;left:720px;right:var(--pad);top:170px;display:flex;flex-direction:column;gap:28px}
.step .lead{font-size:36px;line-height:1.35;color:#333}
.pts{list-style:none;display:flex;flex-direction:column;gap:18px}
.pts li{font-size:30px;line-height:1.4;padding-left:40px;position:relative}
.pts li::before{content:"";position:absolute;left:0;top:16px;width:16px;height:16px;background:var(--red)}
.code{font:500 26px/1.5 var(--mono);background:var(--soft);border-left:6px solid var(--ink);padding:20px 28px;white-space:pre}
.callout{font-size:28px;line-height:1.4;border:3px solid var(--red);padding:20px 26px}

/* === BIG STAT === */
.stat .big{position:absolute;left:130px;top:150px;font:800 400px/1 var(--display);color:var(--red);letter-spacing:-.06em}
.stat .cap{position:absolute;left:var(--pad);top:590px;width:860px;font:800 46px/1.15 var(--display);letter-spacing:-.02em}
.stat .det{position:absolute;left:1120px;right:var(--pad);top:240px;display:flex;flex-direction:column}
.det-i{display:grid;grid-template-columns:120px 1fr;align-items:baseline;border-top:2px solid var(--rule);padding:20px 0}
.det-i .k{font:800 56px/1 var(--display)}
.det-i .v{font-size:28px;line-height:1.35}
.stat .ins{position:absolute;left:var(--pad);right:var(--pad);bottom:84px;background:var(--ink);color:#fff;padding:28px 36px;font:700 34px var(--display)}

/* === BAR CHART === */
.bars h2{position:absolute;left:var(--pad);top:150px}
.bars .kick{position:absolute;left:var(--pad);top:120px}
.chart{position:absolute;left:var(--pad);right:var(--pad);top:280px;bottom:80px;display:flex;flex-direction:column;justify-content:space-evenly}
.row{display:grid;grid-template-columns:600px 1fr 170px;align-items:center;gap:28px}
.row .lb{font-size:26px;line-height:1.15;text-align:right}
.track{height:28px;background:var(--soft)}
.fill{height:100%;width:0;background:var(--ink);transition:width 1.1s var(--ease);transition-delay:calc(var(--i,0) * 60ms + 200ms)}
.row.top .fill{background:var(--red)}
.row.top .lb{font-weight:700}
.visible .fill{width:var(--w)}
.row .vl{font:800 28px var(--display)}
.row .vl small{font:500 22px var(--display);color:var(--grey);margin-left:8px}

/* === INSIGHT → ACTION MAP === */
.map h2{position:absolute;left:var(--pad);top:170px}
.map .kick{position:absolute;left:var(--pad);top:130px}
.mrows{position:absolute;left:var(--pad);right:var(--pad);top:380px}
.mr{display:grid;grid-template-columns:1fr 90px 640px;align-items:center;border-top:3px solid var(--ink);padding:30px 0}
.mr .in{font-size:36px;line-height:1.3}
.mr .ar{font:800 48px var(--display);color:var(--red)}
.mr .ac{font:800 38px/1.15 var(--display)}

/* === LESSONS / CLOSING (numbered columns) === */
.lessons h2,.closing h2{position:absolute;left:var(--pad);top:170px}
.cols{position:absolute;left:var(--pad);right:var(--pad);top:420px;display:grid;gap:56px}
.cols.c3{grid-template-columns:repeat(3,1fr)}
.cols.c2{grid-template-columns:repeat(2,1fr);row-gap:44px;top:360px}
.ci{border-top:6px solid var(--ink);padding-top:28px}
.ci .n{font:800 88px/1 var(--display);color:var(--red)}
.ci .t{margin-top:16px;font:800 42px/1.12 var(--display);letter-spacing:-.02em}
.ci .dd{margin-top:16px;font-size:29px;line-height:1.4;color:#444}
.cols.c2 .ci{display:grid;grid-template-columns:96px 1fr;column-gap:20px;padding-top:22px}
.cols.c2 .ci .n{font-size:56px;grid-row:span 2}
.cols.c2 .ci .t{margin-top:0;font-size:38px}
.thanks{position:absolute;left:var(--pad);right:var(--pad);bottom:84px;display:flex;justify-content:space-between;align-items:baseline;border-top:3px solid var(--ink);padding-top:24px}
.thanks .tt{font:800 64px var(--display);color:var(--red);letter-spacing:-.02em}
.thanks .sp{font:700 30px var(--display)}

/* === Q&A SLIDE: question left, answer right === */
.qa .lcol{position:absolute;left:var(--pad);top:170px;width:820px;bottom:110px;display:flex;flex-direction:column;gap:30px}
.qa .rcol{position:absolute;left:1080px;right:var(--pad);top:170px;bottom:110px;display:flex;flex-direction:column}
.ans{list-style:none;display:flex;flex-direction:column}
.ans li{display:grid;grid-template-columns:80px 1fr;border-top:3px solid var(--ink);padding:26px 0 30px}
.ans li .n{font:800 30px var(--display);color:var(--red);padding-top:4px}
.ans li .tx{font:600 34px/1.38 var(--body)}
.pending{flex:1;border:3px dashed var(--ink);display:flex;flex-direction:column;justify-content:center;padding:56px;gap:22px}
.pending .ar{font:800 72px/1 var(--display);color:var(--red)}
.pending .tx{font:800 44px/1.15 var(--display);letter-spacing:-.02em}
.see{margin-top:auto;font:700 24px var(--display);color:var(--grey)}
.see a{color:var(--ink);text-decoration:none;border-bottom:3px solid var(--red)}

/* === STATEMENT === */
.statement .kick{position:absolute;left:var(--pad);top:190px;display:flex;gap:22px;align-items:baseline;font:700 34px var(--body);color:#444;width:1500px}
.statement .txt{position:absolute;left:var(--pad);top:330px;width:1380px;font:800 118px/1.06 var(--display);letter-spacing:-.035em}
.statement .sub{position:absolute;left:var(--pad);bottom:110px;width:1200px;font-size:36px;line-height:1.4;color:#444;border-top:3px solid var(--ink);padding-top:26px}

/* === LADDER (stairs / roadmap) === */
.ladder .top{position:absolute;left:var(--pad);right:var(--pad);top:160px;display:flex;flex-direction:column;gap:22px}
.ladder .top .quote{width:1200px}
.stairs{position:absolute;left:var(--pad);top:500px;width:1000px;height:480px;display:flex;align-items:flex-end;gap:20px}
.stair{flex:1;background:var(--ink);color:#fff;padding:26px;display:flex;flex-direction:column;justify-content:flex-start;gap:12px;transform-origin:bottom;transform:scaleY(0);transition:transform .9s var(--ease);transition-delay:calc(var(--i,0) * 140ms + 250ms)}
.visible .stair{transform:none}
.stair:last-child{background:var(--red)}
.stair .k{font:800 22px var(--display);letter-spacing:.12em;opacity:.7}
.stair .t{font:800 38px/1.08 var(--display)}
.stair .dd{font-size:23px;line-height:1.3;opacity:.92}
.hire{position:absolute;left:1240px;right:var(--pad);top:520px;bottom:130px;border-top:6px solid var(--red);padding-top:26px;display:flex;flex-direction:column;gap:18px}
.hire .chip{font:800 34px var(--display);border-bottom:2px solid var(--rule);padding-bottom:16px}
.hire .note{margin-top:auto;font-size:26px;line-height:1.4;color:#555}
.ladder .lead{font-size:34px;line-height:1.4;color:#333;width:1500px}
.road{position:absolute;left:var(--pad);right:var(--pad);top:640px;display:grid;grid-template-columns:repeat(4,1fr);gap:56px}
.rd{border-top:6px solid var(--ink);padding-top:24px;position:relative}
.rd:last-child{border-color:var(--red)}
.rd .k{font:800 26px var(--display);color:var(--red)}
.rd .t{margin-top:12px;font:800 48px/1.05 var(--display);letter-spacing:-.02em}
.rd:not(:last-child) .k::after{content:"  →";color:var(--grey)}

/* === LINKS === */
.links .lcol{position:absolute;left:var(--pad);top:170px;width:620px;display:flex;flex-direction:column;gap:30px}
.links .lcol .intro{font-size:32px;line-height:1.4;color:#333}
.lk{position:absolute;left:880px;right:var(--pad);top:170px;display:flex;flex-direction:column}
.lk a{display:grid;grid-template-columns:1fr auto;row-gap:6px;border-top:3px solid var(--ink);padding:24px 0;text-decoration:none;color:var(--ink)}
.lk a:last-child{border-bottom:3px solid var(--ink)}
.lk .nm{font:800 40px var(--display);letter-spacing:-.01em}
.lk .ar{grid-row:span 2;align-self:center;font:800 44px var(--display);color:var(--red)}
.lk .u{font:500 22px var(--mono);color:var(--grey)}
.lk .dd{grid-column:1;font-size:26px;color:#444}

/* === TIPS (2x2 cards) === */
.qrow{display:flex;justify-content:space-between;align-items:center}
.qrow .statb{align-self:auto}
.tips .top{position:absolute;left:var(--pad);right:var(--pad);top:160px;display:flex;flex-direction:column;gap:20px}
.tips .top .quote{width:1300px}
.tgrid{position:absolute;left:var(--pad);right:var(--pad);top:470px;bottom:90px;display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:28px}
.tc{background:var(--soft);padding:30px 36px;border-top:6px solid var(--ink);display:flex;flex-direction:column;gap:12px}
.tc:first-child{border-color:var(--red)}
.tc .t{font:800 38px var(--display);letter-spacing:-.01em}
.tc .dd{font-size:28px;line-height:1.4;color:#333}

/* === TIMELINE === */
.timeline .top{position:absolute;left:var(--pad);right:var(--pad);top:160px;display:flex;flex-direction:column;gap:22px}
.timeline .top .quote{width:1300px}
.timeline .lead{position:absolute;left:var(--pad);top:540px;width:1500px;font-size:32px;line-height:1.4;color:#333}
.tl{position:absolute;left:var(--pad);right:var(--pad);top:700px;display:grid;grid-template-columns:repeat(4,1fr)}
.tl::before{content:"";position:absolute;left:0;right:0;top:15px;height:4px;background:var(--ink)}
.tli{position:relative;padding-top:56px}
.tli::before{content:"";position:absolute;left:0;top:0;width:34px;height:34px;border-radius:50%;background:var(--ink)}
.tli:last-child::before{background:var(--red)}
.tli .w{font:700 26px var(--display);color:var(--grey)}
.tli .t{margin-top:10px;font:800 50px/1.05 var(--display);letter-spacing:-.02em}
.tli:last-child .t{color:var(--red)}

/* === LOOP === */
.loop .lcol{position:absolute;left:var(--pad);top:170px;width:760px;display:flex;flex-direction:column;gap:28px}
.loopv{position:absolute;left:1000px;top:200px;width:760px;height:560px}
.loopv svg{width:760px;height:560px;max-width:none;max-height:none}
.loop .txt{font-size:32px;line-height:1.45;color:#333}
.aside{position:absolute;left:var(--pad);right:var(--pad);bottom:84px;background:var(--ink);color:#fff;padding:26px 36px;display:flex;gap:32px;align-items:baseline}
.aside .q{font:italic 400 28px var(--body);color:#bbb}
.aside .a{font:800 34px var(--display)}

/* === Q&A INDEX === */
.index h2{position:absolute;left:var(--pad);top:160px}
.ix{position:absolute;left:var(--pad);right:var(--pad);top:310px;display:grid;grid-template-columns:1fr 1fr;column-gap:80px}
.ixg .label{color:var(--ink);border-bottom:6px solid var(--ink);padding-bottom:14px;margin-bottom:6px}
.ixi{display:grid;grid-template-columns:118px 1fr 90px;align-items:baseline;gap:16px;border-bottom:2px solid var(--rule);padding:17px 0;text-decoration:none;color:var(--ink)}
.ixi .n{font:800 28px var(--display);color:var(--red)}
.ixi .t{font-size:27px;line-height:1.3}
.ixi .p{font:700 22px var(--display);color:var(--grey);text-align:right}


/* === CAREER ROLES OVERVIEW (5 columns, data flows left → right) === */
.roles .kick{position:absolute;left:var(--pad);top:130px}
.roles h2{position:absolute;left:var(--pad);top:170px}
.rl{position:absolute;left:var(--pad);right:var(--pad);top:400px;display:grid;grid-template-columns:repeat(5,1fr);gap:28px}
.rli{border-top:6px solid var(--ink);padding-top:24px;display:flex;flex-direction:column;gap:16px;min-height:330px}
.rli .tools-l{margin-top:auto;border-top:2px solid var(--rule);padding-top:16px}
.rli:last-child{border-color:var(--red)}
.rli .n{font:800 30px/36px var(--display);height:36px;color:var(--red)}
.rl .rli:not(:last-child) .n::after{content:"→";color:var(--grey);margin-left:12px}
.rli .t{font:800 40px/1.05 var(--display);letter-spacing:-.02em}
.rli .q{font:600 28px/1.35 var(--body)}
.rli .tools-l{font:700 22px var(--display);color:var(--grey);letter-spacing:.02em}
.more{position:absolute;left:var(--pad);right:var(--pad);bottom:110px;border-top:3px solid var(--ink);padding-top:26px;font-size:30px;color:#444}

/* === CAREER ROLE DETAIL: path | work, then 2 use cases === */
.role .hd{position:absolute;left:var(--pad);right:var(--pad);top:130px;display:flex;flex-direction:column;gap:14px}
.role .hd .h-xl{font-size:96px}
.role .hd .tg{font-size:34px;line-height:1.35;color:#333}
.role .rn{position:absolute;right:var(--pad);top:120px;font:800 200px/1 var(--display);color:var(--red);letter-spacing:-.05em}
.role .c1{position:absolute;left:var(--pad);width:760px;top:430px}
.role .c2{position:absolute;left:1000px;right:var(--pad);top:430px}
.path{list-style:none;counter-reset:p}
.path li{counter-increment:p;display:grid;grid-template-columns:64px 1fr;border-top:2px solid var(--rule);padding:13px 0;font:600 28px/1.3 var(--body)}
.path li::before{content:counter(p,decimal-leading-zero);font:800 24px var(--display);color:var(--red);padding-top:3px}
.path li:last-child{border-bottom:2px solid var(--rule)}
.role .pts li{font-size:28px}
.role .label{margin-bottom:14px}
.cases{position:absolute;left:var(--pad);right:var(--pad);top:770px;bottom:84px;display:grid;grid-template-columns:1fr 1fr;gap:28px}
.case{background:var(--soft);border-top:6px solid var(--ink);padding:22px 30px;display:flex;flex-direction:column;gap:10px}
.case:first-child{border-color:var(--red)}
.case .t{font:800 32px var(--display);letter-spacing:-.01em}
.case .t small{font:700 18px var(--display);letter-spacing:.14em;text-transform:uppercase;color:var(--grey);display:block;margin-bottom:6px}
.case .dd{font-size:25px;line-height:1.4;color:#333}


/* === VENN: AI ⊃ ML ⊃ DL, overlapping Data Science (redrawn from reference diagram) === */
.venn .kick{position:absolute;left:var(--pad);top:130px}
.venn h2{position:absolute;left:var(--pad);top:170px;width:1600px;font-size:64px}
.vd{position:absolute;left:120px;top:300px;width:880px;height:660px}
.vd svg{width:880px;height:660px;max-width:none;max-height:none}
.defs{position:absolute;left:1060px;right:var(--pad);top:290px;display:flex;flex-direction:column}
.df{border-top:3px solid var(--ink);padding:12px 0 14px;display:grid;grid-template-columns:28px 1fr;column-gap:16px}
.df i{width:22px;height:22px;margin-top:8px;display:block}
.df .t{font:800 32px var(--display);letter-spacing:-.01em}
.df .dd{grid-column:2;font-size:24px;line-height:1.38;color:#333;margin-top:4px}
.venn .vnote{position:absolute;left:1060px;right:var(--pad);bottom:84px;background:var(--ink);color:#fff;padding:22px 28px;font:600 25px/1.4 var(--body)}


/* === Q&A FIGURE (image evidence above the answer box) === */
.fig{display:flex;flex-direction:column;gap:14px;margin-bottom:22px}
.fig img{width:100%;height:auto;border:3px solid var(--ink);display:block;max-height:none}
.fig figcaption{font:600 24px/1.4 var(--body)}
.fig figcaption small{display:block;margin-top:6px;font:500 18px/1.35 var(--display);color:var(--grey)}
.fig ~ .pending{padding:28px 36px;flex-direction:row;align-items:center;gap:24px}
.fig ~ .pending .ar{font-size:48px}.fig ~ .pending .tx{font-size:34px}

/* === PRESENTATION UI (outside the stage) === */
.progress{position:fixed;left:0;bottom:0;height:5px;background:var(--red);z-index:1000;transition:width .4s var(--ease)}
.edit-hotzone{position:fixed;top:0;left:0;width:80px;height:80px;z-index:10000;cursor:pointer}
.edit-toggle{position:fixed;top:16px;left:16px;z-index:10001;font:700 14px var(--display);letter-spacing:.1em;text-transform:uppercase;background:var(--ink);color:#fff;border:0;padding:10px 14px;cursor:pointer;opacity:0;pointer-events:none;transition:opacity .3s}
.edit-toggle.show,.edit-toggle.active{opacity:1;pointer-events:auto}
.edit-toggle.active{background:var(--red)}
body.editing [data-edit]{outline:2px dashed rgba(255,51,0,.5);outline-offset:4px}
"""


# =============================================================================
# SLIDE RENDERERS — one function per slide type in content/*.json
# =============================================================================
def r(i: int) -> str:
    """Reveal attributes with stagger index."""
    return f'class="r" style="--i:{i}"'


def quotes(qs: list[str]) -> str:
    return "".join(f'<p class="quote" data-edit>“{e(q)}”</p>' for q in qs)


def qtag(m, q: str) -> str:
    return f'<div class="tag">{e(m["see_q"])} {e(q)}</div>'


def render_cover(s, m, ctx):
    return f"""<div class="redbar"></div>
<div class="kick r" style="--i:0" data-edit>{e(s['kicker'])}</div>
<div class="circle r" style="--i:2;right:160px;top:220px;width:340px;height:340px"></div>
<div class="sq r" style="--i:3;right:330px;top:400px;width:170px;height:170px"></div>
<h1 class="r" style="--i:1" data-edit>{s['title_html']}</h1>
<p class="sub r" style="--i:2" data-edit>{e(s['sub'])}</p>
<div class="foot r" style="--i:4"><div><span class="label">{e(s['speaker_label'])}</span><span data-edit>{e(s['speaker'])}</span></div>
<div style="text-align:right"><span class="label">{e(s['meta_label'])}</span><span data-edit>{e(s['meta'])}</span></div></div>"""


def render_speaker(s, m, ctx):
    def fact(i, f):
        ks = f["k"] if isinstance(f["k"], list) else [f["k"]]  # a list = several equal-weight headlines
        head = "".join(f'<div class="k" data-edit>{e(k)}</div>' for k in ks)
        sub = f'<div class="v" data-edit>{e(f["v"])}</div>' if f.get("v") else ""
        return f'<div class="fact r" style="--i:{i+2}"><div class="l">{e(f["l"])}</div>{head}{sub}</div>'
    facts = "".join(fact(i, f) for i, f in enumerate(s["facts"]))
    pubs = "".join(f'<li><span class="t" data-edit>{e(x["t"])}</span><span class="v" data-edit>{e(x["v"])}</span></li>' for x in s["pubs"])
    return f"""<div class="label r" style="--i:0;position:absolute;left:160px;top:150px">{e(s['kicker'])}</div>
<div class="circle r" style="--i:3;right:160px;top:150px;width:200px;height:200px"></div>
<div class="name r" style="--i:1" data-edit>{e(s['name'])}</div>
<div class="role r" style="--i:2" data-edit>{e(s['role'])}</div>
<div class="facts">{facts}</div>
<div class="pubs r" style="--i:7"><div class="label">{e(s['pubs_label'])}</div><ul>{pubs}</ul></div>"""


def render_agenda(s, m, ctx):
    items = "".join(f'<div class="ag-i r" style="--i:{i+1}"><div class="n">{e(it["n"])}</div><div class="t" data-edit>{e(it["t"])}</div><div class="dd" data-edit>{e(it["d"])}</div></div>' for i, it in enumerate(s["items"]))
    return f'<h2 class="h-xl r" style="--i:0" data-edit>{e(s["title"])}</h2><div class="ag">{items}</div>'


def render_section(s, m, ctx):
    chips = ""
    if s.get("qs"):
        chips = '<div class="qchips r" style="--i:3">' + "".join(f'<span>{e(m["see_q"])} {e(q)}</span>' for q in s["qs"]) + "</div>"
    return f"""<div class="redbar"></div>
<div class="num r" style="--i:0">{e(s['n'])}</div>
<h2 class="r" style="--i:1" data-edit>{s['title']}</h2>
<p class="sub r" style="--i:2" data-edit>{e(s['sub'])}</p>{chips}"""


def render_pipeline(s, m, ctx):
    steps = "".join(f'<div class="ps r" style="--i:{i+1}"><div class="n">{e(p["n"])}</div><div class="t" data-edit>{e(p["t"])}</div><div class="dd" data-edit>{e(p["d"])}</div></div>' for i, p in enumerate(s["steps"]))
    tools = " <em>→</em> ".join(e(t) for t in s["tools"].split(" → "))
    return f"""<h2 class="h-xl r" style="--i:0" data-edit>{e(s['title'])}</h2>
<div class="pipe">{steps}</div><div class="tools r" style="--i:8">{tools}</div>"""


def render_step(s, m, ctx):
    pts = "".join(f"<li data-edit>{e(p)}</li>" for p in s["points"])
    extra = ""
    if s.get("code"):
        extra += f'<div class="code r" style="--i:4">{e(s["code"])}</div>'
    if s.get("callout"):
        extra += f'<div class="callout r" style="--i:4" data-edit>{e(s["callout"])}</div>'
    return f"""<div class="bign r" style="--i:0">{e(s['n'])}</div>
<div class="col"><h2 class="h-xl r" style="--i:1" data-edit>{e(s['title'])}</h2>
<p class="lead r" style="--i:2" data-edit>{e(s['lead'])}</p>
<ul class="pts r" style="--i:3">{pts}</ul>{extra}</div>
<div class="lesson r" style="--i:6"><b>{e(m['lesson'])}</b><span data-edit>{e(s['lesson'])}</span></div>"""


def render_stat(s, m, ctx):
    det = "".join(f'<div class="det-i r" style="--i:{i+2}"><div class="k">{e(d["k"])}</div><div class="v" data-edit>{e(d["v"])}</div></div>' for i, d in enumerate(s["detail"]))
    return f"""<div class="label r" style="--i:0;position:absolute;left:160px;top:130px">{e(s['kicker'])}</div>
<div class="big r" style="--i:0">{e(s['big'])}</div>
<p class="cap r" style="--i:1" data-edit>{e(s['caption'])}</p>
<div class="det">{det}</div>
<div class="ins r" style="--i:7" data-edit>{e(s['insight'])}</div>"""


def render_bars(s, m, ctx):
    mx = max(i["count"] for i in s["items"])
    rows = []
    for i, it in enumerate(s["items"]):
        pct = round(it["count"] / s["total"] * 100)
        top = " top" if i < 3 else ""
        rows.append(f'<div class="row{top} r" style="--i:{i+1}"><div class="lb" data-edit>{e(it["label"])}</div>'
                    f'<div class="track"><div class="fill" style="--w:{it["count"]/mx*100:.1f}%;--i:{i}"></div></div>'
                    f'<div class="vl">{it["count"]}<small>· {pct}%</small></div></div>')
    return f"""<div class="kick label r" style="--i:0">{e(s['kicker'])}</div>
<h2 class="h-q r" style="--i:0;font-size:72px" data-edit>{e(s['title'])}</h2>
<div class="chart">{''.join(rows)}</div>"""


def render_map(s, m, ctx):
    rows = "".join(f'<div class="mr r" style="--i:{i+1}"><div class="in" data-edit>{e(x["insight"])}</div><div class="ar">→</div><div class="ac" data-edit>{e(x["action"])}</div></div>' for i, x in enumerate(s["rows"]))
    return f"""<div class="kick label r" style="--i:0">{e(s['kicker'])}</div>
<h2 class="h-xl r" style="--i:0" data-edit>{e(s['title'])}</h2><div class="mrows">{rows}</div>"""


def render_lessons(s, m, ctx):
    cols = "".join(f'<div class="ci r" style="--i:{i+1}"><div class="n">{i+1}</div><div class="t" data-edit>{e(x["t"])}</div><div class="dd" data-edit>{e(x["d"])}</div></div>' for i, x in enumerate(s["items"]))
    return f'<h2 class="h-xl r" style="--i:0" data-edit>{e(s["title"])}</h2><div class="cols c3">{cols}</div>'


def render_qa(s, m, ctx):
    stat = f'<div class="statb r" style="--i:3" data-edit>{e(s["stat"])}</div>' if s.get("stat") else ""
    if s["answer"]:
        lis = "".join(f'<li class="r" style="--i:{i+2}"><span class="n">{i+1:02d}</span><span class="tx" data-edit>{e(a)}</span></li>' for i, a in enumerate(s["answer"]))
        right = f'<div class="label r" style="--i:1;margin-bottom:18px">{e(m["answer"])}</div><ul class="ans">{lis}</ul>'
    else:
        right = f'<div class="pending r" style="--i:2"><div class="ar">→</div><div class="tx" data-edit>{e(m["pending"])}</div></div>'
    if s.get("figure"):
        fg = s["figure"]
        right = (f'<figure class="fig r" style="--i:1"><img src="{e(fg["src"])}" alt="{e(fg["alt"])}">'
                 f'<figcaption><span data-edit>{e(fg["caption"])}</span><small data-edit>{e(fg["source"])}</small></figcaption></figure>') + right
    if s.get("see"):
        right += f'<div class="see r" style="--i:6">→ <a href="#{ctx["qpage"][s["see"]]}">{e(m["see_q"])} {e(s["see"])} · {e(m["page"])} {ctx["qpage"][s["see"]]}</a></div>'
    return f"""<div class="lcol">{qtag(m, s['q'])}<h2 class="h-q r" style="--i:0" data-edit>{e(s['question'])}</h2>
<div class="r" style="--i:1"><div class="label" style="margin-bottom:16px">{e(m['students_asked'])}</div>{quotes(s['quotes'])}</div>{stat}</div>
<div class="rcol">{right}</div>"""


def render_statement(s, m, ctx):
    tag = f'<span class="tag">{e(m["see_q"])} {e(s["q"])}</span>' if s.get("q") else ""
    return f"""<div class="kick r" style="--i:0">{tag}<span data-edit>{e(s['kicker'])}</span></div>
<div class="circle r" style="--i:2;right:160px;top:170px;width:160px;height:160px"></div>
<div class="txt r" style="--i:1" data-edit>{s['text']}</div>
<p class="sub r" style="--i:3" data-edit>{e(s['sub'])}</p>"""


def render_ladder(s, m, ctx):
    head = f"""<div class="top">{qtag(m, s['q'])}<h2 class="h-q r" style="--i:0" data-edit>{e(s['question'])}</h2>
<div class="r" style="--i:1">{quotes(s['quotes'])}</div>"""
    if s.get("horizontal"):
        head += f'<p class="lead r" style="--i:2" data-edit>{e(s["lead"])}</p></div>'
        rd = "".join(f'<div class="rd r" style="--i:{i+3}"><div class="k">{i+1:02d}</div><div class="t" data-edit>{e(x["t"])}</div></div>' for i, x in enumerate(s["steps"]))
        return head + f'<div class="road">{rd}</div>'
    n = len(s["steps"])
    st = "".join(f'<div class="stair" style="--i:{i};height:{55 + 45*i/max(n-1,1):.0f}%"><div class="k">{i+1:02d}</div><div class="t" data-edit>{e(x["t"])}</div><div class="dd" data-edit>{e(x["d"])}</div></div>' for i, x in enumerate(s["steps"]))
    chips = "".join(f'<div class="chip" data-edit>{e(c)}</div>' for c in s["footer"])
    return head + f"""</div><div class="stairs">{st}</div>
<div class="hire r" style="--i:4"><div class="label">{e(s['footer_label'])}</div>{chips}<p class="note" data-edit>{e(s['footer_note'])}</p></div>"""


def render_links(s, m, ctx):
    lk = "".join(f'<a href="{e(x["url"])}" target="_blank" rel="noopener" class="r" style="--i:{i+1}"><span class="nm">{e(x["name"])}</span><span class="ar">↗</span><span class="u">{e(x["url"].split("//",1)[1].rstrip("/"))}</span><span class="dd">{e(x["d"])}</span></a>' for i, x in enumerate(s["links"]))
    return f"""<div class="lcol">{qtag(m, s['q'])}<h2 class="h-q r" style="--i:0" data-edit>{e(s['question'])}</h2>
<p class="intro r" style="--i:1" data-edit>{e(s['intro'])}</p></div><div class="lk">{lk}</div>"""


def render_tips(s, m, ctx):
    stat = f'<div class="statb r" style="--i:2" data-edit>{e(s["stat"])}</div>' if s.get("stat") else ""
    cards = "".join(f'<div class="tc r" style="--i:{i+2}"><div class="t" data-edit>{e(x["t"])}</div><div class="dd" data-edit>{e(x["d"])}</div></div>' for i, x in enumerate(s["items"]))
    head = f'<div class="top"><div class="qrow">{qtag(m, s["q"])}{stat}</div><h2 class="h-q r" style="--i:0" data-edit>{e(s["question"])}</h2><div class="r" style="--i:1">{quotes(s["quotes"])}</div></div>'
    return head + f'<div class="tgrid">{cards}</div>'


def render_timeline(s, m, ctx):
    it = "".join(f'<div class="tli r" style="--i:{i+3}"><div class="w" data-edit>{e(x["when"])}</div><div class="t" data-edit>{e(x["what"])}</div></div>' for i, x in enumerate(s["items"]))
    stat = f'<div class="statb r" style="--i:2" data-edit>{e(s["stat"])}</div>' if s.get("stat") else ""
    return f"""<div class="top"><div class="qrow">{qtag(m, s['q'])}{stat}</div><h2 class="h-q r" style="--i:0;width:1300px" data-edit>{e(s['question'])}</h2>
<div class="r" style="--i:1">{quotes(s['quotes'])}</div></div>
<p class="lead r" style="--i:2" data-edit>{e(s['lead'])}</p><div class="tl">{it}</div>"""


def render_loop(s, m, ctx):
    svg = f"""<svg viewBox="0 0 760 560" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="ah" markerWidth="12" markerHeight="12" refX="6" refY="6" orient="auto"><path d="M0,0 L12,6 L0,12 z" fill="#ff3300"/></marker></defs>
<path d="M230,120 C330,10 430,10 530,110" fill="none" stroke="#ff3300" stroke-width="8" marker-end="url(#ah)"/>
<path d="M530,440 C430,550 330,550 230,450" fill="none" stroke="#ff3300" stroke-width="8" marker-end="url(#ah)"/>
<circle cx="200" cy="280" r="150" fill="#0d0d0d"/><circle cx="560" cy="280" r="150" fill="#ff3300"/>
<text x="200" y="295" text-anchor="middle" fill="#fff" font-family="Archivo" font-weight="800" font-size="52">{e(s['a'])}</text>
<text x="560" y="295" text-anchor="middle" fill="#fff" font-family="Archivo" font-weight="800" font-size="52">{e(s['b'])}</text></svg>"""
    return f"""<div class="lcol">{qtag(m, s['q'])}<h2 class="h-q r" style="--i:0" data-edit>{e(s['question'])}</h2>
<p class="txt r" style="--i:2" data-edit>{e(s['text'])}</p></div>
<div class="loopv r" style="--i:1">{svg}</div>
<div class="aside r" style="--i:4"><span class="q" data-edit>{e(s['aside_q'])}</span><span class="a" data-edit>{e(s['aside_a'])}</span></div>"""


def render_index(s, m, ctx):
    groups = []
    for g in s["groups"]:
        items = "".join(f'<a class="ixi" href="#{ctx["qpage"][q["id"]]}"><span class="n">{e(m["see_q"])} {e(q["id"])}</span><span class="t">{e(q["t"])}</span><span class="p">{e(m["page"])} {ctx["qpage"][q["id"]]}</span></a>' for q in g["qs"])
        groups.append(f'<div class="ixg r" style="--i:{len(groups)+1}"><div class="label">{e(g["name"])}</div>{items}</div>')
    return f'<h2 class="h-q r" style="--i:0;font-size:64px" data-edit>{e(s["title"])}</h2><div class="ix">{"".join(groups)}</div>'


def render_closing(s, m, ctx):
    cols = "".join(f'<div class="ci r" style="--i:{i+1}"><div class="n">{i+1}</div><div class="t" data-edit>{e(x["t"])}</div><div class="dd" data-edit>{e(x["d"])}</div></div>' for i, x in enumerate(s["items"]))
    return f"""<div class="redbar"></div><h2 class="h-xl r" style="--i:0" data-edit>{e(s['title'])}</h2>
<div class="cols c2">{cols}</div>
<div class="thanks r" style="--i:6"><span class="tt" data-edit>{e(s['thanks'])}</span><span class="sp" data-edit>{e(s['speaker'])}</span></div>"""


def render_roles(s, m, ctx):
    cards = "".join(f'<div class="rli r" style="--i:{i+1}"><div class="n">{i+1:02d}</div><div class="t" data-edit>{e(x["name"])}</div><div class="q" data-edit>{e(x["q"])}</div><div class="tools-l" data-edit>{e(x["tools"])}</div></div>' for i, x in enumerate(s["items"]))
    return f"""<div class="kick label r" style="--i:0">{e(s['kicker'])}</div>
<h2 class="h-xl r" style="--i:0" data-edit>{e(s['title'])}</h2>
<div class="rl">{cards}</div><p class="more r" style="--i:7" data-edit>{e(s['more'])}</p>"""


def render_role(s, m, ctx):
    path = "".join(f"<li data-edit>{e(x)}</li>" for x in s["roadmap"])
    work = "".join(f"<li data-edit>{e(x)}</li>" for x in s["work"])
    cases = "".join(f'<div class="case r" style="--i:{i+5}"><div class="t"><small>{e(m["cases"])} {i+1}</small><span data-edit>{e(c["t"])}</span></div><div class="dd" data-edit>{e(c["d"])}</div></div>' for i, c in enumerate(s["cases"]))
    return f"""<div class="rn r" style="--i:1">{e(s['n'])}</div>
<div class="hd"><div class="label r" style="--i:0">{e(m['role_of'])} {e(s['n'])} / 5</div>
<h2 class="h-xl r" style="--i:0" data-edit>{e(s['name'])}</h2><p class="tg r" style="--i:1" data-edit>{e(s['tagline'])}</p></div>
<div class="c1 r" style="--i:2"><div class="label">{e(m['roadmap'])}</div><ol class="path">{path}</ol></div>
<div class="c2 r" style="--i:3"><div class="label">{e(m['work'])}</div><ul class="pts">{work}</ul></div>
<div class="cases">{cases}</div>"""


def render_venn(s, m, ctx):
    L = s["labels"]
    def lbl(x, y, lines, fill):
        return "".join(f'<text x="{x}" y="{y + i*46}" text-anchor="middle" fill="{fill}" font-family="Archivo" font-weight="800" font-size="40">{e(t)}</text>' for i, t in enumerate(lines))
    # geometry traced from the reference diagram (768x575), scaled 1.12
    svg = f"""<svg viewBox="0 0 880 660" xmlns="http://www.w3.org/2000/svg">
<circle cx="308" cy="302" r="292" fill="#ffd9cc"/>
<circle cx="308" cy="375" r="213" fill="#ffad94"/>
<circle cx="308" cy="465" r="123" fill="#ff7a52"/>
<circle cx="588" cy="352" r="258" fill="#0d0d0d" fill-opacity=".62" style="mix-blend-mode:multiply"/>
{lbl(308, 78, L['ai'], '#0d0d0d')}{lbl(245, 268, L['ml'], '#0d0d0d')}{lbl(285, 458, L['dl'], '#0d0d0d')}{lbl(715, 340, L['ds'], '#ffffff')}</svg>"""
    sw = ["#ffd9cc", "#ffad94", "#ff7a52", "#5c5c5c"]
    defs = "".join(f'<div class="df r" style="--i:{i+2}"><i style="background:{sw[i]}"></i><div class="t" data-edit>{e(x["t"])}</div><div class="dd" data-edit>{e(x["d"])}</div></div>' for i, x in enumerate(s["defs"]))
    return f"""<div class="kick label r" style="--i:0">{e(s['kicker'])}</div>
<h2 class="h-xl r" style="--i:0" data-edit>{e(s['title'])}</h2>
<div class="vd r" style="--i:1">{svg}</div><div class="defs">{defs}</div>
<p class="vnote r" style="--i:7" data-edit>{e(s['note'])}</p>"""


RENDER = {k[len("render_"):]: v for k, v in globals().items() if k.startswith("render_")}


# =============================================================================
# CONTROLLER JS: stage scaling, navigation, hash deep links, inline editing
# =============================================================================
JS = r"""
/* === SLIDE PRESENTATION CONTROLLER === */
class SlidePresentation {
  constructor() {
    this.slides = [...document.querySelectorAll('.slide')];
    this.stage = document.getElementById('deckStage');
    this.bar = document.getElementById('progress');
    this.i = 0; this.lock = false;
    this.scale(); addEventListener('resize', () => this.scale());
    addEventListener('keydown', ev => this.key(ev));
    addEventListener('wheel', ev => this.wheel(ev), { passive: true });
    let x0 = null;
    addEventListener('touchstart', ev => { x0 = ev.touches[0].clientX; }, { passive: true });
    addEventListener('touchend', ev => { if (x0 === null) return; const dx = ev.changedTouches[0].clientX - x0; if (Math.abs(dx) > 50) this.go(this.i + (dx < 0 ? 1 : -1)); x0 = null; });
    addEventListener('hashchange', () => this.fromHash());
    this.fromHash(true);
  }
  scale() {
    const k = Math.min(innerWidth / 1920, innerHeight / 1080);
    this.stage.style.transform = `translate(${(innerWidth - 1920 * k) / 2}px, ${(innerHeight - 1080 * k) / 2}px) scale(${k})`;
  }
  fromHash(first) { const n = parseInt(location.hash.slice(1), 10); this.go(Number.isFinite(n) ? n - 1 : (first ? 0 : this.i), true); }
  key(ev) {
    if (document.body.classList.contains('editing')) return;
    const next = ['ArrowRight', 'ArrowDown', ' ', 'PageDown'], prev = ['ArrowLeft', 'ArrowUp', 'PageUp'];
    if (next.includes(ev.key)) { ev.preventDefault(); this.go(this.i + 1); }
    else if (prev.includes(ev.key)) { ev.preventDefault(); this.go(this.i - 1); }
    else if (ev.key === 'Home') this.go(0); else if (ev.key === 'End') this.go(this.slides.length - 1);
  }
  wheel(ev) {
    if (this.lock || Math.abs(ev.deltaY) < 30 || document.body.classList.contains('editing')) return;
    this.lock = true; setTimeout(() => this.lock = false, 700);
    this.go(this.i + (ev.deltaY > 0 ? 1 : -1));
  }
  go(n, fromHash) {
    this.i = Math.max(0, Math.min(n, this.slides.length - 1));
    this.slides.forEach((s, j) => { s.classList.toggle('active', j === this.i); s.classList.toggle('visible', j === this.i); });
    this.bar.style.width = `${(this.i + 1) / this.slides.length * 100}%`;
    if (!fromHash) history.replaceState(null, '', `#${this.i + 1}`);
  }
}
const deck = new SlidePresentation();

/* === INLINE EDITING: hover top-left or press E; Ctrl+S downloads the edited file === */
const editor = {
  isActive: false,
  key: 'deck-edits:' + location.pathname,
  els: () => [...document.querySelectorAll('[data-edit]')],
  restore() { try { const d = JSON.parse(localStorage.getItem(this.key) || '{}'); this.els().forEach((el, i) => { if (d[i] !== undefined) el.innerHTML = d[i]; }); } catch (_) {} },
  persist() { const d = {}; this.els().forEach((el, i) => d[i] = el.innerHTML); localStorage.setItem(this.key, JSON.stringify(d)); },
  toggleEditMode() {
    this.isActive = !this.isActive;
    document.body.classList.toggle('editing', this.isActive);
    this.els().forEach(el => el.contentEditable = this.isActive ? 'true' : 'false');
    toggle.classList.toggle('active', this.isActive); toggle.textContent = this.isActive ? 'Done (E)' : 'Edit (E)';
    if (!this.isActive) this.persist();
  },
  save() {
    this.persist();
    const clone = document.documentElement.cloneNode(true);
    clone.querySelectorAll('[contenteditable]').forEach(el => el.removeAttribute('contenteditable'));
    clone.querySelector('body').classList.remove('editing');
    const blob = new Blob(['<!DOCTYPE html>\n' + clone.outerHTML], { type: 'text/html' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
    a.download = location.pathname.split('/').pop() || 'deck.html'; a.click();
  }
};
const toggle = document.getElementById('editToggle'), hot = document.querySelector('.edit-hotzone');
let hideT = null;
const show = () => { clearTimeout(hideT); toggle.classList.add('show'); };
const hide = () => { hideT = setTimeout(() => { if (!editor.isActive) toggle.classList.remove('show'); }, 400); };
hot.addEventListener('mouseenter', show); hot.addEventListener('mouseleave', hide);
toggle.addEventListener('mouseenter', show); toggle.addEventListener('mouseleave', hide);
hot.addEventListener('click', () => editor.toggleEditMode());
toggle.addEventListener('click', () => editor.toggleEditMode());
document.addEventListener('keydown', ev => {
  if ((ev.key === 'e' || ev.key === 'E') && !ev.target.isContentEditable) editor.toggleEditMode();
  if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === 's') { ev.preventDefault(); editor.save(); }
});
document.addEventListener('input', () => editor.isActive && editor.persist());
editor.restore();
"""


# =============================================================================
# BUILD
# =============================================================================
QUESTION_TYPES = {"qa", "ladder", "links", "tips", "timeline", "loop", "statement"}


def build(lang: str) -> pathlib.Path:
    data = json.loads((ROOT / "content" / f"{lang}.json").read_text(encoding="utf-8"))
    m, slides = data["meta"], data["slides"]
    # first slide that answers each question -> page number for the Q&A index and cross-links
    qpage: dict[str, int] = {}
    for n, s in enumerate(slides, 1):
        if s["type"] in QUESTION_TYPES and s.get("q"):
            qpage.setdefault(s["q"], n)
    ctx = {"qpage": qpage}
    total = len(slides)
    parts = []
    for n, s in enumerate(slides, 1):
        chrome = "" if s["type"] == "cover" else (
            f'<div class="chrome"><span class="sec">{e(data["sections"][s["sec"]])}</span>'
            f'<span class="pg"><b>{n:02d}</b> {m["of"]} {total:02d}</span></div>')
        parts.append(f'<section class="slide {s["type"]}" data-n="{n}"><div class="grid"></div>{chrome}{RENDER[s["type"]](s, m, ctx)}</section>')
    doc = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(m['title'])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?{FONTS}&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
/* === FIXED-STAGE BASE (viewport-base.css, verbatim) === */
{BASE_CSS}
{CSS}
</style>
</head>
<body>
<div class="edit-hotzone"></div><button class="edit-toggle" id="editToggle" title="Edit mode (E)">Edit (E)</button>
<div class="deck-viewport"><main class="deck-stage" id="deckStage">
{chr(10).join(parts)}
</main></div>
<div class="progress" id="progress"></div>
<script>{JS}</script>
</body>
</html>"""
    out = ROOT / f"deck-{lang}.html"
    out.write_text(doc, encoding="utf-8")
    return out


if __name__ == "__main__":
    for lang in ("vi", "en"):
        p = build(lang)
        print(p.name, p.stat().st_size, "bytes")
