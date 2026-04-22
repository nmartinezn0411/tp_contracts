const state = {
  records: [],
  filtered: [],
  selectedId: null,
};

const els = {
  metricsGrid: document.querySelector("#metrics-grid"),
  projectBreakdown: document.querySelector("#project-breakdown"),
  flagBreakdown: document.querySelector("#flag-breakdown"),
  casesBody: document.querySelector("#cases-body"),
  visibleCount: document.querySelector("#visible-count"),
  lastUpdated: document.querySelector("#last-updated"),
  detailTitle: document.querySelector("#detail-title"),
  detailSummary: document.querySelector("#detail-summary"),
  detailAnalysis: document.querySelector("#detail-analysis"),
  searchInput: document.querySelector("#search-input"),
  statusFilter: document.querySelector("#status-filter"),
  projectFilter: document.querySelector("#project-filter"),
  flagFilter: document.querySelector("#flag-filter"),
};

const currency = new Intl.NumberFormat("es-DO", {
  style: "currency",
  currency: "USD",
  maximumFractionDigits: 0,
});

const integer = new Intl.NumberFormat("es-DO");

init();

async function init() {
  bindFilters();

  try {
    const response = await fetch("/api/billing-validation", { credentials: "same-origin" });
    if (!response.ok) {
      throw new Error(`Error ${response.status}`);
    }

    const data = await response.json();
    state.records = Array.isArray(data) ? data : [];
    populateProjects();
    applyFilters();
    els.lastUpdated.textContent = `Actualizado con ${integer.format(state.records.length)} registros`;
  } catch (error) {
    els.lastUpdated.textContent = "No se pudieron cargar los datos";
    els.casesBody.innerHTML = `<tr><td colspan="6"><div class="empty-state">Error cargando el dashboard. Verifica la sesion o el archivo JSON.</div></td></tr>`;
  }
}

function bindFilters() {
  [els.searchInput, els.statusFilter, els.projectFilter, els.flagFilter].forEach((element) => {
    element.addEventListener("input", applyFilters);
    element.addEventListener("change", applyFilters);
  });
}

function populateProjects() {
  const projects = [...new Set(state.records.map((item) => item.Project).filter(Boolean))].sort();
  els.projectFilter.innerHTML = `<option value="ALL">Todos</option>${projects
    .map((project) => `<option value="${escapeHtml(project)}">${escapeHtml(project)}</option>`)
    .join("")}`;
}

function applyFilters() {
  const search = els.searchInput.value.trim().toLowerCase();
  const status = els.statusFilter.value;
  const project = els.projectFilter.value;
  const flag = els.flagFilter.value;

  state.filtered = state.records.filter((record) => {
    const matchesSearch =
      !search ||
      [record.Employee_Name, record.Project, String(record.Employee_ID)]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(search);

    const matchesStatus = status === "ALL" || record.Status === status;
    const matchesProject = project === "ALL" || record.Project === project;
    const matchesFlag = flag === "ALL" || Boolean(record[flag]);

    return matchesSearch && matchesStatus && matchesProject && matchesFlag;
  });

  if (!state.filtered.some((item) => item.Employee_ID === state.selectedId)) {
    state.selectedId = state.filtered[0]?.Employee_ID ?? null;
  }

  renderMetrics();
  renderBreakdowns();
  renderTable();
  renderDetail();
}

function renderMetrics() {
  const total = state.filtered.length;
  const errors = state.filtered.filter((item) => item.Status === "ERROR").length;
  const oks = state.filtered.filter((item) => item.Status === "OK").length;
  const overbilling = state.filtered.filter((item) => item.Overbilling).length;
  const revenueImpact = state.filtered.reduce(
    (sum, item) => sum + Math.max(0, Number(item.Actual_Billing) - Number(item.Expected_Billing)),
    0
  );

  const cards = [
    {
      label: "Casos visibles",
      value: integer.format(total),
      context: "Registros actualmente incluidos por los filtros.",
    },
    {
      label: "Errores detectados",
      value: integer.format(errors),
      context: total ? `${Math.round((errors / total) * 100)}% del universo filtrado.` : "Sin datos para calcular.",
    },
    {
      label: "Casos correctos",
      value: integer.format(oks),
      context: "Registros sin discrepancias activas.",
    },
    {
      label: "Sobrefacturacion",
      value: integer.format(overbilling),
      context: "Casos donde la facturacion real supera la esperada.",
    },
    {
      label: "Impacto economico",
      value: currency.format(revenueImpact),
      context: "Exceso acumulado identificado antes del envio al cliente.",
    },
  ];

  els.metricsGrid.innerHTML = cards
    .map(
      (card) => `
        <article class="metric-card">
          <p class="metric-label">${card.label}</p>
          <p class="metric-value">${card.value}</p>
          <p class="metric-context">${card.context}</p>
        </article>
      `
    )
    .join("");
}

