// RazorGuard AI - Frontend Controller

let benchmarkData = null;
let thresholdChart = null;
let networkGraph = null;
let allTransactions = [];
let allDisputes = [];

// Initialize on Load
document.addEventListener("DOMContentLoaded", async () => {
  if (window.lucide) {
    lucide.createIcons();
  }

  await loadOverviewStats();
  await loadRecentTransactions();
  await loadBenchmarkMetrics();
  await loadDisputes();
  await loadAbuseRings();

  // Run initial simulation
  runSimulation();
});

// ----------------- Navigation -----------------
function switchTab(tabId) {
  document.querySelectorAll(".tab-content").forEach(el => el.classList.add("hidden"));
  const target = document.getElementById(`tab-${tabId}`);
  if (target) {
    target.classList.remove("hidden");
  }

  document.querySelectorAll(".nav-tab").forEach(btn => {
    if (btn.dataset.tab === tabId) {
      btn.classList.add("bg-blue-600", "text-white", "shadow");
      btn.classList.remove("text-slate-400");
    } else {
      btn.classList.remove("bg-blue-600", "text-white", "shadow");
      btn.classList.add("text-slate-400");
    }
  });

  if (tabId === "benchmark" && benchmarkData && !thresholdChart) {
    initThresholdChart(benchmarkData.threshold_analysis);
  }

  if (tabId === "abuse-rings" && !networkGraph) {
    loadAbuseRings();
  }

  if (window.lucide) {
    lucide.createIcons();
  }
}

// ----------------- Overview Stats -----------------
async function loadOverviewStats() {
  try {
    const res = await fetch("/api/v1/overview-stats");
    const data = await res.json();

    document.getElementById("stat-total-txns").innerText = data.total_scanned_transactions;
    document.getElementById("stat-loss-prevented").innerText = `₹${data.prevented_loss_inr.toLocaleString("en-IN")}`;
    document.getElementById("stat-disputes-rate").innerText = `${data.auto_defense_rate_pct}%`;
  } catch (err) {
    console.error("Error loading overview stats:", err);
  }
}

// ----------------- Transactions Loader -----------------
async function loadRecentTransactions() {
  try {
    const res = await fetch("/api/v1/transactions?limit=25");
    allTransactions = await res.json();

    const tbody = document.getElementById("overview-transactions-tbody");
    const fullTbody = document.getElementById("full-transactions-tbody");

    if (allTransactions.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" class="py-6 text-center text-slate-500 font-sans">No transactions recorded yet.</td></tr>`;
      return;
    }

    // Populate Overview Table
    tbody.innerHTML = allTransactions.slice(0, 7).map(t => `
      <tr class="hover:bg-slate-900/50 transition">
        <td class="py-3 px-3 font-semibold text-blue-400">${t.txn_id}</td>
        <td class="py-3 px-3 text-slate-200">₹${t.amount.toLocaleString("en-IN")}</td>
        <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-sans">${t.payment_mode}</span></td>
        <td class="py-3 px-3 font-bold ${getScoreColorClass(t.risk_score)}">${t.risk_score}</td>
        <td class="py-3 px-3">${getActionBadge(t.action)}</td>
        <td class="py-3 px-3 text-slate-400 font-sans truncate max-w-[200px]" title="${t.risk_narrative}">${t.top_risk_drivers[0]?.feature || "Normal baseline"}</td>
      </tr>
    `).join("");

    // Populate Full Explorer Table
    renderFullTransactions(allTransactions);

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error("Error loading transactions:", err);
  }
}

function renderFullTransactions(txns) {
  const fullTbody = document.getElementById("full-transactions-tbody");
  if (!fullTbody) return;

  fullTbody.innerHTML = txns.map(t => `
    <tr class="hover:bg-slate-900/50 transition">
      <td class="py-3 px-3 font-semibold text-blue-400">${t.txn_id}</td>
      <td class="py-3 px-3 text-slate-400 font-sans">${t.customer_id}</td>
      <td class="py-3 px-3 text-slate-200">₹${t.amount.toLocaleString("en-IN")}</td>
      <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-sans">${t.payment_mode}</span></td>
      <td class="py-3 px-3 text-slate-400 font-sans">${t.delivery_city || "Domestic"}</td>
      <td class="py-3 px-3 font-bold ${getScoreColorClass(t.risk_score)}">${t.risk_score}</td>
      <td class="py-3 px-3"><span class="px-2 py-0.5 rounded text-xs font-bold ${getTierBadgeClass(t.risk_tier)}">${t.risk_tier}</span></td>
      <td class="py-3 px-3">${getActionBadge(t.action)}</td>
    </tr>
  `).join("");
}

