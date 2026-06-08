/* Chart.js renderers. Jillani SofTech. */
const FS_INK = "#6b7a90";

/* Plugin: draw the value on each doughnut slice + a total in the center. */
const FS_DoughnutLabels = {
  id: "fsDoughnutLabels",
  afterDraw(chart) {
    if (chart.config.type !== "doughnut") return;
    const { ctx } = chart;
    const meta = chart.getDatasetMeta(0);
    const data = chart.data.datasets[0].data;
    const total = data.reduce((a, b) => a + (Number(b) || 0), 0);

    ctx.save();
    // value on each slice
    ctx.font = "700 13px 'Plus Jakarta Sans', sans-serif";
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    meta.data.forEach((arc, i) => {
      if (!data[i]) return;
      const pos = arc.tooltipPosition();
      ctx.fillText(String(data[i]), pos.x, pos.y);
    });
    // total in the center
    const cx = meta.data.length ? meta.data[0].x : chart.width / 2;
    const cy = meta.data.length ? meta.data[0].y : chart.height / 2;
    ctx.fillStyle = "#0b1f3a";
    ctx.font = "800 24px 'Sora', sans-serif";
    ctx.fillText(String(total), cx, cy - 8);
    ctx.fillStyle = FS_INK;
    ctx.font = "600 11px 'Plus Jakarta Sans', sans-serif";
    ctx.fillText("DOCUMENTS", cx, cy + 12);
    ctx.restore();
  },
};

function fsRenderCharts(data) {
  const t = document.getElementById("trendChart");
  if (t) new Chart(t, { type: "line", data: { labels: data.compliance_trend.labels, datasets: [
        { label: "Compliance Score", data: data.compliance_trend.values, borderColor: "#1fae72", backgroundColor: "rgba(31,174,114,.12)", tension: .4, fill: true, borderWidth: 2 },
        { label: "Risk Score", data: data.risk_trend.values, borderColor: "#1d6fe0", backgroundColor: "rgba(29,111,224,.10)", tension: .4, fill: true, borderWidth: 2 } ] },
      options: { responsive: true, plugins: { legend: { labels: { color: FS_INK, usePointStyle: true } } }, scales: { y: { ticks: { color: FS_INK }, grid: { color: "#eef2f8" } }, x: { ticks: { color: FS_INK }, grid: { display: false } } } } });

  const c = document.getElementById("catChart");
  if (c) new Chart(c, {
      type: "doughnut",
      data: { labels: data.categories.labels, datasets: [{ data: data.categories.values, backgroundColor: ["#0b1f3a","#1d6fe0","#2e86ff","#1fae72","#8fb4e8","#c9d6ea"], borderWidth: 2, borderColor: "#fff" }] },
      options: { cutout: "60%", layout: { padding: 6 },
        plugins: { legend: { position: "bottom", labels: { color: FS_INK, usePointStyle: true, boxWidth: 8, padding: 12 } },
          tooltip: { callbacks: { label: (ctx) => ` ${ctx.label}: ${ctx.parsed} document(s)` } } } },
      plugins: [FS_DoughnutLabels] });

  const u = document.getElementById("usageChart");
  if (u) new Chart(u, { type: "bar", data: { labels: data.ai_usage.labels, datasets: [{ label: "AI Queries", data: data.ai_usage.values, backgroundColor: "#1d6fe0", borderRadius: 6, maxBarThickness: 28 }] },
      options: { plugins: { legend: { display: false } }, scales: { y: { ticks: { color: FS_INK }, grid: { color: "#eef2f8" } }, x: { ticks: { color: FS_INK }, grid: { display: false } } } } });
}
