#!/usr/bin/env python3
"""Generate a self-contained HTML dashboard for batch experiment results."""

import json
import os
import statistics
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "results", "20260714-212716")
EXPERIMENTS_DIR = os.path.join(SCRIPT_DIR, "experiments")

METHODS = ["comap", "auto_pal", "default"]
METHOD_LABELS = {
    "comap": "CoMAP (11KB Map-and-Act — same as Baseline)",
    "auto_pal": "Auto-PAL (900B minimal)",
    "default": "Default (4.8KB streamlined)",
}
METHOD_COLORS = {
    "comap": "#ef4444",
    "auto_pal": "#3b82f6",
    "default": "#10b981",
}

# ── Load data ──────────────────────────────────────────────────
results = {m: {} for m in METHODS}
all_tasks = set()
for m in METHODS:
    for t in range(1, 11):
        wd = os.path.join(EXPERIMENTS_DIR, m, f"task{t:03d}", "workdir")
        if os.path.isdir(wd):
            files = [f for f in os.listdir(wd) if f.endswith(".py")]
            if files:
                results[m][t] = min(
                    os.path.getsize(os.path.join(wd, f)) for f in files
                )
                all_tasks.add(t)

TASKS = sorted(all_tasks)

# ── Compute stats ──────────────────────────────────────────────
stats = {}
for m in METHODS:
    vals = list(results[m].values())
    if vals:
        stats[m] = {
            "count": len(vals),
            "min": min(vals),
            "max": max(vals),
            "median": round(statistics.median(vals), 1),
            "mean": round(statistics.mean(vals), 1),
            "std": round(statistics.stdev(vals), 2) if len(vals) >= 2 else 0,
        }

# Win counts
wins = {m: 0 for m in METHODS}
for t in TASKS:
    vals = [(results[m].get(t), m) for m in METHODS if results[m].get(t)]
    if vals:
        min_v = min(v for v, _ in vals)
        for v, m in vals:
            if v == min_v:
                wins[m] += 1

# ── Build HTML ─────────────────────────────────────────────────
data_json = json.dumps({
    "tasks": TASKS,
    "results": {m: {str(t): results[m].get(t) for t in TASKS} for m in METHODS},
    "stats": stats,
    "wins": wins,
    "methods": METHODS,
    "methodLabels": METHOD_LABELS,
    "methodColors": METHOD_COLORS,
})
gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

html = rf"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Code Golf — Batch Experiment Results</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: #f8fafc; color: #1e293b; padding: 24px; }}
h1 {{ font-size: 28px; margin-bottom: 8px; }}
.subtitle {{ color: #64748b; margin-bottom: 32px; font-size: 15px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(580px, 1fr));
        gap: 24px; }}
