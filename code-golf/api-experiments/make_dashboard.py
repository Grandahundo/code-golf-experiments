#!/usr/bin/env python3
"""Generate a self-contained dashboard.html for a compare run.

Usage: python3 make_dashboard.py runs/compare-20260717-132031
Writes <run_dir>/dashboard.html with results.json embedded.
"""
import json, os, sys

TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Code-golf 实验 — 长度稳定性与题目难度</title>
<style>
  .viz-root {
    color-scheme: light;
    --page:           #f9f9f7;
    --surface-1:      #fcfcfb;
    --text-primary:   #0b0b0b;
    --text-secondary: #52514e;
    --text-muted:     #898781;
    --grid:           #e1e0d9;
    --axis:           #c3c2b7;
    --border:         rgba(11,11,11,0.10);
    --series-1:       #2a78d6;  /* deepseek */
    --series-2:       #008300;  /* glm */
    --series-3:       #e87ba4;  /* qwen */
    --bar:            #4a3aa7;  /* task-level difficulty bars (violet slot) */
    --seq-1: #cde2fb; --seq-2: #9ec5f4; --seq-3: #6da7ec; --seq-4: #3987e5; --seq-5: #256abf;
    --seq-ink-1: #0b0b0b; --seq-ink-2: #0b0b0b; --seq-ink-3: #0b0b0b; --seq-ink-4: #ffffff; --seq-ink-5: #ffffff;
  }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) .viz-root {
      color-scheme: dark;
      --page:           #0d0d0d;
      --surface-1:      #1a1a19;
      --text-primary:   #ffffff;
      --text-secondary: #c3c2b7;
      --text-muted:     #898781;
      --grid:           #2c2c2a;
      --axis:           #383835;
      --border:         rgba(255,255,255,0.10);
      --series-1:       #3987e5;
      --series-2:       #008300;
      --series-3:       #d55181;
      --bar:            #9085e9;
      --seq-1: #104281; --seq-2: #1c5cab; --seq-3: #2a78d6; --seq-4: #5598e7; --seq-5: #86b6ef;
      --seq-ink-1: #ffffff; --seq-ink-2: #ffffff; --seq-ink-3: #ffffff; --seq-ink-4: #0b0b0b; --seq-ink-5: #0b0b0b;
    }
  }
  :root[data-theme="dark"] .viz-root {
    color-scheme: dark;
    --page:           #0d0d0d;
    --surface-1:      #1a1a19;
    --text-primary:   #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted:     #898781;
    --grid:           #2c2c2a;
    --axis:           #383835;
    --border:         rgba(255,255,255,0.10);
    --series-1:       #3987e5;
    --series-2:       #008300;
    --series-3:       #d55181;
    --bar:            #9085e9;
    --seq-1: #104281; --seq-2: #1c5cab; --seq-3: #2a78d6; --seq-4: #5598e7; --seq-5: #86b6ef;
    --seq-ink-1: #ffffff; --seq-ink-2: #ffffff; --seq-ink-3: #ffffff; --seq-ink-4: #0b0b0b; --seq-ink-5: #0b0b0b;
  }

  * { box-sizing: border-box; }
  body.viz-root {
    margin: 0; padding: 24px;
    background: var(--page); color: var(--text-primary);
    font: 14px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif;
  }
  .wrap { max-width: 1160px; margin: 0 auto; }
  h1 { font-size: 20px; font-weight: 650; margin: 0 0 2px; }
  .sub { color: var(--text-secondary); margin: 0 0 16px; font-size: 13px; }

  .filters { display: flex; gap: 8px; align-items: center; margin: 0 0 16px; flex-wrap: wrap; }
  .filters .hint { color: var(--text-muted); font-size: 12px; margin-left: 4px; }
  .chip {
    display: inline-flex; align-items: center; gap: 7px;
    padding: 5px 12px; border-radius: 999px; cursor: pointer;
    background: var(--surface-1); border: 1px solid var(--border);
    color: var(--text-primary); font-size: 13px; user-select: none;
  }
  .chip .sw { width: 10px; height: 10px; border-radius: 50%; }
  .chip[aria-pressed="false"] { opacity: .38; }
  .chip:focus-visible { outline: 2px solid var(--series-1); outline-offset: 2px; }

  .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px,1fr)); gap: 12px; margin-bottom: 16px; }
  .tile {
    background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 10px; padding: 14px 16px;
  }
  .tile .label { color: var(--text-secondary); font-size: 12.5px; }
  .tile .value { font-size: 26px; font-weight: 600; margin-top: 2px; }
  .tile .note  { color: var(--text-muted); font-size: 12px; margin-top: 2px; }

  .card {
    background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 10px; padding: 16px 18px 12px; margin-bottom: 16px;
  }
  .card h2 { font-size: 15px; font-weight: 600; margin: 0 0 2px; }
  .card .desc { color: var(--text-secondary); font-size: 12.5px; margin: 0 0 10px; }
  .row2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  @media (max-width: 900px) { .row2 { grid-template-columns: 1fr; } }
  svg { display: block; width: 100%; height: auto; }
  svg text { font: 11.5px system-ui, -apple-system, "Segoe UI", sans-serif; }
  .tick-num { font-variant-numeric: tabular-nums; }

  .legend { display: flex; gap: 16px; align-items: center; color: var(--text-secondary); font-size: 12.5px; margin: 2px 0 8px; flex-wrap: wrap; }
  .legend .item { display: inline-flex; gap: 6px; align-items: center; }

  #tooltip {
    position: fixed; pointer-events: none; z-index: 10; display: none;
    background: var(--surface-1); border: 1px solid var(--border);
    border-radius: 8px; padding: 8px 11px; font-size: 12.5px;
    box-shadow: 0 4px 14px rgba(0,0,0,.14); min-width: 130px;
  }
  #tooltip .tt-val { font-size: 15px; font-weight: 650; }
  #tooltip .tt-sub { color: var(--text-secondary); margin-top: 1px; }

  table { border-collapse: collapse; width: 100%; font-size: 12.5px; }
  th, td { text-align: right; padding: 6px 10px; border-bottom: 1px solid var(--grid); font-variant-numeric: tabular-nums; }
  th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) { text-align: left; }
  th { color: var(--text-secondary); font-weight: 600; }
  td .dot { display: inline-block; width: 9px; height: 9px; border-radius: 50%; margin-right: 6px; vertical-align: baseline; }
  .theme-btn { margin-left: auto; }
  footer { color: var(--text-muted); font-size: 12px; margin-top: 4px; }