function filterTransactions(tier) {
  document.querySelectorAll(".txn-filter-btn").forEach(btn => {
    if (btn.innerText.trim() === tier) {
      btn.classList.add("bg-blue-600", "text-white");
      btn.classList.remove("bg-slate-800", "text-slate-300");
    } else {
      btn.classList.remove("bg-blue-600", "text-white");
      btn.classList.add("bg-slate-800", "text-slate-300");
    }
  });

  if (tier === "ALL") {
    renderFullTransactions(allTransactions);
  } else {
    const filtered = allTransactions.filter(t => t.risk_tier === tier);
    renderFullTransactions(filtered);
  }
}

// ----------------- Live Simulator -----------------
async function runSimulation() {
  const payload = {
    amount: parseFloat(document.getElementById("sim-amount").value) || 2000,
    payment_mode: document.getElementById("sim-payment-mode").value,
    item_category: document.getElementById("sim-category").value,
    txn_velocity_1h: parseInt(document.getElementById("sim-velocity-1h").value) || 1,
    txn_velocity_24h: parseInt(document.getElementById("sim-velocity-1h").value) + 2,
    user_account_age_days: parseInt(document.getElementById("sim-account-age").value) || 90,
    historical_rto_rate: parseFloat(document.getElementById("sim-rto-rate").value) || 0.05,
    ip_country: document.getElementById("sim-ip-country").value,
    ip_delivery_distance_km: parseFloat(document.getElementById("sim-distance").value) || 10,
    historical_dispute_count: parseInt(document.getElementById("sim-disputes").value) || 0,
    is_vpn_or_proxy: document.getElementById("sim-vpn").checked,
    card_bin_country_match: document.getElementById("sim-card-match").checked,
    device_fingerprint_entropy: document.getElementById("sim-vpn").checked ? 0.35 : 0.88,
    failed_attempts_before_success: 0
  };

  try {
    const res = await fetch("/api/v1/risk/score", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    displaySimulationResult(data);
    await loadOverviewStats();
    await loadRecentTransactions();
  } catch (err) {
    console.error("Simulation error:", err);
  }
}

function displaySimulationResult(res) {
  const scoreVal = document.getElementById("sim-score-value");
  const verdictTier = document.getElementById("sim-verdict-tier");
  const actionPill = document.getElementById("sim-action-pill");
  const gaugeCircle = document.getElementById("sim-gauge-circle");
  const driversList = document.getElementById("sim-drivers-list");
  const narrativeBox = document.getElementById("sim-narrative");

  scoreVal.innerText = res.risk_score;
  verdictTier.innerText = `${res.risk_tier} RISK`;
  actionPill.innerText = `ACTION: ${res.action}`;
  narrativeBox.innerText = res.risk_narrative;

  // Colors
  if (res.risk_tier === "LOW") {
    verdictTier.className = "px-2.5 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
    actionPill.className = "mt-4 px-4 py-1.5 rounded-xl font-mono text-sm font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
    gaugeCircle.className = "w-32 h-32 rounded-full border-8 border-emerald-500/80 flex items-center justify-center glow-emerald";
  } else if (res.risk_tier === "MEDIUM") {
    verdictTier.className = "px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30";
    actionPill.className = "mt-4 px-4 py-1.5 rounded-xl font-mono text-sm font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20";
    gaugeCircle.className = "w-32 h-32 rounded-full border-8 border-amber-500/80 flex items-center justify-center glow-amber";
  } else if (res.risk_tier === "HIGH") {
    verdictTier.className = "px-2.5 py-0.5 rounded-full text-xs font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30";
    actionPill.className = "mt-4 px-4 py-1.5 rounded-xl font-mono text-sm font-bold bg-orange-500/10 text-orange-400 border border-orange-500/20";
    gaugeCircle.className = "w-32 h-32 rounded-full border-8 border-orange-500/80 flex items-center justify-center glow-amber";
  } else {
    verdictTier.className = "px-2.5 py-0.5 rounded-full text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30";
    actionPill.className = "mt-4 px-4 py-1.5 rounded-xl font-mono text-sm font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20";
    gaugeCircle.className = "w-32 h-32 rounded-full border-8 border-rose-500/80 flex items-center justify-center glow-rose";
  }

  // Explainability factors
  driversList.innerHTML = res.top_risk_drivers.map(d => {
    let badgeColor = d.impact === "POSITIVE" ? "text-emerald-400 bg-emerald-950/60 border-emerald-800" :
                     d.impact === "NEGATIVE" ? "text-rose-400 bg-rose-950/60 border-rose-800" :
                     "text-slate-400 bg-slate-900 border-slate-800";
    return `
      <div class="p-2.5 rounded-lg ${badgeColor} border text-xs flex items-start space-x-2">
        <i data-lucide="${d.impact === 'POSITIVE' ? 'shield-check' : 'alert-circle'}" class="w-4 h-4 shrink-0 mt-0.5"></i>
        <div>
          <strong class="font-semibold block">${d.feature}</strong>
          <span class="text-slate-300">${d.description}</span>
        </div>
      </div>
    `;
  }).join("");

  if (window.lucide) lucide.createIcons();
}

function loadPreset(preset) {
  if (preset === "safe_upi") {
    document.getElementById("sim-amount").value = 1450;
    document.getElementById("sim-payment-mode").value = "UPI";
    document.getElementById("sim-category").value = "GROCERY";
    document.getElementById("sim-velocity-1h").value = 1;
    document.getElementById("sim-account-age").value = 340;
    document.getElementById("sim-rto-rate").value = 0.02;
    document.getElementById("sim-ip-country").value = "IN";
    document.getElementById("sim-distance").value = 8;
    document.getElementById("sim-disputes").value = 0;
    document.getElementById("sim-vpn").checked = false;
    document.getElementById("sim-card-match").checked = true;
  } else if (preset === "stolen_card") {
    document.getElementById("sim-amount").value = 68000;
    document.getElementById("sim-payment-mode").value = "CREDIT_CARD";
    document.getElementById("sim-category").value = "ELECTRONICS";
    document.getElementById("sim-velocity-1h").value = 6;
    document.getElementById("sim-account-age").value = 2;
    document.getElementById("sim-rto-rate").value = 0.10;
    document.getElementById("sim-ip-country").value = "US";
    document.getElementById("sim-distance").value = 1800;
    document.getElementById("sim-disputes").value = 1;
    document.getElementById("sim-vpn").checked = true;
    document.getElementById("sim-card-match").checked = false;
  } else if (preset === "cod_rto") {
    document.getElementById("sim-amount").value = 12500;
    document.getElementById("sim-payment-mode").value = "COD";
    document.getElementById("sim-category").value = "APPAREL";
    document.getElementById("sim-velocity-1h").value = 3;
    document.getElementById("sim-account-age").value = 12;
    document.getElementById("sim-rto-rate").value = 0.85;
    document.getElementById("sim-ip-country").value = "IN";
    document.getElementById("sim-distance").value = 120;
    document.getElementById("sim-disputes").value = 0;
    document.getElementById("sim-vpn").checked = false;
    document.getElementById("sim-card-match").checked = true;
  }

  runSimulation();
}

// ----------------- Benchmark Metrics & False Positive Economics -----------------
async function loadBenchmarkMetrics() {
  try {
    const res = await fetch("/api/v1/benchmark/metrics");
    benchmarkData = await res.json();

    const hm = benchmarkData.held_out_metrics;
    const cm = hm.confusion_matrix;
    const ue = benchmarkData.unit_economics;

    document.getElementById("stat-precision").innerText = `${hm.precision}%`;
    document.getElementById("stat-fpr").innerText = `${hm.false_positive_rate}%`;

    document.getElementById("bm-precision").innerText = `${hm.precision}%`;
    document.getElementById("bm-recall").innerText = `${hm.recall}%`;
    document.getElementById("bm-f1").innerText = `${hm.f1_score}%`;
    document.getElementById("bm-auc").innerText = hm.roc_auc.toFixed(4);
    document.getElementById("bm-fpr").innerText = `${hm.false_positive_rate}%`;
    document.getElementById("bm-net-value").innerText = `₹${(ue.net_savings_inr / 100000).toFixed(2)}L`;

    document.getElementById("cm-tp").innerText = cm.tp;
    document.getElementById("cm-fp").innerText = cm.fp;
    document.getElementById("cm-fn").innerText = cm.fn;
    document.getElementById("cm-tn").innerText = cm.tn.toLocaleString();

    initThresholdChart(benchmarkData.threshold_analysis);
  } catch (err) {
    console.error("Error loading benchmark:", err);
  }
}

function updateThresholdStats(val) {
  const tVal = parseFloat(val);
  document.getElementById("slider-thresh-label").innerText = tVal.toFixed(2);

  if (!benchmarkData || !benchmarkData.threshold_analysis) return;

  const row = benchmarkData.threshold_analysis.reduce((prev, curr) => {
    return (Math.abs(curr.threshold - tVal) < Math.abs(prev.threshold - tVal) ? curr : prev);
  });

  document.getElementById("dyn-gross-saved").innerText = `₹${row.gross_saved_inr.toLocaleString("en-IN")}`;
  document.getElementById("dyn-fp-cost").innerText = `₹${row.fp_cost_inr.toLocaleString("en-IN")}`;
  document.getElementById("dyn-net-margin").innerText = `₹${row.net_benefit_inr.toLocaleString("en-IN")}`;
  document.getElementById("dyn-tp-count").innerText = row.tp;
  document.getElementById("dyn-fp-count").innerText = row.fp;
}

function initThresholdChart(analysis) {
  const ctx = document.getElementById("thresholdCurveChart");
  if (!ctx) return;

  const labels = analysis.map(a => a.threshold.toFixed(2));
  const precisions = analysis.map(a => a.precision);
  const recalls = analysis.map(a => a.recall);
  const f1Scores = analysis.map(a => a.f1_score);

  if (thresholdChart) {
    thresholdChart.destroy();
  }

  thresholdChart = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Precision (%)",
          data: precisions,
          borderColor: "#38bdf8",
          backgroundColor: "#38bdf8",
          tension: 0.3,
          borderWidth: 2
        },
        {
          label: "Recall (%)",
          data: recalls,
          borderColor: "#34d399",
          backgroundColor: "#34d399",
          tension: 0.3,
          borderWidth: 2
        },
        {
          label: "F1 Score (%)",
          data: f1Scores,
          borderColor: "#818cf8",
          backgroundColor: "#818cf8",
          tension: 0.3,
          borderWidth: 2,
          borderDash: [5, 5]
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: {
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#94a3b8", font: { family: "'JetBrains Mono'" } }
        },
        y: {
          min: 80,
          max: 100,
          grid: { color: "rgba(255, 255, 255, 0.05)" },
          ticks: { color: "#94a3b8", font: { family: "'JetBrains Mono'" } }
        }
      },
      plugins: {
        legend: {
          labels: { color: "#cbd5e1" }
        }
      }
    }
  });
}