.card {{ background: #fff; border-radius: 14px; padding: 22px;
        box-shadow: 0 1px 3px rgba(0,0,0,.07); border: 1px solid #e2e8f0; }}
.card h2 {{ font-size: 16px; margin-bottom: 14px; color: #334155; }}
.chart-wrap {{ position: relative; width: 100%; }}
.verdict-box {{ background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 12px;
               padding: 18px 24px; margin-bottom: 24px; }}
.verdict-box h2 {{ color: #166534; margin-bottom: 8px; }}
.verdict-box p {{ font-size: 14px; color: #15803d; }}
table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
th, td {{ padding: 7px 10px; text-align: right; border-bottom: 1px solid #e2e8f0; }}
th:first-child, td:first-child {{ text-align: left; font-weight: 600; }}
tr:last-child td {{ border-bottom: none; }}
.badge {{ display: inline-block; padding: 2px 8px; border-radius: 6px;
         font-size: 12px; font-weight: 600; }}
.badge-best {{ background: #dcfce7; color: #166534; }}
.badge-worst {{ background: #fef2f2; color: #991b1b; }}
</style>
</head>
<body>

<h1>🏌️ Code Golf — Batch Experiment Results</h1>
<p class="subtitle">Generated {gen_time} · 3 Methods × 10 Tasks · deepseek-v4-pro</p>

<div class="verdict-box">
<h2>🏆 Verdict: Default > CoMAP > Auto-PAL</h2>
<p>Default (4.8KB streamlined prompt) wins <strong>{wins['default']}/10</strong> tasks with a median of <strong>{stats['default']['median']}B</strong>.
CoMAP (11KB Map-and-Act — same as Baseline) is the most consistent (lowest mean: {stats['comap']['mean']}B).
Auto-PAL (900B minimal) excels on simple tasks but collapses on complex ones.</p>
</div>

<div class="grid">
  <div class="card" style="grid-column: 1 / -1;">
    <h2>📊 Per-Task Best Bytes (lower = better)</h2>
    <div class="chart-wrap"><canvas id="perTaskBar" style="height:400px"></canvas></div>
  </div>

  <div class="card">
    <h2>📈 Method Comparison (Median + Mean)</h2>
    <div class="chart-wrap"><canvas id="medianMean"></canvas></div>
  </div>

  <div class="card">
    <h2>🥇 Task Wins (including ties)</h2>
    <div class="chart-wrap"><canvas id="winPie"></canvas></div>
  </div>

  <div class="card">
    <h2>🔥 Ranking Heatmap (rows = methods, cols = tasks)</h2>
    <div class="chart-wrap"><canvas id="heatmap"></canvas></div>
  </div>

  <div class="card" style="grid-column: 1 / -1;">
    <h2>📋 Complete Results Table</h2>
    <div id="resultsTable"></div>
  </div>
</div>

<script>
var DATA = {data_json};
var T = DATA.tasks;
var M = DATA.methods;
var R = DATA.results;
var S = DATA.stats;
var W = DATA.wins;
var C = DATA.methodColors;
var L = DATA.methodLabels;

Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
Chart.defaults.font.size = 12;

// ── 1. Per-task grouped bar ───────────────────────────────────
(function() {{
  var datasets = M.map(function(m) {{
    return {{
      label: m,
      data: T.map(function(t) {{ return R[m][String(t)] || null; }}),
      backgroundColor: C[m],
      borderRadius: 4,
      borderColor: 'white',
      borderWidth: 1,
    }};
  }});
  new Chart(document.getElementById('perTaskBar'), {{
    type: 'bar',
    data: {{ labels: T.map(function(t) {{ return 'task' + String(t).padStart(3,'0'); }}), datasets: datasets }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ position: 'top' }} }},
      scales: {{
        y: {{ title: {{ display: true, text: 'Bytes' }}, beginAtZero: true, grid: {{ color: '#e2e8f0' }} }},
        x: {{ grid: {{ display: false }} }}
      }}
    }}
  }});
}})();

// ── 2. Median vs Mean bar ─────────────────────────────────────
(function() {{
  var labels = M.map(function(m) {{ return m; }});
  new Chart(document.getElementById('medianMean'), {{
    type: 'bar',
    data: {{
      labels: labels,
      datasets: [
        {{
          label: 'Median (bytes)',
          data: M.map(function(m) {{ return S[m].median; }}),
          backgroundColor: M.map(function(m) {{ return C[m]; }}),
          borderRadius: 4,
          borderColor: 'white',
          borderWidth: 1,
        }},
        {{
          label: 'Mean (bytes)',
          data: M.map(function(m) {{ return S[m].mean; }}),
          backgroundColor: M.map(function(m) {{ return C[m] + '99'; }}),
          borderRadius: 4,
          borderColor: 'white',
          borderWidth: 1,
        }}
      ]
    }},
    options: {{
      responsive: true,
      plugins: {{ legend: {{ position: 'top' }} }},
      scales: {{ y: {{ title: {{ display: true, text: 'Bytes' }}, beginAtZero: true, grid: {{ color: '#e2e8f0' }} }} }}
    }}
  }});
}})();

// ── 3. Win pie ────────────────────────────────────────────────
(function() {{
  new Chart(document.getElementById('winPie'), {{
    type: 'doughnut',
    data: {{
      labels: M.map(function(m) {{ return m + ' (' + W[m] + ' wins)'; }}),
      datasets: [{{
        data: M.map(function(m) {{ return W[m]; }}),
        backgroundColor: M.map(function(m) {{ return C[m]; }}),
        borderColor: 'white',
        borderWidth: 2,
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{
        legend: {{ position: 'bottom' }},
        title: {{ display: true, text: 'Total wins: ' + (W.comap + W.auto_pal + W.default) + ' (ties count for all)', font: {{ size: 13 }} }}
      }}
    }}
  }});
}})();

// ── 4. Heatmap ────────────────────────────────────────────────
(function() {{
  var matrix = M.map(function(m) {{
    return T.map(function(t) {{ return R[m][String(t)] || null; }});
  }});
  // Build color grid: normalize per column (task)
  var colors = M.map(function(m, mi) {{
    return T.map(function(t, ti) {{
      var vals = M.map(function(mm) {{ return R[mm][String(t)]; }}).filter(function(v) {{ return v != null; }});
      var min = Math.min.apply(null, vals);
      var max = Math.max.apply(null, vals);
      var v = R[m][String(t)];
      if (v == null) return 'rgba(0,0,0,0)';
      if (v === min) return C[m] + 'cc';
      var ratio = (v - min) / (max - min || 1);
      return 'rgba(200,200,200,' + (0.15 + ratio * 0.5) + ')';
    }});
  }});

  // Draw with custom plugin
  var labels = T.map(function(t) {{ return 'task' + String(t).padStart(3,'0'); }});
  var dataMatrix = matrix;

  new Chart(document.getElementById('heatmap'), {{
    type: 'matrix',
    data: {{
      datasets: [{{
        label: 'Bytes',
        data: (function() {{
          var points = [];
          for (var mi = 0; mi < M.length; mi++) {{
            for (var ti = 0; ti < T.length; ti++) {{
              if (dataMatrix[mi][ti] != null) {{
                points.push({{ x: ti, y: mi, v: dataMatrix[mi][ti] }});
              }}
            }}
          }}
          return points;
        }})(),
        backgroundColor: function(ctx) {{
          var ti = ctx.raw.x;
          var mi = ctx.raw.y;
          var vals = M.map(function(mm) {{ return R[mm][String(T[ti])]; }}).filter(function(v) {{ return v != null; }});
          var min = Math.min.apply(null, vals);
          var max = Math.max.apply(null, vals);
          var v = ctx.raw.v;
          if (v == null) return 'rgba(0,0,0,0)';
          if (v === min) return C[M[mi]] + 'dd';
          var ratio = (v - min) / (max - min || 1);
          var r = Math.round(148 + (1 - ratio) * 80);
          var g = Math.round(163 + (1 - ratio) * 56);
          return 'rgba(' + r + ',' + g + ',184,' + (0.3 + ratio * 0.5) + ')';
        }},
        borderColor: 'white',
        borderWidth: 2,
        borderRadius: 4,
        width: function(ctx) {{ return ctx.chart.chartArea ? (ctx.chart.chartArea.width / T.length) * 0.85 : 50; }},
        height: function(ctx) {{ return ctx.chart.chartArea ? (ctx.chart.chartArea.height / M.length) * 0.75 : 30; }},
      }}]
    }},
    options: {{
      responsive: true,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          callbacks: {{
            title: function(items) {{
              var item = items[0];
              return 'task' + String(T[item.raw.x]).padStart(3, '0') + ' — ' + M[item.raw.y];
            }},
            label: function(item) {{ return item.raw.v + ' bytes'; }}
          }}
        }}
      }},
      scales: {{
        x: {{
          type: 'category',
          labels: labels,
          ticks: {{ font: {{ size: 10 }} }},
          grid: {{ display: false }},
        }},
        y: {{
          type: 'category',
          labels: M,
          ticks: {{ font: {{ size: 10 }} }},
          grid: {{ display: false }},
          offset: true,
        }}
      }},
      layout: {{ padding: 4 }}
    }},
    plugins: [{{
      id: 'heatmapLabels',
      afterDraw: function(chart) {{
        var ctx = chart.ctx;
        var meta = chart.getDatasetMeta(0);
        ctx.font = 'bold 11px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.textAlign = 'center';
        ctx.textCoMAP = 'middle';
        meta.data.forEach(function(rect) {{
          if (rect.raw && rect.raw.v != null) {{
            // Find min per column
            var ti = rect.raw.x;
            var vals = M.map(function(mm) {{ return R[mm][String(T[ti])]; }}).filter(function(v) {{ return v != null; }});
            var min = Math.min.apply(null, vals);
            ctx.fillStyle = rect.raw.v === min ? '#166534' : '#475569';
            ctx.fillText(rect.raw.v + 'B', rect.x, rect.y);
          }}
        }});
      }}
    }}]
  }});
}})();

// ── 5. Results table ──────────────────────────────────────────
(function() {{
  var div = document.getElementById('resultsTable');
  var h = '<table><thead><tr><th>Task</th>';
  M.forEach(function(m) {{ h += '<th>' + m + '</th>'; }});
  h += '<th>Best Method</th></tr></thead><tbody>';

  T.forEach(function(t) {{
    h += '<tr><td><b>task' + String(t).padStart(3, '0') + '</b></td>';
    var vals = M.map(function(m) {{ return R[m][String(t)]; }});
    var best = Math.min.apply(null, vals.filter(function(v) {{ return v != null; }}));

    M.forEach(function(m) {{
      var v = R[m][String(t)];
      var cls = (v === best && vals.filter(function(x){{return x===v;}}).length === 1) ? 'badge badge-best' : '';
      var vStr = (v != null) ? v + 'B' : '—';
      if (cls) {{
        h += '<td><span class="' + cls + '">' + vStr + '</span></td>';
      }} else {{
        h += '<td>' + vStr + '</td>';
      }}
    }});

    var winners = M.filter(function(m) {{ return R[m][String(t)] === best; }});
    h += '<td>' + winners.join(' / ') + '</td></tr>';
  }});

  // Summary row
  h += '<tr style="border-top:2px solid #cbd5e1;font-weight:700;"><td>Wins</td>';
  M.forEach(function(m) {{ h += '<td>' + W[m] + '/10</td>'; }});
  h += '<td></td></tr>';
  h += '<tr style="font-weight:600;"><td>Median</td>';
  M.forEach(function(m) {{ h += '<td>' + S[m].median + 'B</td>'; }});
  h += '<td></td></tr>';
  h += '<tr style="font-weight:600;"><td>Mean</td>';
  M.forEach(function(m) {{ h += '<td>' + S[m].mean + 'B</td>'; }});
  h += '<td></td></tr>';
  h += '<tr style="font-weight:600;"><td>Range</td>';
  M.forEach(function(m) {{ h += '<td>' + S[m].min + '–' + S[m].max + 'B</td>'; }});
  h += '<td></td></tr>';
  h += '</tbody></table>';
  div.innerHTML = h;
}})();
</script>
</body>
</html>"""

# ── Write ──────────────────────────────────────────────────────
out_path = os.path.join(RESULTS_DIR, "plots", "dashboard.html")
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w") as f:
    f.write(html)
print(f"Saved: {out_path}")
print(f"Open: file://{out_path}")
