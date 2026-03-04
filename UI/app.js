let bookings = [];
let stands = [];
let meta = { locations: [], campaigns: [], cities: [], users: [] };

const API_BASE = window.__API_BASE__ || "";
const bookingSort = { key: "id", dir: "desc" };
const standSort = { key: "id", dir: "asc" };
const columnFilters = { bookings: {}, stands: {} };
const DATE_FILTER_KEYS = {
    bookings: new Set(["created_at", "date"]),
    stands: new Set(["limit_valid_from"])
};

let bookingEditId = null;
let standEditId = null;
let nextBookingId = null;
let nextStandId = null;
let activeColumnFilter = null;

function getActiveFilterState() {
    if (!activeColumnFilter) {
        return null;
    }
    const { table, key } = activeColumnFilter;
    return { table, key };
}

function isDateFilterColumn(table, key) {
    return Boolean(DATE_FILTER_KEYS[table] && DATE_FILTER_KEYS[table].has(key));
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function compareValues(a, b, dir = "asc") {
    const ax = a ?? "";
    const bx = b ?? "";
    let result = 0;

    if (typeof ax === "number" && typeof bx === "number") {
        result = ax - bx;
    } else {
        result = String(ax).localeCompare(String(bx), "de", { numeric: true, sensitivity: "base" });
    }

    return dir === "asc" ? result : -result;
}

function updateSortIndicators() {
    const headers = Array.from(document.querySelectorAll("th.sortable"));
    headers.forEach(h => h.removeAttribute("data-sort-dir"));

    const bHeader = document.querySelector(`th.sortable[data-table="bookings"][data-key="${bookingSort.key}"]`);
    const sHeader = document.querySelector(`th.sortable[data-table="stands"][data-key="${standSort.key}"]`);

    if (bHeader) {
        bHeader.setAttribute("data-sort-dir", bookingSort.dir);
    }
    if (sHeader) {
        sHeader.setAttribute("data-sort-dir", standSort.dir);
    }
}

function setBookingFormMode(isEdit) {
    const title = document.getElementById("booking-form-title");
    const closeBtn = document.getElementById("booking-close-btn");
    const idLabel = document.getElementById("booking-form-id-label");
    if (title) {
        title.textContent = isEdit ? "Buchung anpassen" : "Neue Buchung";
        if (idLabel) {
            title.appendChild(idLabel);
        }
    }
    if (idLabel) {
        const value = isEdit ? bookingEditId : nextBookingId;
        idLabel.textContent = value != null ? `(#${value})` : "";
    }
    if (closeBtn) {
        closeBtn.classList.toggle("hidden", !isEdit);
    }
}

function setStandFormMode(isEdit) {
    const title = document.getElementById("stand-form-title");
    const closeBtn = document.getElementById("stand-close-btn");
    const idLabel = document.getElementById("stand-form-id-label");
    if (title) {
        title.textContent = isEdit ? "Standplatz anpassen" : "Neuer Standplatz";
        if (idLabel) {
            title.appendChild(idLabel);
        }
    }
    if (idLabel) {
        const value = isEdit ? standEditId : nextStandId;
        idLabel.textContent = value != null ? `(#${value})` : "";
    }
    if (closeBtn) {
        closeBtn.classList.toggle("hidden", !isEdit);
    }
}

function closeBookingEditMode() {
    bookingEditId = null;
    const form = document.getElementById("booking-create-form");
    if (form) {
        form.reset();
    }
    setBookingFormMode(false);
    applyDefaultBookingPriceFromLocation();
}

function closeStandEditMode() {
    standEditId = null;
    const form = document.getElementById("stand-create-form");
    if (form) {
        form.reset();
    }
    setStandFormMode(false);
    updateStandCityRequirement();
}

function setTextIfExists(id, value) {
    const el = document.getElementById(id);
    if (el) {
        el.textContent = value;
    }
}

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
    const monthNames = [
        "Januar", "Februar", "Maerz", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember"
    ];

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
    const monthNames = [
        "Januar", "Februar", "Maerz", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember"
    ];

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

function getDaysInMonth(year, month) {
    return new Date(year, month, 0).getDate();
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
        }
    };
}