// ----------------- Disputes & Auto-Responder -----------------
async function loadDisputes() {
  try {
    const res = await fetch("/api/v1/disputes");
    allDisputes = await res.json();

    const container = document.getElementById("disputes-list-container");
    if (allDisputes.length === 0) {
      container.innerHTML = `<div class="p-4 text-center text-slate-500">No active chargeback disputes.</div>`;
      return;
    }

    container.innerHTML = allDisputes.map((d, idx) => `
      <div onclick="selectDispute(${idx})" class="p-4 rounded-xl glass-panel glass-panel-hover border border-slate-800 cursor-pointer space-y-2">
        <div class="flex items-center justify-between">
          <span class="font-mono font-bold text-cyan-400 text-xs">${d.dispute_id}</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">AUTO-DEFENDED</span>
        </div>
        <div class="flex items-center justify-between text-xs">
          <span class="text-slate-300 font-semibold">₹${d.amount.toLocaleString("en-IN")}</span>
          <span class="text-slate-400">${d.customer_name}</span>
        </div>
        <p class="text-[11px] text-slate-400 truncate">${d.dispute_reason}</p>
      </div>
    `).join("");

    // Select first dispute
    if (allDisputes.length > 0) {
      selectDispute(0);
    }
  } catch (err) {
    console.error("Error loading disputes:", err);
  }
}