</style>
</head>
<body class="viz-root">
<div class="wrap">
  <h1>Code-golf 实验：trial 稳定性 × 题目难度</h1>
  <p class="sub" id="runmeta"></p>

  <div class="filters" id="filters">
    <span class="hint">模型筛选（作用于下方全部图表）</span>
    <button class="chip theme-btn" id="themeBtn" aria-pressed="false">深色模式</button>
  </div>

  <div class="kpis" id="kpis"></div>

  <div class="card">
    <h2>逐 trial 代码长度 — 同题稳定性 &amp; 题间差异</h2>
    <p class="desc">每个点是一次 trial（对数轴）。同一列内点越集中 = 该题该模型输出越稳定；横向对比各题的整体高度 = 题目间的长度差异。横线为该题该模型正确解的中位数。</p>
    <div class="legend" id="stripLegend"></div>
    <div id="strip"></div>
  </div>

  <div class="row2">
    <div class="card">
      <h2>题目难度榜（按错误率排序）</h2>
      <p class="desc">错误率 = 所选模型全部 trial 中未通过的比例；长度为正确解中位数。两者共同刻画难度。</p>
      <div id="board"></div>
    </div>
    <div class="card">
      <h2>长度变异系数 CV — 稳定性热图</h2>
      <p class="desc">CV = std / mean（该题该模型正确解长度）。颜色越远离底色 = 越不稳定；“–” 表示正确 trial &lt; 2。</p>
      <div id="heat"></div>
    </div>
  </div>

  <div class="card">
    <h2>数据表（全部数值）</h2>
    <p class="desc">图中每个值都可在此读取。</p>
    <div style="overflow-x:auto"><table id="tbl"></table></div>
  </div>

  <footer id="foot"></footer>