function renderDashboardCharts() {
    installDashboardChartsFallback();
    if (!window.DashboardCharts) {
        drawChartFallbackMessage("dashboard-chart-bookings", "Diagramm nicht geladen (charts.js fehlt).");
        drawChartFallbackMessage("dashboard-chart-costs", "Diagramm nicht geladen (charts.js fehlt).");
        return;
    }
    const yearSelect = document.getElementById("dashboard-year");
    const periodSelect = document.getElementById("dashboard-chart-period");
    const campaignSelect = document.getElementById("dashboard-chart-campaign");

    const selectedYear = Number(yearSelect?.value || new Date().getFullYear());
    const selectedPeriod = String(periodSelect?.value || "year");
    const selectedCampaign = String(campaignSelect?.value || "").trim();

    const filtered = bookings.filter(item => {
        if (Boolean(item.cancelled) || !Boolean(item.confirmed)) {
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
}

function computeMetricsForPeriod(items) {
    const safe = items.filter(item => !Boolean(item.cancelled));
    const total = safe.length;
    const confirmed = safe.filter(item => Boolean(item.confirmed)).length;
    const open = safe.filter(item => !Boolean(item.confirmed)).length;
    const revenue = safe.reduce((sum, item) => sum + Number(item.price || 0), 0);
    return { total, confirmed, open, revenue };
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

function startBookingEdit(bookingId) {
    const booking = bookings.find(item => Number(item.id) === Number(bookingId));
    if (!booking) {
        return;
    }

    bookingEditId = Number(booking.id);

    document.getElementById("new-booking-date").value = booking.date || "";
    document.getElementById("new-booking-location").value = booking.stand || "";
    document.getElementById("new-booking-campaign").value = booking.campaign || "";
    const user = (meta.users || []).find(item => Number(item.id) === Number(booking.user_id));
    document.getElementById("new-booking-user").value = user ? user.name : "";
    document.getElementById("new-booking-price").value = Number(booking.price || 0).toFixed(2);
    document.getElementById("new-booking-confirmed").checked = Boolean(booking.confirmed);
    document.getElementById("new-booking-cancelled").checked = Boolean(booking.cancelled);

    setBookingFormMode(true);
}

function startStandEdit(standId) {
    const stand = stands.find(item => Number(item.id) === Number(standId));
    if (!stand) {
        return;
    }

    standEditId = Number(stand.id);

    document.getElementById("new-stand-name").value = stand.name || "";
    document.getElementById("new-stand-city").value = stand.city || "";
    document.getElementById("new-stand-kanton").value = "";
    const standUser = (meta.users || []).find(item => Number(item.id) === Number(stand.user_id));
    document.getElementById("new-stand-user").value = standUser ? standUser.name : "";
    document.getElementById("new-stand-price").value = stand.price != null ? Number(stand.price).toFixed(2) : "";
    document.getElementById("new-stand-rating").value = stand.rating ?? "";
    document.getElementById("new-stand-dialog").value = stand.max_dialog ?? "";
    document.getElementById("new-stand-limit-yearly").value = stand.location_limit_yearly_raw ?? "";
    document.getElementById("new-stand-limit-monthly").value = stand.location_limit_monthly_raw ?? "";
    document.getElementById("new-stand-limit-campaign").value = stand.location_limit_campaign_raw ?? "";
    document.getElementById("new-stand-limit-valid-from").value = stand.location_limit_valid_from_raw || "";
    document.getElementById("new-stand-sbb").checked = Boolean(stand.is_sbb);
    document.getElementById("new-stand-note").value = stand.note || "";

    setStandFormMode(true);
    updateStandCityRequirement();
}

function renderBookings() {
    const filtered = bookings.filter(booking => {
        return matchesColumnFilters("bookings", booking);
    });

    const sorted = [...filtered].sort((a, b) => {
        const getStatus = x => (x.cancelled ? "Storniert" : (x.confirmed ? "Bestaetigt" : "Offen"));
        const va = bookingSort.key === "status" ? getStatus(a) : a[bookingSort.key];
        const vb = bookingSort.key === "status" ? getStatus(b) : b[bookingSort.key];
        return compareValues(va, vb, bookingSort.dir);
    });

    const body = document.getElementById("booking-rows");
    body.innerHTML = "";

    sorted.forEach(booking => {
        const tr = document.createElement("tr");
        tr.style.cursor = "pointer";
        tr.title = "Doppelklick zum Bearbeiten";
        const statusText = booking.cancelled ? "Storniert" : (booking.confirmed ? "Bestaetigt" : "Offen");
        tr.innerHTML = `
            <td>#${booking.id}</td>
            <td>${booking.created_at || "-"}</td>
            <td>${booking.date}</td>
            <td>${booking.stand}</td>
            <td>${booking.city || "-"}</td>
            <td>${booking.campaign}</td>
            <td>CHF ${Number(booking.price || 0).toFixed(2)}</td>
            <td>${statusText}</td>
        `;
        tr.addEventListener("dblclick", () => startBookingEdit(booking.id));
        body.appendChild(tr);
    });
}

function renderStands() {
    const filtered = stands.filter(stand => {
        return matchesColumnFilters("stands", stand);
    });

    const sorted = [...filtered].sort((a, b) => compareValues(a[standSort.key], b[standSort.key], standSort.dir));

    const body = document.getElementById("stands-rows");
    body.innerHTML = "";

    sorted.forEach(stand => {
        const tr = document.createElement("tr");
        tr.style.cursor = "pointer";
        tr.title = "Doppelklick zum Bearbeiten";
        tr.innerHTML = `
            <td>#${stand.id ?? "-"}</td>
            <td>${stand.name || "-"}</td>
            <td>${stand.city || "-"}</td>
            <td>${stand.kanton || "-"}</td>
            <td>${stand.price != null ? `CHF ${Number(stand.price).toFixed(2)}` : "-"}</td>
            <td>${stand.rating ?? "-"}</td>
            <td>${stand.max_dialog ?? "-"}</td>
            <td>${stand.limit_yearly ?? "-"}</td>
            <td>${stand.remaining_yearly ?? "-"}</td>
            <td>${stand.limit_monthly ?? "-"}</td>
            <td>${stand.remaining_monthly ?? "-"}</td>
            <td>${stand.limit_campaign ?? "-"}</td>
            <td>${stand.remaining_campaign ?? "-"}</td>
            <td>${stand.limit_valid_from ?? "-"}</td>
            <td>${stand.is_sbb ? "Ja" : "Nein"}</td>
            <td>${stand.note || "-"}</td>
        `;
        tr.addEventListener("dblclick", () => startStandEdit(stand.id));
        body.appendChild(tr);
    });
}

function fillDatalist(listId, items) {
    const list = document.getElementById(listId);
    if (!list) {
        return;
    }

    list.innerHTML = "";

    items.forEach(item => {
        const option = document.createElement("option");
        option.value = item.name;
        list.appendChild(option);
    });
}

function normalizeText(value) {
    return String(value || "").trim().toLowerCase();
}

function findItemByName(items, typedName) {
    const target = normalizeText(typedName);
    if (!target) {
        return null;
    }
    return (items || []).find(item => normalizeText(item.name) === target) || null;
}

function cityExists(cityName) {
    const normalized = normalizeText(cityName);
    if (!normalized) {
        return false;
    }
    return (meta.cities || []).some(city => normalizeText(city.name) === normalized);
}

function updateStandCityRequirement() {
    const cityInput = document.getElementById("new-stand-city");
    const kantonInput = document.getElementById("new-stand-kanton");
    if (!cityInput || !kantonInput) {
        return;
    }

    const cityName = cityInput.value || "";
    const needsKanton = cityName.trim() !== "" && !cityExists(cityName);
    kantonInput.required = needsKanton;
    const container = kantonInput.closest(".form-field");
    if (container) {
        container.style.display = needsKanton ? "grid" : "none";
        kantonInput.style.display = needsKanton ? "" : "none";
    } else {
        kantonInput.style.display = needsKanton ? "" : "none";
    }
    if (!needsKanton) {
        kantonInput.value = "";
    }
}

function applyDefaultBookingPriceFromLocation() {
    const locationInput = document.getElementById("new-booking-location");
    const priceInput = document.getElementById("new-booking-price");
    if (!locationInput || !priceInput) {
        return;
    }

    const selectedLocation = findItemByName(meta.locations || [], locationInput.value);
    if (!selectedLocation) {
        priceInput.value = "0.00";
        return;
    }

    if (selectedLocation.price == null) {
        priceInput.value = "0.00";
        return;
    }

    priceInput.value = Number(selectedLocation.price).toFixed(2);
}

async function loadMeta() {
    const response = await fetch(`${API_BASE}/api/meta`);
    if (!response.ok) {
        throw new Error("Meta request failed");
    }

    const currentBookingLocation = document.getElementById("new-booking-location")?.value || "";
    const currentBookingCampaign = document.getElementById("new-booking-campaign")?.value || "";
    const currentBookingUser = document.getElementById("new-booking-user")?.value || "";
    const currentStandUser = document.getElementById("new-stand-user")?.value || "";

    meta = await response.json();
    nextBookingId = meta.next_booking_id ?? null;
    nextStandId = meta.next_stand_id ?? null;

    fillDatalist("new-booking-location-list", meta.locations || []);
    fillDatalist("new-booking-campaign-list", meta.campaigns || []);
    fillDatalist("new-booking-user-list", meta.users || []);
    fillDatalist("new-stand-user-list", meta.users || []);
    initDashboardCampaignOptions();

    document.getElementById("new-booking-location").value = currentBookingLocation;
    document.getElementById("new-booking-campaign").value = currentBookingCampaign;
    document.getElementById("new-booking-user").value = currentBookingUser;
    document.getElementById("new-stand-user").value = currentStandUser;

    updateStandCityRequirement();
    setBookingFormMode(bookingEditId != null);
    setStandFormMode(standEditId != null);
}

function getStandMonthQuery() {
    return "";
}

async function loadBookingsFromApi() {
    const response = await fetch(`${API_BASE}/api/bookings`);
    if (!response.ok) {
        throw new Error("Bookings request failed");
    }
    bookings = await response.json();
    initDashboardYearOptions();
    initDashboardMonthOptions();
    initDashboardChartPeriodOptions();
    renderBookings();
    renderDashboardFromBookings();
}

async function loadStandsFromApi() {
    const response = await fetch(`${API_BASE}/api/stands${getStandMonthQuery()}`);
    if (!response.ok) {
        throw new Error("Stands request failed");
    }
    stands = await response.json();
    renderStands();
}

async function loadFromApi() {
    await loadMeta();
    await Promise.all([loadBookingsFromApi(), loadStandsFromApi()]);
}

function wireSorting() {
    const headers = Array.from(document.querySelectorAll("th.sortable"));
    headers.forEach(header => {
        const filterBtn = document.createElement("button");
        filterBtn.type = "button";
        filterBtn.className = "col-filter-btn";
        filterBtn.title = "Sortieren/Filtern";
        filterBtn.textContent = "↕";
        filterBtn.addEventListener("click", event => {
            event.stopPropagation();
            const label = (header.firstChild?.textContent || header.dataset.key || "").trim();
            if (header.dataset.table === "bookings") {
                bookingSort.key = "id";
                bookingSort.dir = "desc";
                renderBookings();
            } else {
                standSort.key = "id";
                standSort.dir = "asc";
                renderStands();
            }
            updateSortIndicators();
            openColumnFilterPopover(header.dataset.table, header.dataset.key, label, filterBtn);
        });
        header.appendChild(filterBtn);

        header.addEventListener("click", () => {
            const table = header.dataset.table;
            const key = header.dataset.key;
            const state = table === "bookings" ? bookingSort : standSort;

            if (state.key === key) {
                state.dir = state.dir === "asc" ? "desc" : "asc";
            } else {
                state.key = key;
                state.dir = "asc";
            }

            if (table === "bookings") {
                renderBookings();
            } else {
                renderStands();
            }

            updateSortIndicators();
        });
    });

    updateSortIndicators();
}

function getColumnValue(table, key, item) {
    if (table === "bookings" && key === "status") {
        return item.cancelled ? "Storniert" : (item.confirmed ? "Bestaetigt" : "Offen");
    }
    if (table === "stands" && key === "is_sbb") {
        return item.is_sbb ? "Ja" : "Nein";
    }
    const value = item[key];
    if (value == null) {
        return "";
    }
    return String(value);
}

function matchesColumnFilters(table, item) {
    const filters = columnFilters[table] || {};
    const entries = Object.entries(filters);
    for (const [key, filterValue] of entries) {
        if (filterValue && typeof filterValue === "object" && filterValue.type === "date_range") {
            const value = getColumnValue(table, key, item);
            if (filterValue.from && (!value || value < filterValue.from)) {
                return false;
            }
            if (filterValue.to && (!value || value > filterValue.to)) {
                return false;
            }
            continue;
        }
        const selectedValues = filterValue;
        if (!Array.isArray(selectedValues) || selectedValues.length === 0) {
            continue;
        }
        const value = getColumnValue(table, key, item);
        if (!selectedValues.includes(value)) {
            return false;
        }
    }
    return true;
}

function getRowsByTable(table) {
    return table === "bookings" ? bookings : stands;
}

function updateColumnFilterHits() {
    const hits = document.getElementById("column-filter-hits");
    const count = document.getElementById("column-filter-count");
    const input = document.getElementById("column-filter-search");
    const dateRange = document.getElementById("column-filter-date-range");
    const dateFrom = document.getElementById("column-filter-date-from");
    const dateTo = document.getElementById("column-filter-date-to");
    const state = getActiveFilterState();
    if (!hits || !count || !input || !dateRange || !dateFrom || !dateTo || !state || !activeColumnFilter) {
        return;
    }

    if (activeColumnFilter.mode === "date_range") {
        input.classList.add("hidden");
        count.classList.add("hidden");
        hits.classList.add("hidden");
        dateRange.classList.remove("hidden");
        hits.innerHTML = "";
        return;
    }

    input.classList.remove("hidden");
    count.classList.remove("hidden");
    hits.classList.remove("hidden");
    dateRange.classList.add("hidden");

    const { table, key } = state;
    const query = String(input.value || "").trim().toLowerCase();
    const values = getRowsByTable(table).map(item => getColumnValue(table, key, item));
    const uniqueValues = Array.from(new Set(values.filter(v => String(v).trim() !== "")));
    const matches = query
        ? uniqueValues.filter(v => v.toLowerCase().includes(query))
        : uniqueValues;
    const selected = activeColumnFilter.selected || new Set(uniqueValues);
    const allSelected = selected.size >= uniqueValues.length;

    count.textContent = `${matches.length} Treffer`;
    const allRow = `
        <label class="filter-popover-option">
            <input type="checkbox" data-role="all" ${allSelected ? "checked" : ""}>
            <span>Alle anzeigen</span>
        </label>
    `;
    const rows = matches.slice(0, 100).map(v => `
        <label class="filter-popover-option">
            <input type="checkbox" data-role="value" data-value="${escapeHtml(v)}" ${selected.has(v) ? "checked" : ""}>
            <span>${escapeHtml(v)}</span>
        </label>
    `).join("");
    hits.innerHTML = allRow + (rows || `<div class="filter-popover-hit empty">Keine Treffer</div>`);

    const allCheckbox = hits.querySelector('input[data-role="all"]');
    if (allCheckbox) {
        allCheckbox.addEventListener("change", () => {
            if (!activeColumnFilter) {
                return;
            }
            if (allCheckbox.checked) {
                activeColumnFilter.selected = new Set(uniqueValues);
            } else {
                activeColumnFilter.selected = new Set();
            }
            applyLiveColumnFilter();
            updateColumnFilterHits();
        });
    }

    hits.querySelectorAll('input[data-role="value"]').forEach(box => {
        box.addEventListener("change", () => {
            if (!activeColumnFilter) {
                return;
            }
            const rawValue = box.getAttribute("data-value") || "";
            const value = rawValue
                .replaceAll("&amp;", "&")
                .replaceAll("&lt;", "<")
                .replaceAll("&gt;", ">")
                .replaceAll("&quot;", '"')
                .replaceAll("&#39;", "'");
            if (box.checked) {
                activeColumnFilter.selected.add(value);
            } else {
                activeColumnFilter.selected.delete(value);
            }
            applyLiveColumnFilter();
            updateColumnFilterHits();
        });
    });
}

function placeColumnFilterPopover() {
    const popover = document.getElementById("column-filter-popover");
    if (!popover || !activeColumnFilter?.trigger) {
        return;
    }

    const rect = activeColumnFilter.trigger.getBoundingClientRect();
    const top = rect.bottom + window.scrollY + 6;
    const left = rect.left + window.scrollX;

    popover.style.top = `${top}px`;
    popover.style.left = `${left}px`;
}

function openColumnFilterPopover(table, key, label, trigger) {
    const popover = document.getElementById("column-filter-popover");
    const title = document.getElementById("column-filter-title");
    const input = document.getElementById("column-filter-search");
    if (!popover || !title || !input || !trigger) {
        return;
    }

    const existing = columnFilters[table]?.[key];
    if (isDateFilterColumn(table, key)) {
        const from = existing && existing.type === "date_range" ? (existing.from || "") : "";
        const to = existing && existing.type === "date_range" ? (existing.to || "") : "";
        activeColumnFilter = { table, key, trigger, mode: "date_range", from, to };
        const dateFrom = document.getElementById("column-filter-date-from");
        const dateTo = document.getElementById("column-filter-date-to");
        if (dateFrom) {
            dateFrom.value = from;
        }
        if (dateTo) {
            dateTo.value = to;
        }
    } else {
        const allValues = Array.from(
            new Set(getRowsByTable(table).map(item => getColumnValue(table, key, item)).filter(v => String(v).trim() !== ""))
        );
        const selected = Array.isArray(existing) && existing.length ? new Set(existing) : new Set(allValues);
        activeColumnFilter = { table, key, trigger, mode: "value_list", allValues, selected };
    }

    title.textContent = `Filtern: ${label}`;
    input.value = "";
    popover.classList.remove("hidden");
    placeColumnFilterPopover();
    updateColumnFilterHits();
    input.focus();
    input.select();
}

function closeColumnFilterPopover() {
    const popover = document.getElementById("column-filter-popover");
    if (popover) {
        popover.classList.add("hidden");
    }
    activeColumnFilter = null;
}

function applyLiveColumnFilter() {
    const state = getActiveFilterState();
    if (!state || !activeColumnFilter) {
        return;
    }

    const { table, key } = state;
    if (!columnFilters[table]) {
        columnFilters[table] = {};
    }

    if (activeColumnFilter.mode === "date_range") {
        const dateFrom = document.getElementById("column-filter-date-from");
        const dateTo = document.getElementById("column-filter-date-to");
        const from = String(dateFrom?.value || "").trim();
        const to = String(dateTo?.value || "").trim();
        activeColumnFilter.from = from;
        activeColumnFilter.to = to;
        if (!from && !to) {
            delete columnFilters[table][key];
        } else {
            columnFilters[table][key] = { type: "date_range", from, to };
        }
    } else {
        const selected = Array.from(activeColumnFilter.selected || []);
        if (selected.length === 0 || selected.length >= (activeColumnFilter.allValues || []).length) {
            delete columnFilters[table][key];
        } else {
            columnFilters[table][key] = selected;
        }
    }

    if (table === "bookings") {
        renderBookings();
    } else {
        renderStands();
    }
}

function wireColumnFilterPopover() {
    const input = document.getElementById("column-filter-search");
    const popover = document.getElementById("column-filter-popover");
    const dateFrom = document.getElementById("column-filter-date-from");
    const dateTo = document.getElementById("column-filter-date-to");

    if (input) {
        input.addEventListener("input", () => {
            updateColumnFilterHits();
        });
        input.addEventListener("keydown", event => {
            if (event.key === "Escape") {
                event.preventDefault();
                closeColumnFilterPopover();
            }
        });
    }

    [dateFrom, dateTo].forEach(el => {
        if (!el) {
            return;
        }
        el.addEventListener("input", () => {
            applyLiveColumnFilter();
        });
        el.addEventListener("change", () => {
            applyLiveColumnFilter();
        });
    });

    document.addEventListener("click", event => {
        const target = event.target;
        const isButton = target?.closest?.(".col-filter-btn");
        const insidePopover = popover && popover.contains(target);
        if (!insidePopover && !isButton) {
            closeColumnFilterPopover();
        }
    });

    window.addEventListener("resize", () => {
        if (activeColumnFilter) {
            placeColumnFilterPopover();
        }
    });

    window.addEventListener("scroll", () => {
        if (activeColumnFilter) {
            placeColumnFilterPopover();
        }
    }, true);
}

function wireTabs() {
    const tabs = Array.from(document.querySelectorAll(".tab"));
    const views = Array.from(document.querySelectorAll(".tab-view"));

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            tabs.forEach(item => item.classList.remove("active"));
            tab.classList.add("active");

            views.forEach(view => view.classList.remove("active"));
            const selected = document.getElementById(`tab-${tab.dataset.tab}`);
            if (selected) {
                selected.classList.add("active");
            }
            closeColumnFilterPopover();
            if (tab.dataset.tab === "dashboard") {
                setTimeout(() => {
                    renderDashboardCharts();
                }, 0);
            }
        });
    });
}