function renderBreakdowns() {
  const projectCounts = summarizeCounts(
    state.filtered.filter((item) => item.Status === "ERROR"),
    (item) => item.Project || "Sin proyecto"
  );
  renderBarList(els.projectBreakdown, projectCounts, "No hay errores para mostrar.");

  const flagCounts = [
    ["Tarifa incorrecta", state.filtered.filter((item) => item.Rate_Mismatch).length],
    ["Horas inconsistentes", state.filtered.filter((item) => item.Hours_Mismatch).length],
    ["Exceso de horas", state.filtered.filter((item) => item.Exceeds_Max_Hours).length],
    ["Sobrefacturacion", state.filtered.filter((item) => item.Overbilling).length],
  ].filter(([, count]) => count > 0);

  renderBarList(els.flagBreakdown, flagCounts, "No se detectan discrepancias en la vista actual.");
}

function summarizeCounts(items, getKey) {
  const counts = new Map();
  items.forEach((item) => {
    const key = getKey(item);
    counts.set(key, (counts.get(key) || 0) + 1);
  });

  return [...counts.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5);
}

function renderBarList(container, items, emptyMessage) {
  if (!items.length) {
    container.innerHTML = `<div class="empty-state">${emptyMessage}</div>`;
    return;
  }

  const max = Math.max(...items.map(([, value]) => value), 1);
  container.innerHTML = items
    .map(
      ([label, value]) => `
        <div class="bar-row">
          <div class="bar-meta">
            <strong>${escapeHtml(label)}</strong>
            <span>${integer.format(value)}</span>
          </div>
          <div class="bar-track">
            <div class="bar-fill" style="width:${(value / max) * 100}%"></div>
          </div>
        </div>
      `
    )
    .join("");
}

function renderTable() {
  els.visibleCount.textContent = integer.format(state.filtered.length);

  if (!state.filtered.length) {
    els.casesBody.innerHTML = `<tr><td colspan="6"><div class="empty-state">No hay registros que coincidan con los filtros seleccionados.</div></td></tr>`;
    return;
  }

  els.casesBody.innerHTML = state.filtered
    .map((record) => {
      const delta = Number(record.Actual_Billing) - Number(record.Expected_Billing);
      const isActive = state.selectedId === record.Employee_ID;
      return `
        <tr class="${isActive ? "active" : ""}" data-id="${record.Employee_ID}">
          <td>
            <span class="status-pill ${record.Status === "ERROR" ? "status-error" : "status-ok"}">${escapeHtml(
        record.Status
      )}</span>
          </td>
          <td>
            <span class="employee-name">${escapeHtml(record.Employee_Name)}</span>
            <span class="employee-meta">ID ${escapeHtml(String(record.Employee_ID))}</span>
          </td>
          <td>${escapeHtml(record.Project)}</td>
          <td>${integer.format(record.Hours_Worked)} trabajadas / ${integer.format(record.Hours_Billed)} facturadas</td>
          <td>${currency.format(record.Rate_Charged)} / ${currency.format(record.Rate_per_Hour)}</td>
          <td class="${delta > 0 ? "impact-strong" : "impact-soft"}">${formatDelta(delta)}</td>
        </tr>
      `;
    })
    .join("");

  [...els.casesBody.querySelectorAll("tr[data-id]")].forEach((row) => {
    row.addEventListener("click", () => {
      state.selectedId = Number(row.dataset.id);
      renderTable();
      renderDetail();
    });
  });
}