</div>
<div id="tooltip" role="status"></div>

<script>
const DATA = __DATA__;
const META = __META__;
const MODELS = ["deepseek-v4-pro", "glm-5.2", "qwen3.7-max"];
const SHORT  = {"deepseek-v4-pro": "deepseek", "glm-5.2": "glm", "qwen3.7-max": "qwen"};
let active = new Set(MODELS);

// ── helpers ──────────────────────────────────────────────────
const TASKS = [...new Set(DATA.map(r => r.task))].sort();
const byTM = {};
for (const r of DATA) (byTM[r.task + "|" + r.model] ??= []).push(r);
const median = a => { const s = [...a].sort((x,y)=>x-y), m = s.length>>1;
  return s.length ? (s.length % 2 ? s[m] : (s[m-1]+s[m])/2) : null; };
const mean = a => a.reduce((x,y)=>x+y,0)/a.length;
const stdev = a => a.length>1 ? Math.sqrt(a.reduce((s,x)=>s+(x-mean(a))**2,0)/(a.length-1)) : null;
const css = n => getComputedStyle(document.body).getPropertyValue(n).trim();
const seriesColor = m => css("--series-" + (MODELS.indexOf(m)+1));
const fmtB = v => v >= 1000 ? (v/1000).toFixed(1).replace(/\.0$/,"") + "k" : String(Math.round(v));
const el = (tag, attrs, parent) => { const e = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const k in attrs) e.setAttribute(k, attrs[k]); if (parent) parent.appendChild(e); return e; };

function cellStats(t, m) {
  const rs = byTM[t + "|" + m] || [];
  const ok = rs.filter(r => r.correct).map(r => r.bytes);
  return { n: rs.length, nOk: ok.length, ok,
           med: ok.length ? median(ok) : null,
           min: ok.length ? Math.min(...ok) : null,
           max: ok.length ? Math.max(...ok) : null,
           cv: ok.length > 1 ? 100*stdev(ok)/mean(ok) : null,
           secs: rs.length ? mean(rs.map(r => r.seconds)) : null };
}

// ── tooltip ──────────────────────────────────────────────────
const tt = document.getElementById("tooltip");
function showTip(x, y, lines) {  // lines: [[text, cls|swatchColor?], ...]
  tt.replaceChildren();
  for (const [text, cls, swatch] of lines) {
    const d = document.createElement("div");
    if (cls) d.className = cls;
    if (swatch) { const s = document.createElement("span");
      s.style.cssText = `display:inline-block;width:10px;height:3px;border-radius:2px;margin:0 6px 3px 0;background:${swatch}`;
      d.appendChild(s); }
    d.appendChild(document.createTextNode(text));
    tt.appendChild(d);
  }
  tt.style.display = "block";
  const w = tt.offsetWidth, h = tt.offsetHeight;
  tt.style.left = Math.min(x + 14, innerWidth - w - 8) + "px";
  tt.style.top  = Math.max(8, Math.min(y - h - 12, innerHeight - h - 8)) + "px";
}
const hideTip = () => tt.style.display = "none";