function wireCreateForms() {
    const bookingForm = document.getElementById("booking-create-form");
    const bookingError = document.getElementById("booking-create-error");
    const bookingLocation = document.getElementById("new-booking-location");
    const bookingClose = document.getElementById("booking-close-btn");

    if (bookingLocation) {
        bookingLocation.addEventListener("change", () => {
            applyDefaultBookingPriceFromLocation();
        });
    }

    if (bookingClose) {
        bookingClose.addEventListener("click", () => {
            closeBookingEditMode();
        });
    }

    if (bookingForm) {
        bookingForm.addEventListener("submit", async event => {
            event.preventDefault();
            bookingError.textContent = "";

            const selectedLocation = findItemByName(meta.locations || [], document.getElementById("new-booking-location")?.value || "");
            const selectedCampaign = findItemByName(meta.campaigns || [], document.getElementById("new-booking-campaign")?.value || "");
            const selectedUser = findItemByName(meta.users || [], document.getElementById("new-booking-user")?.value || "");
            if (!selectedLocation || !selectedCampaign || !selectedUser) {
                bookingError.textContent = "Bitte Standplatz, Kampagne und Benutzer aus der Vorschlagsliste waehlen.";
                return;
            }

            const payload = {
                date_of_event: document.getElementById("new-booking-date")?.value || "",
                price: document.getElementById("new-booking-price")?.value || "",
                location_id: selectedLocation.id,
                campaign_id: selectedCampaign.id,
                user_id: selectedUser.id,
                confirmed: Boolean(document.getElementById("new-booking-confirmed")?.checked),
                cancelled: Boolean(document.getElementById("new-booking-cancelled")?.checked)
            };

            const isEdit = bookingEditId != null;
            const method = isEdit ? "PUT" : "POST";
            const url = isEdit ? `${API_BASE}/api/bookings/${bookingEditId}` : `${API_BASE}/api/bookings`;

            try {
                const response = await fetch(url, {
                    method,
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const err = await response.json().catch(() => ({}));
                    throw new Error(err.error || "Buchung konnte nicht gespeichert werden");
                }

                await Promise.all([loadBookingsFromApi(), loadStandsFromApi()]);
                closeBookingEditMode();
            } catch (error) {
                bookingError.textContent = String(error.message || error);
            }
        });
    }

    const standForm = document.getElementById("stand-create-form");
    const standError = document.getElementById("stand-create-error");
    const standCityInput = document.getElementById("new-stand-city");
    const standClose = document.getElementById("stand-close-btn");

    if (standCityInput) {
        standCityInput.addEventListener("input", updateStandCityRequirement);
        standCityInput.addEventListener("change", updateStandCityRequirement);
    }

    if (standClose) {
        standClose.addEventListener("click", () => {
            closeStandEditMode();
        });
    }

    if (standForm) {
        standForm.addEventListener("submit", async event => {
            event.preventDefault();
            standError.textContent = "";

            const selectedUser = findItemByName(meta.users || [], document.getElementById("new-stand-user")?.value || "");
            if (!selectedUser) {
                standError.textContent = "Bitte Benutzer aus der Vorschlagsliste waehlen.";
                return;
            }

            const payload = {
                name: (document.getElementById("new-stand-name")?.value || "").trim(),
                city_name: (document.getElementById("new-stand-city")?.value || "").trim(),
                kanton_name: (document.getElementById("new-stand-kanton")?.value || "").trim(),
                user_id: selectedUser.id,
                price: document.getElementById("new-stand-price")?.value || "",
                rating: document.getElementById("new-stand-rating")?.value || "",
                max_dialog: document.getElementById("new-stand-dialog")?.value || "",
                limit_yearly: document.getElementById("new-stand-limit-yearly")?.value || "",
                limit_monthly: document.getElementById("new-stand-limit-monthly")?.value || "",
                limit_campaign: document.getElementById("new-stand-limit-campaign")?.value || "",
                limit_valid_from: document.getElementById("new-stand-limit-valid-from")?.value || "",
                is_sbb: Boolean(document.getElementById("new-stand-sbb")?.checked),
                note: (document.getElementById("new-stand-note")?.value || "").trim()
            };

            const isEdit = standEditId != null;
            const method = isEdit ? "PUT" : "POST";
            const url = isEdit ? `${API_BASE}/api/stands/${standEditId}` : `${API_BASE}/api/stands`;

            try {
                const response = await fetch(url, {
                    method,
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const err = await response.json().catch(() => ({}));
                    throw new Error(err.error || "Standplatz konnte nicht gespeichert werden");
                }

                await Promise.all([loadMeta(), loadStandsFromApi()]);
                closeStandEditMode();
            } catch (error) {
                standError.textContent = String(error.message || error);
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    setBookingFormMode(false);
    setStandFormMode(false);
    installDashboardChartsFallback();
    initDashboardYearOptions();
    initDashboardMonthOptions();

    wireTabs();
    wireSorting();
    wireColumnFilterPopover();
    wireCreateForms();

    const dashboardYear = document.getElementById("dashboard-year");
    const dashboardMonth = document.getElementById("dashboard-month");
    const dashboardCampaignYear = document.getElementById("dashboard-campaign-year");
    const dashboardCampaignMonth = document.getElementById("dashboard-campaign-month");
    if (dashboardYear) {
        dashboardYear.addEventListener("change", () => {
            initDashboardMonthOptions();
            initDashboardChartPeriodOptions();
            renderDashboardFromBookings();
        });
    }
    if (dashboardMonth) {
        dashboardMonth.addEventListener("change", () => {
            renderDashboardFromBookings();
        });
    }
    if (dashboardCampaignYear) {
        dashboardCampaignYear.addEventListener("change", () => {
            renderDashboardFromBookings();
        });
    }
    if (dashboardCampaignMonth) {
        dashboardCampaignMonth.addEventListener("change", () => {
            renderDashboardFromBookings();
        });
    }
    const dashboardChartPeriod = document.getElementById("dashboard-chart-period");
    if (dashboardChartPeriod) {
        dashboardChartPeriod.addEventListener("change", () => {
            renderDashboardCharts();
        });
    }
    const dashboardChartCampaign = document.getElementById("dashboard-chart-campaign");
    if (dashboardChartCampaign) {
        dashboardChartCampaign.addEventListener("change", () => {
            renderDashboardCharts();
        });
    }

    window.addEventListener("resize", () => {
        renderDashboardCharts();
    });

    loadFromApi().then(() => {
        applyDefaultBookingPriceFromLocation();
    }).catch(error => {
        console.error(error);
        const bookingError = document.getElementById("booking-create-error");
        if (bookingError) {
            bookingError.textContent = "API nicht erreichbar oder Serverfehler.";
        }
    });
});
