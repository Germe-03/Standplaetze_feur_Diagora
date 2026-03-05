function renderDashboard(yearMetrics, monthMetrics) {
    const y = yearMetrics || {};
    const m = monthMetrics || {};

    setTextIfExists("metric-year-total", String(y.total || 0));
    setTextIfExists("metric-year-confirmed", String(y.confirmed || 0));
    setTextIfExists("metric-year-open", String(y.open || 0));
    setTextIfExists("metric-year-revenue", `CHF ${Number(y.revenue || 0).toFixed(2)}`);

    setTextIfExists("metric-month-total", String(m.total || 0));
    setTextIfExists("metric-month-confirmed", String(m.confirmed || 0));
    setTextIfExists("metric-month-open", String(m.open || 0));
    setTextIfExists("metric-month-revenue", `CHF ${Number(m.revenue || 0).toFixed(2)}`);

    // Backward-compatible support for older cached dashboard layout (single row IDs).
    setTextIfExists("metric-total", String(m.total || 0));
    setTextIfExists("metric-confirmed", String(m.confirmed || 0));
    setTextIfExists("metric-open", String(m.open || 0));
    setTextIfExists("metric-revenue", `CHF ${Number(m.revenue || 0).toFixed(2)}`);
}

function initDashboardMonthOptions() {
    const select = document.getElementById("dashboard-month");
    if (!select) {
        return;
    }
    const yearSelect = document.getElementById("dashboard-year");
    const now = new Date();
    const year = Number(yearSelect?.value || now.getFullYear());
    const monthNames = getGermanMonthNames();

    const currentValue = select.value;
    select.innerHTML = "";
    for (let m = 1; m <= 12; m++) {
        const value = String(m).padStart(2, "0");
        const option = document.createElement("option");
        option.value = value;
        option.textContent = `${monthNames[m - 1]} ${year}`;
        select.appendChild(option);
    }

    if (currentValue && Array.from(select.options).some(o => o.value === currentValue)) {
        select.value = currentValue;
    } else if (year === now.getFullYear()) {
        select.value = String(now.getMonth() + 1).padStart(2, "0");
    } else {
        select.value = "01";
    }
}

function initDashboardYearOptions() {
    const select = document.getElementById("dashboard-year");
    if (!select) {
        return;
    }
    const now = new Date();
    const currentYear = now.getFullYear();
    const years = new Set([currentYear]);

    (bookings || []).forEach(item => {
        const d = String(item.date || "");
        const y = Number(d.slice(0, 4));
        if (!Number.isNaN(y) && y > 1900 && y < 3000) {
            years.add(y);
        }
    });

    const sortedYears = Array.from(years).sort((a, b) => b - a);
    const currentValue = select.value;
    select.innerHTML = "";
    sortedYears.forEach(y => {
        const option = document.createElement("option");
        option.value = String(y);
        option.textContent = String(y);
        select.appendChild(option);
    });

    if (currentValue && Array.from(select.options).some(o => o.value === currentValue)) {
        select.value = currentValue;
    } else {
        select.value = String(currentYear);
    }
}

function initDashboardCampaignOptionsFor(selectId) {
    const select = document.getElementById(selectId);
    if (!select) {
        return;
    }

    const currentValue = select.value;
    select.innerHTML = "";
    const allOption = document.createElement("option");
    allOption.value = "";
    allOption.textContent = "Alle Kampagnen";
    select.appendChild(allOption);

    const campaigns = [...(meta.campaigns || [])]
        .sort((a, b) => String(a.name || "").localeCompare(String(b.name || ""), "de", { sensitivity: "base" }));

    campaigns.forEach(campaign => {
        const option = document.createElement("option");
        option.value = String(campaign.id);
        option.textContent = campaign.name;
        select.appendChild(option);
    });

    if (currentValue && Array.from(select.options).some(o => o.value === currentValue)) {
        select.value = currentValue;
    } else {
        select.value = "";
    }
}

function initDashboardCampaignOptions() {
    initDashboardCampaignOptionsFor("dashboard-campaign-year");
    initDashboardCampaignOptionsFor("dashboard-campaign-month");
    initDashboardCampaignOptionsFor("dashboard-chart-campaign");
}