// ── filter chips ─────────────────────────────────────────────
function buildFilters() {
  const bar = document.getElementById("filters");
  const btn = document.getElementById("themeBtn");
  MODELS.forEach(m => {
    const c = document.createElement("button");
    c.className = "chip"; c.setAttribute("aria-pressed", "true"); c.dataset.model = m;
    const sw = document.createElement("span"); sw.className = "sw"; c.appendChild(sw);
    c.appendChild(document.createTextNode(m));
    c.onclick = () => {
      if (active.has(m)) { if (active.size === 1) return; active.delete(m); }
      else active.add(m);
      c.setAttribute("aria-pressed", active.has(m));
      renderAll();
    };
    bar.insertBefore(c, btn);
  });
  btn.textContent = matchMedia("(prefers-color-scheme: dark)").matches ? "浅色模式" : "深色模式";
  btn.onclick = () => {
    const dark = document.documentElement.dataset.theme === "dark" ||
      (!document.documentElement.dataset.theme && matchMedia("(prefers-color-scheme: dark)").matches);
    document.documentElement.dataset.theme = dark ? "light" : "dark";
    btn.textContent = dark ? "深色模式" : "浅色模式";
    renderAll();
  };
  matchMedia("(prefers-color-scheme: dark)").addEventListener("change", renderAll);
}
function paintChips() {
  document.querySelectorAll(".chip[data-model]").forEach(c =>
    c.querySelector(".sw").style.background = seriesColor(c.dataset.model));
}

// ── KPI row ──────────────────────────────────────────────────
function renderKPIs() {
  const ms = MODELS.filter(m => active.has(m));
  const rows = DATA.filter(r => ms.includes(r.model));
  const nOk = rows.filter(r => r.correct).length;
  const accByM = ms.map(m => { const rs = rows.filter(r => r.model === m);
    return [m, rs.filter(r => r.correct).length, rs.length]; })
    .sort((a,b) => b[1]/b[2] - a[1]/a[2]);
  const errByT = TASKS.map(t => { const rs = rows.filter(r => r.task === t);
    return [t, rs.filter(r => !r.correct).length, rs.length]; })
    .sort((a,b) => b[1]/b[2] - a[1]/a[2]);
  const meds = TASKS.map(t => median(rows.filter(r => r.task === t && r.correct).map(r => r.bytes)))
    .filter(v => v != null);
  const tiles = [
    ["总体正确率", Math.round(100*nOk/rows.length) + "%", `${nOk}/${rows.length} trials`],
    ["正确率最高模型", SHORT[accByM[0][0]], `${accByM[0][1]}/${accByM[0][2]} 正确`],
    ["最难题目", errByT[0][0], `${errByT[0][2]-errByT[0][1]}/${errByT[0][2]} 正确`],
    ["题间中位长度跨度", (Math.max(...meds)/Math.min(...meds)).toFixed(1) + "×",
      `${fmtB(Math.min(...meds))}B → ${fmtB(Math.max(...meds))}B`],
  ];
  const k = document.getElementById("kpis"); k.replaceChildren();
  for (const [label, value, note] of tiles) {
    const d = document.createElement("div"); d.className = "tile";
    for (const [cls, txt] of [["label",label],["value",value],["note",note]]) {
      const e = document.createElement("div"); e.className = cls; e.textContent = txt; d.appendChild(e); }
    k.appendChild(d);
  }
}

