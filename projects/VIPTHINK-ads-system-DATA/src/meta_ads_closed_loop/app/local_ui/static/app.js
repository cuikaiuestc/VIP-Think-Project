const state = {
  data: window.META_CLOSED_LOOP_DATA,
  selectedCampaignFilter: "all",
  selectedPriority: "all",
  selectedCampaignId: null,
  selectedAdsetId: null,
};

const money = (value, currency) => `${currency} ${Number(value).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const percent = (value) => `${Number(value || 0).toFixed(2)}%`;
const integer = (value) => Number(value || 0).toLocaleString("en-US");

function costPair(item) {
  const cpl = item.cpl === null || item.cpl === undefined ? "CPL -" : `CPL ${money(item.cpl, item.currency)}`;
  const cpa = item.cpa === null || item.cpa === undefined ? "CPA -" : `CPA ${money(item.cpa, item.currency)}`;
  return `${cpl} / ${cpa}`;
}

function emptyRow(colspan, message) {
  return `<tr><td colspan="${colspan}" class="empty-cell">${message}</td></tr>`;
}

function creativePreview(creative) {
  if (creative?.preview_url) {
    const label = creative.name || creative.title || creative.id || "creative_asset预览";
    return `<img class="creative-thumb" src="${creative.preview_url}" alt="${label}" loading="lazy" />`;
  }
  return `<span class="preview-empty">暂无图片预览</span>`;
}

function render() {
  const { snapshot, report } = state.data;
  document.getElementById("accountName").textContent = snapshot.account_name;
  const campaignObjectCount = snapshot.object_counts?.campaigns ?? snapshot.campaigns.length;
  document.getElementById("accountMeta").textContent = `${snapshot.currency} · ${snapshot.timezone} · 已读取 ${campaignObjectCount} 个 Campaign 对象`;
  document.getElementById("sourceLabel").textContent = snapshot.source;
  document.getElementById("updatedAt").textContent = snapshot.updated_at;

  renderMetrics();
  renderWorkflow();
  renderObjectSummary();
  renderCampaigns();
  renderDiagnostics();
  renderDrafts();
  renderBlockedLog();
  renderReport(report);
}

function renderObjectSummary() {
  const { accounts, snapshot } = state.data;
  document.getElementById("accountTable").innerHTML = accounts
    .map((item) => `
      <div class="mini-row">
        <strong>${item.name || "未命名账户"}</strong>
        <span>${item.currency || "-"} · ${item.timezone_name || "-"}</span>
      </div>
    `)
    .join("");
  const adsetRows = snapshot.adsets
    .slice(0, 8)
    .map((item) => `
      <div class="mini-row">
        <strong>${item.name}</strong>
        <span>${money(item.spend, item.currency)} · 线索 ${item.leads} · ${item.status}</span>
      </div>
    `)
    .join("");
  document.getElementById("adsetTable").innerHTML =
    adsetRows +
      (snapshot.adsets.length > 8 ? `<div class="mini-row"><strong>还有 ${snapshot.adsets.length - 8} 个 Ad Set</strong><span>表格视图后续展开</span></div>` : "") ||
    `<div class="mini-row"><strong>暂无 Ad Set 数据</strong><span>请检查 read-only 权限</span></div>`;
  const adRows = snapshot.ads
    .slice(0, 8)
    .map((item) => {
      const creativeName = item.creative?.name || item.creative?.title || item.creative?.id || "creative_asset信息待补齐";
      return `
        <div class="mini-row">
          ${creativePreview(item.creative)}
          <strong>${item.name}</strong>
          <span>${money(item.spend, item.currency)} · 点击 ${item.clicks} · LPV ${item.landing_page_views}</span>
          <small>creative_asset：${creativeName}</small>
        </div>
      `;
    })
    .join("");
  document.getElementById("adTable").innerHTML =
    adRows +
      (snapshot.ads.length > 8 ? `<div class="mini-row"><strong>还有 ${snapshot.ads.length - 8} 个 Ad</strong><span>表格视图后续展开</span></div>` : "") ||
    `<div class="mini-row"><strong>暂无广告数据</strong><span>请检查 read-only 权限</span></div>`;
}

function renderMetrics() {
  const { snapshot, diagnoses, drafts, blockedActions } = state.data;
  const items = [
    ["近 7 天消耗", money(snapshot.total_spend, snapshot.currency), "read-only"],
    ["账户", state.data.accounts.length, "可见投放账户"],
    ["Campaign", snapshot.object_counts?.campaigns ?? snapshot.campaigns.length, "已读取对象"],
    ["Ad Set", snapshot.object_counts?.adsets ?? snapshot.adsets.length, "已读取对象"],
    ["Ad", snapshot.object_counts?.ads ?? snapshot.ads.length, "已读取对象"],
    ["线索", snapshot.total_leads, "Meta 事件"],
    ["购买", snapshot.total_purchases, "Meta 事件"],
    ["LPV", snapshot.total_landing_page_views, "广告层汇总"],
    ["诊断", diagnoses.length, "待处理"],
    ["本地草稿", drafts.length, "不会写回 Meta"],
    ["Blocked", blockedActions.length, "危险动作"],
  ];
  document.getElementById("metricGrid").innerHTML = items
    .map(([label, value, note]) => `
      <article class="metric-card">
        <span>${label}</span>
        <strong>${value}</strong>
        <small>${note}</small>
      </article>
    `)
    .join("");
}

function renderWorkflow() {
  document.getElementById("workflowStrip").innerHTML = state.data.workflow
    .map((item, index) => `
      <div class="workflow-step">
        <span>${index + 1}</span>
        <strong>${item}</strong>
      </div>
    `)
    .join("");
}

function filteredCampaigns() {
  const riskIds = new Set(state.data.diagnoses.map((item) => item.object_id));
  return state.data.drilldown.campaigns.filter((item) => {
    if (state.selectedCampaignFilter === "active") return item.status === "ACTIVE";
    if (state.selectedCampaignFilter === "risk") return riskIds.has(item.id);
    return true;
  });
}

function ensureDrilldownSelection(campaigns) {
  if (!campaigns.length) {
    state.selectedCampaignId = null;
    state.selectedAdsetId = null;
    return { campaign: null, adset: null };
  }
  let campaign = campaigns.find((item) => item.id === state.selectedCampaignId);
  if (!campaign) {
    campaign = campaigns[0];
    state.selectedCampaignId = campaign.id;
  }
  let adset = campaign.adsets.find((item) => item.id === state.selectedAdsetId);
  if (!adset) {
    adset = campaign.adsets[0] || null;
    state.selectedAdsetId = adset?.id || null;
  }
  return { campaign, adset };
}

function renderCampaigns() {
  const campaigns = filteredCampaigns();
  ensureDrilldownSelection(campaigns);
  document.getElementById("campaignTable").innerHTML = campaigns
    .map((item) => `
      <tr class="${item.id === state.selectedCampaignId ? "selected-row" : ""}">
        <td>
          <button class="link-button" data-select-campaign="${item.id}">${item.name}</button>
          <small>${item.id}</small>
        </td>
        <td><span class="status-chip">${item.status}</span></td>
        <td>${money(item.spend, item.currency)}</td>
        <td>${integer(item.clicks)}</td>
        <td>${integer(item.landing_page_views)}</td>
        <td>${integer(item.leads)}</td>
        <td>${integer(item.purchases)}</td>
        <td>${percent(item.ctr)}</td>
        <td>${costPair(item)}</td>
        <td>${integer(item.adset_count)} Ad Set / ${integer(item.ad_count)} Ad</td>
        <td><button class="table-action" data-draft-campaign="${item.id}">生成草稿</button></td>
      </tr>
    `)
    .join("") || emptyRow(11, state.data.drilldown.empty_state);
  renderDrilldown(campaigns);
}

function renderDrilldown(campaigns) {
  const { campaign, adset } = ensureDrilldownSelection(campaigns);
  document.getElementById("selectedCampaignName").textContent = campaign?.name || "暂无 Campaign";
  document.getElementById("selectedCampaignMeta").textContent = campaign
    ? `${money(campaign.spend, campaign.currency)} · ${integer(campaign.adset_count)} 个 Ad Set · ${integer(campaign.ad_count)} 个 Ad`
    : "当前筛选无可下钻对象";

  document.getElementById("adsetDrilldownTable").innerHTML = (campaign?.adsets || [])
    .map((item) => `
      <tr class="${item.id === state.selectedAdsetId ? "selected-row" : ""}">
        <td>
          <button class="link-button" data-select-adset="${item.id}">${item.name}</button>
          <small>${item.id}</small>
        </td>
        <td><span class="status-chip">${item.status}</span></td>
        <td>${money(item.spend, item.currency)}</td>
        <td>${integer(item.clicks)}</td>
        <td>${integer(item.landing_page_views)}</td>
        <td>${integer(item.leads)}</td>
        <td>${integer(item.purchases)}</td>
        <td>${percent(item.ctr)}</td>
        <td>${costPair(item)}</td>
        <td>${integer(item.ad_count)}</td>
      </tr>
    `)
    .join("") || emptyRow(10, "所选 Campaign 在当前时间窗没有可见 Ad Set。");

  document.getElementById("selectedAdsetName").textContent = adset?.name || "暂无 Ad Set";
  document.getElementById("selectedAdsetMeta").textContent = adset
    ? `${money(adset.spend, adset.currency)} · ${integer(adset.ad_count)} 个 Ad · ${adset.status}`
    : "请选择有 Ad Set 的 Campaign";

  document.getElementById("adDrilldownTable").innerHTML = (adset?.ads || [])
    .map((item) => `
      <tr>
        <td>
          <strong>${item.name}</strong>
          <small>${item.id}</small>
        </td>
        <td>${creativePreview(item.creative)}</td>
        <td><span class="status-chip">${item.status}</span></td>
        <td>${money(item.spend, item.currency)}</td>
        <td>${integer(item.clicks)}</td>
        <td>${integer(item.landing_page_views)}</td>
        <td>${integer(item.leads)}</td>
        <td>${integer(item.purchases)}</td>
        <td>${percent(item.ctr)}</td>
        <td>${costPair(item)}</td>
      </tr>
    `)
    .join("") || emptyRow(10, "所选 Ad Set 在当前时间窗没有可见 Ad。");
}

function renderDiagnostics() {
  const diagnoses = state.data.diagnoses.filter((item) => state.selectedPriority === "all" || item.priority === state.selectedPriority);
  document.getElementById("diagnosisList").innerHTML = diagnoses
    .map((item) => `
      <article class="diagnosis-card">
        <div class="diagnosis-head">
          <span class="priority priority-${item.priority}">${item.priority}</span>
          <strong>${item.title}</strong>
          <small>${item.confidence}置信度</small>
        </div>
        <p>${item.object_name}</p>
        <ul>${item.evidence.map((evidence) => `<li>${evidence}</li>`).join("")}</ul>
        <div class="card-actions">
          <span>${item.suggested_action}</span>
          <button class="secondary-button" data-create-draft="${item.id}">生成草稿</button>
        </div>
      </article>
    `)
    .join("");
}

function renderDrafts() {
  document.getElementById("draftCount").textContent = `${state.data.drafts.length} 份`;
  document.getElementById("draftList").innerHTML = state.data.drafts
    .map((item) => `
      <article class="draft-card">
        <div>
          <span class="status-chip">${item.status}</span>
          <h4>${item.title}</h4>
        </div>
        <pre>${item.body}</pre>
      </article>
    `)
    .join("");
}

function renderBlockedLog() {
  const log = document.getElementById("blockedLog");
  log.innerHTML = state.data.blockedActions
    .map((item) => `
      <div class="blocked-row">
        <span>blocked</span>
        <strong>${item.action}</strong>
        <p>${item.object_type} ${item.object_id}</p>
        <small>${item.reason}</small>
      </div>
    `)
    .join("");
}

function renderReport(report) {
  document.getElementById("reportSummary").textContent = report.summary;
  const items = [
    ["数据源", report.source],
    ["更新时间", report.updated_at],
    ["诊断数", report.diagnosis_count],
    ["草稿数", report.draft_count],
    ["阻断数", report.blocked_action_count],
  ];
  document.getElementById("reportGrid").innerHTML = items
    .map(([label, value]) => `
      <div>
        <span>${label}</span>
        <strong>${value}</strong>
      </div>
    `)
    .join("");
}

function showSection(id) {
  document.querySelectorAll(".panel-section").forEach((section) => section.classList.toggle("active-section", section.id === id));
  document.querySelectorAll(".nav-item").forEach((button) => button.classList.toggle("active", button.dataset.target === id));
}

function createDraft(diagnosisId) {
  const diagnosis = state.data.diagnoses.find((item) => item.id === diagnosisId) || state.data.diagnoses[0];
  if (!diagnosis) return;
  const nextDraft = {
    id: `draft-ui-${Date.now()}`,
    diagnosis_id: diagnosis.id,
    object_type: diagnosis.object_type,
    object_id: diagnosis.object_id,
    object_name: diagnosis.object_name,
    title: `${diagnosis.object_name}：${diagnosis.title}`,
    body: `建议动作：${diagnosis.suggested_action}\n证据：${diagnosis.evidence.join("；")}\n安全边界：本草稿只保存在本地，不会调用 Meta 写接口。`,
    status: "本地草稿",
    created_at: new Date().toISOString(),
  };
  state.data.drafts.unshift(nextDraft);
  state.data.report.draft_count = state.data.drafts.length;
  state.data.report.summary = `已读取 ${state.data.snapshot.account_name} 的只读数据，发现 ${state.data.diagnoses.length} 条诊断，生成 ${state.data.drafts.length} 份本地草稿，阻断 ${state.data.blockedActions.length} 次危险写动作。`;
  renderDrafts();
  renderMetrics();
  renderReport(state.data.report);
  showSection("drafts");
}

function blockDangerousAction(action = "pause") {
  const campaign = state.data.snapshot.campaigns[0];
  state.data.blockedActions.unshift({
    action,
    object_type: "Campaign",
    object_id: campaign.id,
    reason: "Meta/Facebook API 在本项目中只允许 read-only；该真实写操作已被阻断。",
    created_at: new Date().toISOString(),
  });
  state.data.report.blocked_action_count = state.data.blockedActions.length;
  state.data.report.summary = `已读取 ${state.data.snapshot.account_name} 的只读数据，发现 ${state.data.diagnoses.length} 条诊断，生成 ${state.data.drafts.length} 份本地草稿，阻断 ${state.data.blockedActions.length} 次危险写动作。`;
  renderBlockedLog();
  renderMetrics();
  renderReport(state.data.report);
  showSection("safety");
}

document.addEventListener("click", (event) => {
  const nav = event.target.closest("[data-target]");
  if (nav) showSection(nav.dataset.target);

  const selectCampaign = event.target.closest("[data-select-campaign]");
  if (selectCampaign) {
    state.selectedCampaignId = selectCampaign.dataset.selectCampaign;
    state.selectedAdsetId = null;
    renderCampaigns();
  }

  const selectAdset = event.target.closest("[data-select-adset]");
  if (selectAdset) {
    state.selectedAdsetId = selectAdset.dataset.selectAdset;
    renderCampaigns();
  }

  const draftButton = event.target.closest("[data-create-draft]");
  if (draftButton) createDraft(draftButton.dataset.createDraft);

  const campaignDraft = event.target.closest("[data-draft-campaign]");
  if (campaignDraft) {
    const diagnosis = state.data.diagnoses.find((item) => item.object_id === campaignDraft.dataset.draftCampaign);
    createDraft(diagnosis?.id);
  }

  const openDiagnosis = event.target.closest("[data-open-diagnosis]");
  if (openDiagnosis) {
    state.selectedPriority = "all";
    document.getElementById("priorityFilter").value = "all";
    showSection("diagnostics");
  }
});

document.getElementById("draftPrimary").addEventListener("click", () => createDraft(state.data.diagnoses[0]?.id));
document.getElementById("simulateDanger").addEventListener("click", () => blockDangerousAction("pause"));
document.getElementById("refreshButton").addEventListener("click", () => render());
document.getElementById("copyReport").addEventListener("click", async () => {
  await navigator.clipboard?.writeText(state.data.report.summary);
  document.getElementById("copyReport").textContent = "已复制";
  setTimeout(() => {
    document.getElementById("copyReport").textContent = "复制复盘摘要";
  }, 1200);
});
document.getElementById("priorityFilter").addEventListener("change", (event) => {
  state.selectedPriority = event.target.value;
  renderDiagnostics();
});
document.querySelectorAll(".segment").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".segment").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.selectedCampaignFilter = button.dataset.filter;
    renderCampaigns();
  });
});

render();