function selectDispute(idx) {
  const d = allDisputes[idx];
  if (!d) return;

  const previewBox = document.getElementById("dossier-preview-box");
  const winProbBadge = document.getElementById("dossier-win-prob");

  if (d.defense_data && d.defense_data.markdown_defense_letter) {
    previewBox.innerText = d.defense_data.markdown_defense_letter;
    winProbBadge.innerText = `${d.defense_data.win_probability_pct}% Win Prob`;
  } else {
    previewBox.innerText = `Evidence dossier being compiled...`;
  }
}

function copyDossierText() {
  const text = document.getElementById("dossier-preview-box").innerText;
  navigator.clipboard.writeText(text).then(() => {
    alert("Dossier copied to clipboard! Ready to submit to acquiring bank.");
  });
}

// ----------------- Abuse Ring Sentinel Network Graph -----------------
async function loadAbuseRings() {
  try {
    const res = await fetch("/api/v1/abuse-rings");
    const data = await res.json();

    // Render cluster list
    const clusterContainer = document.getElementById("abuse-clusters-list");
    clusterContainer.innerHTML = data.clusters.map(c => `
      <div class="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2">
        <div class="flex items-center justify-between">
          <span class="font-bold text-white">${c.name}</span>
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${c.risk_level === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' : 'bg-amber-500/20 text-amber-400 border border-amber-500/30'}">${c.risk_level}</span>
        </div>
        <p class="text-slate-400">${c.primary_vector}</p>
        <div class="flex items-center justify-between pt-1 text-slate-300 font-mono">
          <span>Exposure: ₹${c.total_loss_at_risk.toLocaleString("en-IN")}</span>
          <span class="text-blue-400">${c.confidence_score}% Confidence</span>
        </div>
        <div class="mt-2 p-2 rounded bg-slate-950 text-slate-400 text-[11px] font-sans">
          <strong>Action:</strong> ${c.recommended_action}
        </div>
      </div>
    `).join("");

    // Render Network Graph with Vis.js
    const container = document.getElementById("network-graph-container");
    if (!container) return;

    const graphData = {
      nodes: new vis.DataSet(data.network_graph.nodes),
      edges: new vis.DataSet(data.network_graph.edges)
    };

    const options = {
      nodes: {
        shape: "dot",
        font: { color: "#cbd5e1", size: 11, face: "Plus Jakarta Sans" },
        borderWidth: 2,
        borderColor: "#ffffff"
      },
      edges: {
        color: { color: "#475569", highlight: "#38bdf8" },
        font: { color: "#64748b", size: 9 },
        smooth: { type: "continuous" }
      },
      physics: {
        stabilization: true,
        barnesHut: {
          gravitationalConstant: -3000,
          springLength: 85
        }
      },
      interaction: { hover: true }
    };

    if (networkGraph) {
      networkGraph.destroy();
    }
    networkGraph = new vis.Network(container, graphData, options);

  } catch (err) {
    console.error("Error loading abuse rings:", err);
  }
}

// ----------------- UI Helpers -----------------
function getScoreColorClass(score) {
  if (score < 30) return "text-emerald-400";
  if (score < 60) return "text-amber-400";
  if (score < 85) return "text-orange-400";
  return "text-rose-400";
}

function getTierBadgeClass(tier) {
  if (tier === "LOW") return "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
  if (tier === "MEDIUM") return "bg-amber-500/20 text-amber-400 border border-amber-500/30";
  if (tier === "HIGH") return "bg-orange-500/20 text-orange-400 border border-orange-500/30";
  return "bg-rose-500/20 text-rose-400 border border-rose-500/30";
}

function getActionBadge(action) {
  if (action === "ALLOW") {
    return `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-mono">ALLOW</span>`;
  }
  if (action === "STEP_UP_2FA") {
    return `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30 font-mono">STEP-UP 2FA</span>`;
  }
  if (action === "MANUAL_REVIEW") {
    return `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-orange-500/20 text-orange-400 border border-orange-500/30 font-mono">REVIEW</span>`;
  }
  return `<span class="px-2 py-0.5 rounded text-[11px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30 font-mono">BLOCK</span>`;
}