// ── strip plot ───────────────────────────────────────────────
function renderStrip() {
  const ms = MODELS.filter(m => active.has(m));
  const W = 1120, H = 460, L = 62, R = 14, T = 14, B = 44;
  const plotW = W - L - R, plotH = H - T - B;
  const yMin = 250, yMax = 5200;
  const yOf = v => T + plotH * (Math.log(yMax) - Math.log(Math.max(v, yMin))) / (Math.log(yMax) - Math.log(yMin));
  const band = plotW / TASKS.length;
  const xOf = (t, m) => L + band * (TASKS.indexOf(t) + .5) + (ms.indexOf(m) - (ms.length-1)/2) * Math.min(22, band/(ms.length+1));

  const host = document.getElementById("strip"); host.replaceChildren();
  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img",
    "aria-label": "逐 trial 代码长度分布，按题目与模型分组" }, host);

  // grid + y ticks
  for (const v of [250, 500, 1000, 2000, 4000]) {
    const y = yOf(v);
    el("line", { x1: L, x2: W - R, y1: y, y2: y, stroke: css("--grid"), "stroke-width": 1 }, svg);
    el("text", { x: L - 8, y: y + 4, "text-anchor": "end", fill: css("--text-muted"),
                 class: "tick-num" }, svg).textContent = fmtB(v);
  }
  el("line", { x1: L, x2: W - R, y1: T + plotH, y2: T + plotH, stroke: css("--axis"), "stroke-width": 1 }, svg);
  el("text", { x: 14, y: T + 10, fill: css("--text-muted") }, svg).textContent = "bytes";
  // x labels
  TASKS.forEach(t => el("text", { x: L + band*(TASKS.indexOf(t)+.5), y: H - 18,
    "text-anchor": "middle", fill: css("--text-secondary") }, svg).textContent = t);

  // median ticks + dots
  const dots = [];
  for (const t of TASKS) for (const m of ms) {
    const st = cellStats(t, m), x = xOf(t, m);
    if (st.med != null)
      el("line", { x1: x-9, x2: x+9, y1: yOf(st.med), y2: yOf(st.med),
                   stroke: seriesColor(m), "stroke-width": 2.5, "stroke-linecap": "round" }, svg);
    for (const r of (byTM[t + "|" + m] || [])) {
      if (!r.bytes) continue;
      const cy = yOf(r.bytes);
      const c = el("circle", { cx: x, cy, r: 4.5, tabindex: 0,
        fill: r.correct ? seriesColor(m) : css("--surface-1"),
        stroke: r.correct ? css("--surface-1") : seriesColor(m),
        "stroke-width": 2 }, svg);
      const tip = (px, py) => showTip(px, py, [
        [`${r.bytes} B`, "tt-val"],
        [`${r.task} · trial ${r.trial}`, "tt-sub"],
        [m, "tt-sub", seriesColor(m)],
        [(r.correct ? "✓ 正确 " : "✗ 未通过 ") + (r.passed || "") + ` · ${r.seconds}s`, "tt-sub"],
        ...(r.bytes < yMin ? [["（超出坐标下限，按下限绘制）", "tt-sub"]] : []),
      ]);
      c.addEventListener("focus", () => { const b = c.getBoundingClientRect(); tip(b.right, b.top); });
      c.addEventListener("blur", hideTip);
      dots.push({ x, y: cy, tip, c });
    }
  }
  // nearest-dot hover (24px reach) — pointer never has to hit a 9px dot
  svg.addEventListener("pointermove", ev => {
    const box = svg.getBoundingClientRect(), sx = W / box.width;
    const px = (ev.clientX - box.left) * sx, py = (ev.clientY - box.top) * sx;
    let best = null, bd = 24 * sx;
    for (const d of dots) { const dd = Math.hypot(d.x - px, d.y - py);
      if (dd < bd) { bd = dd; best = d; } }
    dots.forEach(d => d.c.setAttribute("r", d === best ? 6 : 4.5));
    best ? best.tip(ev.clientX, ev.clientY) : hideTip();
  });
  svg.addEventListener("pointerleave", () => { hideTip(); dots.forEach(d => d.c.setAttribute("r", 4.5)); });

  // legend
  const lg = document.getElementById("stripLegend"); lg.replaceChildren();
  const item = (mk, label) => { const s = document.createElement("span"); s.className = "item";
    s.appendChild(mk); s.appendChild(document.createTextNode(label)); lg.appendChild(s); };
  for (const m of ms) { const sw = document.createElement("span");
    sw.style.cssText = `width:10px;height:10px;border-radius:50%;background:${seriesColor(m)}`;
    item(sw, m); }
  const hollow = document.createElement("span");
  hollow.style.cssText = `width:9px;height:9px;border-radius:50%;border:2px solid ${css("--text-muted")}`;
  item(hollow, "空心 = 未通过的 trial");
  const md = document.createElement("span");
  md.style.cssText = `width:14px;height:0;border-top:2.5px solid ${css("--text-secondary")}`;
  item(md, "横线 = 正确解中位数");
}