function initDashboardChartPeriodOptions() {
    const select = document.getElementById("dashboard-chart-period");
    const yearSelect = document.getElementById("dashboard-year");
    if (!select) {
        return;
    }
    const year = Number(yearSelect?.value || new Date().getFullYear());
    const currentValue = select.value;
    const monthNames = getGermanMonthNames();

    select.innerHTML = "";
    const yearOption = document.createElement("option");
    yearOption.value = "year";
    yearOption.textContent = `Ganzes Jahr ${year}`;
    select.appendChild(yearOption);

    for (let m = 1; m <= 12; m++) {
        const value = String(m).padStart(2, "0");
        const option = document.createElement("option");
        option.value = value;
        option.textContent = `${monthNames[m - 1]} ${year}`;
        select.appendChild(option);
    }

    if (currentValue && Array.from(select.options).some(o => o.value === currentValue)) {
        select.value = currentValue;
    } else {
        select.value = "year";
    }
}

function drawChartFallbackMessage(canvasId, message) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) {
        return;
    }
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    const width = Math.max(320, Math.floor(rect.width || canvas.clientWidth || 640));
    const height = Math.max(220, Math.floor(rect.height || canvas.clientHeight || 260));
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    const ctx = canvas.getContext("2d");
    if (!ctx) {
        return;
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, width, height);
    ctx.strokeStyle = "#bfd7f1";
    ctx.strokeRect(0.5, 0.5, width - 1, height - 1);
    ctx.fillStyle = "#3f5f87";
    ctx.font = "13px Manrope, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(message, width / 2, height / 2);
}

function installDashboardChartsFallback() {
    if (window.DashboardCharts) {
        return;
    }

    function renderSimpleLine(canvasId, labels, values, color, currencyMode) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            return;
        }
        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        const width = Math.max(320, Math.floor(rect.width || canvas.clientWidth || 640));
        const height = Math.max(220, Math.floor(rect.height || canvas.clientHeight || 260));
        canvas.width = Math.floor(width * dpr);
        canvas.height = Math.floor(height * dpr);
        const ctx = canvas.getContext("2d");
        if (!ctx) {
            return;
        }
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, width, height);

        const area = { left: 46, top: 14, right: width - 12, bottom: height - 26 };
        const max = Math.max(1, ...values.map(v => Number(v || 0)));

        ctx.strokeStyle = "#d3e5f8";
        ctx.lineWidth = 1;
        for (let i = 1; i <= 4; i++) {
            const y = area.bottom - (i * (area.bottom - area.top) / 4);
            ctx.beginPath();
            ctx.moveTo(area.left, y);
            ctx.lineTo(area.right, y);
            ctx.stroke();
        }

        ctx.strokeStyle = "#95b8dc";
        ctx.beginPath();
        ctx.moveTo(area.left, area.top);
        ctx.lineTo(area.left, area.bottom);
        ctx.lineTo(area.right, area.bottom);
        ctx.stroke();

        if (values.length > 0) {
            const stepX = values.length > 1 ? (area.right - area.left) / (values.length - 1) : 0;
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.beginPath();
            values.forEach((v, idx) => {
                const x = area.left + stepX * idx;
                const y = area.bottom - ((Number(v || 0) / max) * (area.bottom - area.top));
                if (idx === 0) {
                    ctx.moveTo(x, y);
                } else {
                    ctx.lineTo(x, y);
                }
            });
            ctx.stroke();
        }

        ctx.fillStyle = "#446b95";
        ctx.font = "11px Manrope, sans-serif";
        ctx.textAlign = "right";
        const formatY = currencyMode ? (v => `CHF ${Math.round(v)}`) : (v => String(Math.round(v)));
        for (let i = 0; i <= 4; i++) {
            const value = (max / 4) * i;
            const y = area.bottom - (i * (area.bottom - area.top) / 4);
            ctx.fillText(formatY(value), area.left - 8, y + 3);
        }

        ctx.textAlign = "center";
        if (labels.length > 0) {
            const stepX = labels.length > 1 ? (area.right - area.left) / (labels.length - 1) : 0;
            labels.forEach((label, idx) => {
                const x = area.left + stepX * idx;
                ctx.fillText(String(label), x, area.bottom + 15);
            });
        }
    }

    window.DashboardCharts = {
        renderCountChart(canvasId, labels, values) {
            renderSimpleLine(canvasId, labels, values, "#2f6fb0", false);
        },
        renderCostChart(canvasId, labels, values) {
            renderSimpleLine(canvasId, labels, values, "#3b8db6", true);
        },
        renderBudgetPieChart(canvasId) {
            drawChartFallbackMessage(canvasId, "Kreisdiagramm nicht verfuegbar.");
        }
    };
}