function renderDetail() {
  const record = state.filtered.find((item) => item.Employee_ID === state.selectedId);

  if (!record) {
    els.detailTitle.textContent = "Selecciona un registro";
    els.detailSummary.textContent = "Elige un caso para ver discrepancias, impacto y recomendaciones.";
    els.detailAnalysis.innerHTML = "";
    return;
  }

  const discrepancyTags = [];
  if (record.Rate_Mismatch) discrepancyTags.push("tarifa incorrecta");
  if (record.Hours_Mismatch) discrepancyTags.push("horas inconsistentes");
  if (record.Exceeds_Max_Hours) discrepancyTags.push("exceso de horas");
  if (record.Overbilling) discrepancyTags.push("sobrefacturacion");

  const delta = Number(record.Actual_Billing) - Number(record.Expected_Billing);

  els.detailTitle.textContent = `${record.Employee_Name} • Proyecto ${record.Project}`;
  els.detailSummary.innerHTML = `
    <strong>${record.Status === "ERROR" ? "Caso con hallazgos" : "Caso estable"}</strong>.
    ${record.Status === "ERROR"
      ? `Se detectaron ${discrepancyTags.length || 1} alertas: ${escapeHtml(discrepancyTags.join(", ") || "revision manual requerida")}.`
      : "No se encontraron discrepancias criticas en este registro."}
    <div class="detail-facts">
      <div class="fact-card">
        <span class="fact-label">Facturacion esperada</span>
        <span class="fact-value">${currency.format(record.Expected_Billing)}</span>
      </div>
      <div class="fact-card">
        <span class="fact-label">Facturacion actual</span>
        <span class="fact-value">${currency.format(record.Actual_Billing)}</span>
      </div>
      <div class="fact-card">
        <span class="fact-label">Diferencia</span>
        <span class="fact-value">${formatDelta(delta)}</span>
      </div>
      <div class="fact-card">
        <span class="fact-label">Horas maximas por semana</span>
        <span class="fact-value">${integer.format(record.Max_Hours_Per_Week)}</span>
      </div>
    </div>
  `;
  els.detailAnalysis.innerHTML = markdownToHtml(record.AI_ANALYSIS || "");
}

function markdownToHtml(markdown) {
  const lines = String(markdown).replace(/\r/g, "").split("\n");
  let html = "";
  let inUl = false;
  let inOl = false;
  let paragraph = [];

  const flushParagraph = () => {
    if (!paragraph.length) return;
    html += `<p>${inlineMarkdown(paragraph.join(" "))}</p>`;
    paragraph = [];
  };

  const closeLists = () => {
    if (inUl) {
      html += "</ul>";
      inUl = false;
    }
    if (inOl) {
      html += "</ol>";
      inOl = false;
    }
  };

  lines.forEach((rawLine) => {
    const line = rawLine.trim();

    if (!line) {
      flushParagraph();
      closeLists();
      return;
    }

    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    if (heading) {
      flushParagraph();
      closeLists();
      const level = Math.min(heading[1].length, 6);
      html += `<h${level}>${inlineMarkdown(heading[2])}</h${level}>`;
      return;
    }

    const ulMatch = line.match(/^[-*]\s+(.*)$/);
    if (ulMatch) {
      flushParagraph();
      if (inOl) {
        html += "</ol>";
        inOl = false;
      }
      if (!inUl) {
        html += "<ul>";
        inUl = true;
      }
      html += `<li>${inlineMarkdown(ulMatch[1])}</li>`;
      return;
    }

    const olMatch = line.match(/^\d+\.\s+(.*)$/);
    if (olMatch) {
      flushParagraph();
      if (inUl) {
        html += "</ul>";
        inUl = false;
      }
      if (!inOl) {
        html += "<ol>";
        inOl = true;
      }
      html += `<li>${inlineMarkdown(olMatch[1])}</li>`;
      return;
    }

    paragraph.push(line);
  });

  flushParagraph();
  closeLists();

  return html || "<p>Sin analisis disponible.</p>";
}

function inlineMarkdown(text) {
  return escapeHtml(text)
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.+?)\*/g, "<em>$1</em>")
    .replace(/`(.+?)`/g, "<code>$1</code>");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function formatDelta(delta) {
  if (delta > 0) return `+${currency.format(delta)}`;
  if (delta < 0) return `-${currency.format(Math.abs(delta))}`;
  return currency.format(0);
}