// ── difficulty board ─────────────────────────────────────────
function renderBoard() {
  const ms = MODELS.filter(m => active.has(m));
  const rows = TASKS.map(t => {
    const rs = DATA.filter(r => r.task === t && ms.includes(r.model));
    const ok = rs.filter(r => r.correct);
    return { t, n: rs.length, err: rs.length - ok.length,
             errRate: (rs.length - ok.length) / rs.length,
             med: ok.length ? median(ok.map(r => r.bytes)) : null };
  }).sort((a,b) => b.errRate - a.errRate || (b.med ?? 0) - (a.med ?? 0));

  const W = 520, rowH = 30, T = 26, H = T + rowH * rows.length + 8;
  const L = 72, colGap = 24, colW = (W - L - colGap) / 2 - 8;
  const maxMed = Math.max(...rows.map(r => r.med ?? 0));
  const host = document.getElementById("board"); host.replaceChildren();
  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "题目难度排序" }, host);
  const bar = css("--bar");

  el("text", { x: L, y: 14, fill: css("--text-secondary") }, svg).textContent = "错误率";
  el("text", { x: L + colW + colGap + 8, y: 14, fill: css("--text-secondary") }, svg).textContent = "正确解中位长度";

  const rrect = (x, y, w, h, p) => { const r = Math.min(4, w);  // rounded data-end, square baseline
    el("path", { d: `M${x},${y} h${Math.max(0,w-r)} a${r},${r} 0 0 1 ${r},${r} v${h-2*r} a${r},${r} 0 0 1 -${r},${r} h-${Math.max(0,w-r)} z`,
                 fill: bar, opacity: p ? 1 : .45 }, svg); };

  rows.forEach((r, i) => {
    const y = T + i * rowH, bh = 14, by = y + (rowH - bh) / 2 - 2;
    el("text", { x: L - 8, y: y + rowH/2 + 2, "text-anchor": "end", fill: css("--text-primary") }, svg)
      .textContent = r.t.replace("task", "");
    // error-rate bar
    const w1 = colW * r.errRate;
    if (w1 > 0) rrect(L, by, w1, bh, true);
    else el("line", { x1: L, x2: L, y1: by, y2: by + bh, stroke: css("--axis"), "stroke-width": 2 }, svg);
    el("text", { x: L + Math.max(w1, 2) + 6, y: by + bh - 3, fill: css("--text-secondary"), class: "tick-num" }, svg)
      .textContent = `${r.err}/${r.n}`;
    // median-length bar
    const x2 = L + colW + colGap + 8;
    if (r.med != null) {
      const w2 = colW * r.med / maxMed;
      rrect(x2, by, w2, bh, true);
      el("text", { x: x2 + w2 + 6, y: by + bh - 3, fill: css("--text-secondary"), class: "tick-num" }, svg)
        .textContent = fmtB(r.med) + "B";
    } else
      el("text", { x: x2, y: by + bh - 3, fill: css("--text-muted") }, svg).textContent = "无正确解";
  });
}

