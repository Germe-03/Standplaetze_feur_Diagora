let bookings = [];
let stands = [];
let campaigns = [];
let usersAdmin = [];
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
let calendarViewMode = "month";
let calendarAnchorDate = new Date();
let calendarItemsByDate = {};

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
    updateBookingCampaignCreateBox();
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

function activateTab(tabName) {
    const tabs = Array.from(document.querySelectorAll(".tab"));
    const views = Array.from(document.querySelectorAll(".tab-view"));
    tabs.forEach(item => item.classList.toggle("active", item.dataset.tab === tabName));
    views.forEach(view => view.classList.remove("active"));
    const selected = document.getElementById(`tab-${tabName}`);
    if (selected) {
        selected.classList.add("active");
    }
    closeColumnFilterPopover();
    if (tabName === "dashboard") {
        setTimeout(() => {
            renderDashboardCharts();
        }, 0);
    }
    if (tabName === "calendar") {
        setTimeout(() => {
            renderCalendarGrid();
        }, 0);
    }
    if (tabName === "campaigns") {
        setTimeout(() => {
            if (typeof loadCampaignsFromApi === "function" && (!campaigns || campaigns.length === 0)) {
                loadCampaignsFromApi().catch(() => {
                    if (typeof renderCampaigns === "function") {
                        renderCampaigns();
                    }
                });
                return;
            }
            if (typeof renderCampaigns === "function") {
                renderCampaigns();
            }
        }, 0);
    }
    if (tabName === "users") {
        setTimeout(() => {
            if (typeof loadUsersAdminFromApi === "function" && (!usersAdmin || usersAdmin.length === 0)) {
                loadUsersAdminFromApi().catch(() => {
                    if (typeof renderUsersAdmin === "function") {
                        renderUsersAdmin();
                    }
                });
                return;
            }
            if (typeof renderUsersAdmin === "function") {
                renderUsersAdmin();
            }
        }, 0);
    }
}

function jumpToBookingFromCalendar(bookingId) {
    const id = Number(bookingId);
    if (!Number.isFinite(id) || id <= 0) {
        return;
    }
    activateTab("bookings");
    startBookingEdit(id);
    setTimeout(() => {
        const row = document.querySelector(`[data-booking-row-id="${id}"]`);
        if (!row) {
            return;
        }
        row.scrollIntoView({ behavior: "smooth", block: "center" });
        row.classList.add("booking-row-focus");
        window.setTimeout(() => {
            row.classList.remove("booking-row-focus");
        }, 1500);
    }, 0);
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
    updateBookingCampaignCreateBox();
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
    renderCalendarGrid();
}

async function loadStandsFromApi() {
    const response = await fetch(`${API_BASE}/api/stands${getStandMonthQuery()}`);
    if (!response.ok) {
        throw new Error("Stands request failed");
    }
    stands = await response.json();
    renderStands();
}

async function loadCampaignsFromApi() {
    const response = await fetch(`${API_BASE}/api/campaigns`);
    if (!response.ok) {
        const usersById = new Map((meta.users || []).map(u => [Number(u.id), u.name]));
        campaigns = (meta.campaigns || []).map(c => ({
            id: c.id,
            name: c.name,
            year: c.year,
            budget: c.budget,
            user_id: null,
            user_name: usersById.get(Number(c.user_id)) || "",
            is_active: c.is_active !== false,
        }));
        if (typeof renderCampaigns === "function") {
            renderCampaigns();
        }
        return;
    }
    campaigns = (await response.json().catch(() => [])).map(c => ({
        ...c,
        is_active: c?.is_active !== false && c?.is_active !== 0 && c?.is_active !== "0",
    }));
    if (typeof renderCampaigns === "function") {
        renderCampaigns();
    }
}

async function loadUsersAdminFromApi() {
    const fallbackUsersFromMeta = () => (meta.users || []).map(user => {
        const fullName = String(user.name || "").trim();
        const parts = fullName.split(" ").filter(Boolean);
        const first = String(user.first_name || "").trim() || (parts.length > 0 ? parts[0] : fullName);
        const last = String(user.last_name || "").trim() || (parts.length > 1 ? parts.slice(1).join(" ") : "");
        return {
            id: user.id,
            first_name: first,
            last_name: last,
            full_name: fullName,
            role: String(user.role || "").trim() || "-",
            is_active: user.is_active !== false,
        };
    });

    try {
        const response = await fetch(`${API_BASE}/api/users`);
        if (response.ok) {
            usersAdmin = await response.json().catch(() => []);
        } else {
            usersAdmin = fallbackUsersFromMeta();
        }
    } catch (_) {
        usersAdmin = fallbackUsersFromMeta();
    }
    if (typeof renderUsersAdmin === "function") {
        renderUsersAdmin();
    }
}

async function loadFromApi() {
    await loadMeta();
    await Promise.all([loadBookingsFromApi(), loadStandsFromApi(), loadCampaignsFromApi(), loadUsersAdminFromApi()]);
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

    tabs.forEach(tab => {
        tab.addEventListener("click", () => {
            activateTab(tab.dataset.tab);
        });
    });
}