function renderDashboardCharts() {
    installDashboardChartsFallback();
    if (!window.DashboardCharts) {
        drawChartFallbackMessage("dashboard-chart-bookings", "Diagramm nicht geladen (charts.js fehlt).");
        drawChartFallbackMessage("dashboard-chart-costs", "Diagramm nicht geladen (charts.js fehlt).");
        drawChartFallbackMessage("dashboard-chart-budget", "Diagramm nicht geladen (charts.js fehlt).");
        return;
    }
    const yearSelect = document.getElementById("dashboard-year");
    const periodSelect = document.getElementById("dashboard-chart-period");
    const campaignSelect = document.getElementById("dashboard-chart-campaign");

    const selectedYear = Number(yearSelect?.value || new Date().getFullYear());
    const selectedPeriod = String(periodSelect?.value || "year");
    const selectedCampaign = String(campaignSelect?.value || "").trim();

    const yearScoped = bookings.filter(item => {
        if (Boolean(item.cancelled)) {
            return false;
        }
        if (selectedCampaign && String(item.campaign_id ?? "") !== selectedCampaign) {
            return false;
        }
        const d = String(item.date || "");
        return d.startsWith(`${selectedYear}-`);
    });

    const scoped = yearScoped.filter(item => {
        if (Boolean(item.cancelled)) {
            return false;
        }
        if (selectedCampaign && String(item.campaign_id ?? "") !== selectedCampaign) {
            return false;
        }
        const d = String(item.date || "");
        if (!d.startsWith(`${selectedYear}-`)) {
            return false;
        }
        if (selectedPeriod !== "year" && !d.startsWith(`${selectedYear}-${selectedPeriod}-`)) {
            return false;
        }
        return true;
    });
    const filtered = scoped.filter(item => Boolean(item.confirmed));

    let labels = [];
    let countValues = [];
    let costValues = [];

    if (selectedPeriod === "year") {
        const monthNamesShort = ["Jan", "Feb", "Mrz", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"];
        labels = monthNamesShort;
        countValues = new Array(12).fill(0);
        costValues = new Array(12).fill(0);
        filtered.forEach(item => {
            const month = Number(String(item.date || "").slice(5, 7));
            if (month >= 1 && month <= 12) {
                countValues[month - 1] += 1;
                costValues[month - 1] += Number(item.price || 0);
            }
        });
    } else {
        const month = Number(selectedPeriod);
        const days = getDaysInMonth(selectedYear, month);
        labels = Array.from({ length: days }, (_, i) => String(i + 1));
        countValues = new Array(days).fill(0);
        costValues = new Array(days).fill(0);
        filtered.forEach(item => {
            const day = Number(String(item.date || "").slice(8, 10));
            if (day >= 1 && day <= days) {
                countValues[day - 1] += 1;
                costValues[day - 1] += Number(item.price || 0);
            }
        });
    }

    try {
        window.DashboardCharts.renderCountChart("dashboard-chart-bookings", labels, countValues);
        window.DashboardCharts.renderCostChart("dashboard-chart-costs", labels, costValues);
    } catch (error) {
        console.error("Chart rendering failed", error);
        drawChartFallbackMessage("dashboard-chart-bookings", "Diagramm konnte nicht gezeichnet werden.");
        drawChartFallbackMessage("dashboard-chart-costs", "Diagramm konnte nicht gezeichnet werden.");
    }

    try {
        renderBudgetPieChartForSelection(selectedYear, selectedCampaign, yearScoped);
    } catch (error) {
        console.error("Budget pie rendering failed", error);
        drawChartFallbackMessage("dashboard-chart-budget", "Diagramm konnte nicht gezeichnet werden.");
    }
}

function computeMetricsForPeriod(items) {
    const safe = items.filter(item => !Boolean(item.cancelled));
    const total = safe.length;
    const confirmed = safe.filter(item => Boolean(item.confirmed)).length;
    const open = safe.filter(item => !Boolean(item.confirmed)).length;
    const revenue = safe.reduce((sum, item) => sum + Number(item.price || 0), 0);
    return { total, confirmed, open, revenue };
}

function computeBudgetBreakdown(items, totalBudget) {
    const safe = (items || []).filter(item => !Boolean(item.cancelled));
    const confirmedCosts = safe
        .filter(item => Boolean(item.confirmed))
        .reduce((sum, item) => sum + Number(item.price || 0), 0);
    const openCosts = safe
        .filter(item => !Boolean(item.confirmed))
        .reduce((sum, item) => sum + Number(item.price || 0), 0);
    const remaining = Math.max(Number(totalBudget || 0) - confirmedCosts - openCosts, 0);
    return { confirmedCosts, openCosts, remaining };
}

function getBudgetForScope(selectedYear, selectedCampaignId) {
    const campaigns = meta.campaigns || [];
    if (selectedCampaignId) {
        const selected = campaigns.find(c => String(c.id) === String(selectedCampaignId));
        return selected ? Number(selected.budget || 0) : 0;
    }
    return campaigns
        .filter(c => Number(c.year) === Number(selectedYear))
        .reduce((sum, c) => sum + Number(c.budget || 0), 0);
}

function renderBudgetPieChartForSelection(selectedYear, selectedCampaignId, scopedBookings) {
    if (!window.DashboardCharts || typeof window.DashboardCharts.renderBudgetPieChart !== "function") {
        return;
    }

    const budget = getBudgetForScope(selectedYear, selectedCampaignId);
    const breakdown = computeBudgetBreakdown(scopedBookings, budget);
    window.DashboardCharts.renderBudgetPieChart("dashboard-chart-budget", [
        { label: "Rot (Bestaetigt)", value: breakdown.confirmedCosts, color: "#d64555" },
        { label: "Blau (Offen)", value: breakdown.openCosts, color: "#2d66a8" },
        { label: "Gruen (Uebrig)", value: breakdown.remaining, color: "#2f9c63" }
    ]);
}

function renderDashboardFromBookings() {
    const yearSelect = document.getElementById("dashboard-year");
    const monthSelect = document.getElementById("dashboard-month");
    const yearCampaignSelect = document.getElementById("dashboard-campaign-year");
    const monthCampaignSelect = document.getElementById("dashboard-campaign-month");
    const selectedYear = Number(yearSelect?.value || new Date().getFullYear());
    const selectedMonth = String(monthSelect?.value || "").trim();
    const selectedYearCampaign = String(yearCampaignSelect?.value || "").trim();
    const selectedMonthCampaign = String(monthCampaignSelect?.value || "").trim();
    if (!selectedMonth || Number.isNaN(selectedYear)) {
        renderDashboard({ total: 0, confirmed: 0, open: 0, revenue: 0 }, { total: 0, confirmed: 0, open: 0, revenue: 0 });
        return;
    }
    const selectedMonthNum = Number(selectedMonth);

    const scopedYearBookings = bookings.filter(item => {
        if (!selectedYearCampaign) {
            return true;
        }
        return String(item.campaign_id ?? "") === selectedYearCampaign;
    });

    const yearBookings = scopedYearBookings.filter(item => {
        const d = String(item.date || "");
        return d.startsWith(`${selectedYear}-`);
    });

    const scopedMonthBookings = bookings.filter(item => {
        if (!selectedMonthCampaign) {
            return true;
        }
        return String(item.campaign_id ?? "") === selectedMonthCampaign;
    });

    const monthBookings = scopedMonthBookings.filter(item => {
        const d = String(item.date || "");
        return d.startsWith(`${selectedYear}-${String(selectedMonthNum).padStart(2, "0")}-`);
    });

    renderDashboard(
        computeMetricsForPeriod(yearBookings),
        computeMetricsForPeriod(monthBookings)
    );
    renderDashboardCharts();
}