// ── CV heatmap ───────────────────────────────────────────────
function renderHeat() {
  const ms = MODELS.filter(m => active.has(m));
  const bins = [15, 25, 40, 60];  // CV% thresholds → seq steps 1..5
  const host = document.getElementById("heat"); host.replaceChildren();
  const L = 72, T = 26, cw = 118, ch = 30, gap = 2;
  const W = L + ms.length * (cw + gap) + 8, H = T + TASKS.length * (ch + gap) + 6;
  const svg = el("svg", { viewBox: `0 0 ${W} ${H}`, role: "img", "aria-label": "长度变异系数热图" }, host);
  svg.style.maxWidth = (W * 0.9) + "px";

  ms.forEach((m, j) => el("text", { x: L + j*(cw+gap) + cw/2, y: 14, "text-anchor": "middle",
    fill: css("--text-secondary") }, svg).textContent = SHORT[m]);

  TASKS.forEach((t, i) => {
    el("text", { x: L - 8, y: T + i*(ch+gap) + ch/2 + 4, "text-anchor": "end",
                 fill: css("--text-primary") }, svg).textContent = t.replace("task", "");
    ms.forEach((m, j) => {
      const st = cellStats(t, m);
      const x = L + j*(cw+gap), y = T + i*(ch+gap);
      let fill = css("--surface-1"), ink = css("--text-muted"), label = "–";
      if (st.cv != null) {
        const k = bins.filter(b => st.cv >= b).length + 1;
        fill = css("--seq-" + k); ink = css("--seq-ink-" + k);
        label = st.cv.toFixed(0) + "%";
      }
      const rc = el("rect", { x, y, width: cw, height: ch, rx: 3, fill,
        stroke: st.cv == null ? css("--grid") : "none", "stroke-width": 1, tabindex: 0 }, svg);
      el("text", { x: x + cw/2, y: y + ch/2 + 4, "text-anchor": "middle", fill: ink,
                   class: "tick-num", "pointer-events": "none" }, svg).textContent = label;
      const tip = (px, py) => showTip(px, py, [
        [st.cv != null ? `CV ${st.cv.toFixed(1)}%` : "正确 trial 不足", "tt-val"],
        [`${t} · ${m}`, "tt-sub", seriesColor(m)],
        [`正确 ${st.nOk}/${st.n}` + (st.med != null ? ` · 中位 ${fmtB(st.med)}B · ${fmtB(st.min)}–${fmtB(st.max)}B` : ""), "tt-sub"],
      ]);
      rc.addEventListener("pointermove", ev => tip(ev.clientX, ev.clientY));
      rc.addEventListener("pointerleave", hideTip);
      rc.addEventListener("focus", () => { const b = rc.getBoundingClientRect(); tip(b.right, b.top); });
      rc.addEventListener("blur", hideTip);
    });
  });
}

// ── table ────────────────────────────────────────────────────
function renderTable() {
  const ms = MODELS.filter(m => active.has(m));
  const tbl = document.getElementById("tbl"); tbl.replaceChildren();
  const tr = (cells, head) => { const row = document.createElement("tr");
    cells.forEach(c => { const cell = document.createElement(head ? "th" : "td");
      if (c instanceof Node) cell.appendChild(c); else cell.textContent = c;
      row.appendChild(cell); }); tbl.appendChild(row); };
  tr(["题目", "模型", "正确", "min B", "中位 B", "max B", "CV %", "均耗时 s"], true);
  for (const t of TASKS) for (const m of ms) {
    const st = cellStats(t, m);
    const name = document.createElement("span");
    const d = document.createElement("span"); d.className = "dot";
    d.style.background = seriesColor(m);
    name.appendChild(d); name.appendChild(document.createTextNode(SHORT[m]));
    tr([t, name, `${st.nOk}/${st.n}`,
        st.min ?? "–", st.med != null ? Math.round(st.med) : "–", st.max ?? "–",
        st.cv != null ? st.cv.toFixed(1) : "–",
        st.secs != null ? st.secs.toFixed(0) : "–"]);
  }
}

function renderAll() {
  paintChips();
  renderKPIs(); renderStrip(); renderBoard(); renderHeat(); renderTable();
}

document.getElementById("runmeta").textContent =
  `run: ${META.run} · prompt: ${META.prompt} · ${TASKS.length} 题 × ${META.trials} trials × ${MODELS.length} 模型 = ${DATA.length} 次调用`;
document.getElementById("foot").textContent =
  "长度轴为对数刻度；空心点为未通过 trial；CV 与中位数仅基于正确 trial。";
buildFilters();
renderAll();
</script>
</body>
</html>
"""


def main():
    run_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    run_dir = run_dir.rstrip("/")
    data = json.load(open(f"{run_dir}/results.json"))
    try:
        meta = json.load(open(f"{run_dir}/meta.json"))
    except FileNotFoundError:
        meta = {}
    meta_js = {"run": os.path.basename(os.path.abspath(run_dir)),
               "prompt": meta.get("prompt", "?"),
               "trials": meta.get("trials", "?")}
    html = (TEMPLATE
            .replace("__DATA__", json.dumps(data, ensure_ascii=False))
            .replace("__META__", json.dumps(meta_js, ensure_ascii=False))
            .replace("{DARKNOTE}", ""))
    out = f"{run_dir}/dashboard.html"
    open(out, "w").write(html)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
