let bookings = [];
let stands = [];
let meta = { locations: [], campaigns: [], cities: [], users: [] };

const API_BASE = window.__API_BASE__ || "";
const bookingSort = { key: "id", dir: "desc" };
const standSort = { key: "id", dir: "asc" };

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

function renderDashboard(metrics) {
    const total = metrics.total || 0;
    const confirmed = metrics.confirmed || 0;
    const open = metrics.open || 0;
    const revenue = metrics.revenue || 0;

    document.getElementById("metric-total").textContent = String(total);
    document.getElementById("metric-confirmed").textContent = String(confirmed);
    document.getElementById("metric-open").textContent = String(open);
    document.getElementById("metric-revenue").textContent = `CHF ${Number(revenue).toFixed(2)}`;
}

function renderBookings() {
    const search = (document.getElementById("booking-search")?.value || "").trim().toLowerCase();
    const dateFrom = document.getElementById("booking-date-from")?.value || "";
    const dateTo = document.getElementById("booking-date-to")?.value || "";
    const status = document.getElementById("booking-status")?.value || "all";

    const filtered = bookings.filter(booking => {
        const bookingDate = booking.date || "";
        const bySearch =
            !search ||
            String(booking.stand || "").toLowerCase().includes(search) ||
            String(booking.campaign || "").toLowerCase().includes(search);
        const byFrom = !dateFrom || bookingDate >= dateFrom;
        const byTo = !dateTo || bookingDate <= dateTo;

        let byStatus = true;
        if (status === "confirmed") {
            byStatus = Boolean(booking.confirmed) && !Boolean(booking.cancelled);
        } else if (status === "open") {
            byStatus = !Boolean(booking.confirmed) && !Boolean(booking.cancelled);
        } else if (status === "cancelled") {
            byStatus = Boolean(booking.cancelled);
        }

        return bySearch && byFrom && byTo && byStatus;
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
        const statusText = booking.cancelled ? "Storniert" : (booking.confirmed ? "Bestaetigt" : "Offen");
        tr.innerHTML = `
            <td>#${booking.id}</td>
            <td>${booking.created_at || "-"}</td>
            <td>${booking.date}</td>
            <td>${booking.stand}</td>
            <td>${booking.campaign}</td>
            <td>CHF ${Number(booking.price || 0).toFixed(2)}</td>
            <td>${statusText}</td>
        `;
        body.appendChild(tr);
    });
}

function renderStands() {
    const parseOptionalNumber = id => {
        const raw = document.getElementById(id)?.value ?? "";
        if (raw === "") {
            return null;
        }
        const value = Number(raw);
        return Number.isNaN(value) ? null : value;
    };

    const nameFilter = (document.getElementById("stand-name")?.value || "").trim().toLowerCase();
    const cityKantonFilter = (document.getElementById("stand-city-kanton")?.value || "").trim().toLowerCase();

    const priceMin = parseOptionalNumber("stand-price-min");
    const priceMax = parseOptionalNumber("stand-price-max");
    const ratingMin = parseOptionalNumber("stand-rating-min");
    const ratingMax = parseOptionalNumber("stand-rating-max");
    const dialogMin = parseOptionalNumber("stand-dialog-min");
    const dialogMax = parseOptionalNumber("stand-dialog-max");

    const sbbFilter = document.getElementById("stand-sbb")?.value || "all";

    const filtered = stands.filter(stand => {
        const standName = String(stand.name || "").toLowerCase();
        const standCity = String(stand.city || "").toLowerCase();
        const standKanton = String(stand.kanton || "").toLowerCase();
        const standPrice = stand.price != null ? Number(stand.price) : null;
        const standRating = stand.rating != null ? Number(stand.rating) : null;
        const standDialog = stand.max_dialog != null ? Number(stand.max_dialog) : null;

        const byName = !nameFilter || standName.includes(nameFilter);
        const byCityKanton =
            !cityKantonFilter ||
            standCity.includes(cityKantonFilter) ||
            standKanton.includes(cityKantonFilter);

        const byPriceMin = priceMin == null || (standPrice != null && standPrice >= priceMin);
        const byPriceMax = priceMax == null || (standPrice != null && standPrice <= priceMax);
        const byRatingMin = ratingMin == null || (standRating != null && standRating >= ratingMin);
        const byRatingMax = ratingMax == null || (standRating != null && standRating <= ratingMax);
        const byDialogMin = dialogMin == null || (standDialog != null && standDialog >= dialogMin);
        const byDialogMax = dialogMax == null || (standDialog != null && standDialog <= dialogMax);

        let bySbb = true;
        if (sbbFilter === "yes") {
            bySbb = Boolean(stand.is_sbb);
        } else if (sbbFilter === "no") {
            bySbb = !Boolean(stand.is_sbb);
        }

        return (
            byName &&
            byCityKanton &&
            byPriceMin &&
            byPriceMax &&
            byRatingMin &&
            byRatingMax &&
            byDialogMin &&
            byDialogMax &&
            bySbb
        );
    });

    const sorted = [...filtered].sort((a, b) => compareValues(a[standSort.key], b[standSort.key], standSort.dir));

    const body = document.getElementById("stands-rows");
    body.innerHTML = "";

    sorted.forEach(stand => {
        const tr = document.createElement("tr");
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
        body.appendChild(tr);
    });
}

function fillSelect(selectId, items, placeholder) {
    const select = document.getElementById(selectId);
    if (!select) {
        return;
    }

    select.innerHTML = "";
    const ph = document.createElement("option");
    ph.value = "";
    ph.textContent = placeholder;
    select.appendChild(ph);

    items.forEach(item => {
        const option = document.createElement("option");
        option.value = String(item.id);
        option.textContent = item.name;
        select.appendChild(option);
    });

    if (items.length > 0) {
        select.value = String(items[0].id);
    }
}

function applyDefaultBookingPriceFromLocation() {
    const locationSelect = document.getElementById("new-booking-location");
    const priceInput = document.getElementById("new-booking-price");
    if (!locationSelect || !priceInput) {
        return;
    }

    const selectedId = Number(locationSelect.value);
    if (!selectedId) {
        priceInput.value = "0.00";
        return;
    }

    const selectedLocation = (meta.locations || []).find(location => Number(location.id) === selectedId);
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

    meta = await response.json();

    fillSelect("new-booking-location", meta.locations || [], "Standplatz waehlen");
    fillSelect("new-booking-campaign", meta.campaigns || [], "Kampagne waehlen");
    fillSelect("new-booking-user", meta.users || [], "Benutzer waehlen");

    fillSelect("new-stand-city", meta.cities || [], "Stadt waehlen");
    fillSelect("new-stand-user", meta.users || [], "Benutzer waehlen");

    applyDefaultBookingPriceFromLocation();
}

function getStandMonthQuery() {
    const month = (document.getElementById("stand-limit-month")?.value || "").trim();
    if (!month) {
        return "";
    }
    return `?month=${encodeURIComponent(month)}`;
}

async function loadDashboardFromApi() {
    const response = await fetch(`${API_BASE}/api/dashboard`);
    if (!response.ok) {
        throw new Error("Dashboard request failed");
    }
    const metrics = await response.json();
    renderDashboard(metrics);
}

async function loadBookingsFromApi() {
    const response = await fetch(`${API_BASE}/api/bookings`);
    if (!response.ok) {
        throw new Error("Bookings request failed");
    }
    bookings = await response.json();
    renderBookings();
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
    await Promise.all([
        loadDashboardFromApi(),
        loadBookingsFromApi(),
        loadStandsFromApi()
    ]);
}

function wireBookingFilters() {
    const ids = ["booking-search", "booking-date-from", "booking-date-to", "booking-status"];
    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", renderBookings);
            el.addEventListener("change", renderBookings);
        }
    });
}

function wireStandFilters() {
    const ids = [
        "stand-name",
        "stand-city-kanton",
        "stand-price-min",
        "stand-price-max",
        "stand-rating-min",
        "stand-rating-max",
        "stand-dialog-min",
        "stand-dialog-max",
        "stand-sbb"
    ];

    ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener("input", renderStands);
            el.addEventListener("change", renderStands);
        }
    });

    const month = document.getElementById("stand-limit-month");
    if (month) {
        month.addEventListener("change", () => {
            loadStandsFromApi().catch(error => {
                console.error(error);
            });
        });
    }
}

function wireSorting() {
    const headers = Array.from(document.querySelectorAll("th.sortable"));
    headers.forEach(header => {
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
        });
    });
}

function wireCreateForms() {
    const bookingForm = document.getElementById("booking-create-form");
    const bookingError = document.getElementById("booking-create-error");
    const bookingLocation = document.getElementById("new-booking-location");

    if (bookingLocation) {
        bookingLocation.addEventListener("change", () => {
            applyDefaultBookingPriceFromLocation();
        });
    }

    if (bookingForm) {
        bookingForm.addEventListener("submit", async event => {
            event.preventDefault();
            bookingError.textContent = "";

            const payload = {
                date_of_event: document.getElementById("new-booking-date")?.value || "",
                price: document.getElementById("new-booking-price")?.value || "",
                location_id: document.getElementById("new-booking-location")?.value || "",
                campaign_id: document.getElementById("new-booking-campaign")?.value || "",
                user_id: document.getElementById("new-booking-user")?.value || "",
                confirmed: Boolean(document.getElementById("new-booking-confirmed")?.checked),
                cancelled: Boolean(document.getElementById("new-booking-cancelled")?.checked)
            };

            try {
                const response = await fetch(`${API_BASE}/api/bookings`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const err = await response.json().catch(() => ({}));
                    throw new Error(err.error || "Buchung konnte nicht gespeichert werden");
                }

                bookingForm.reset();
                await Promise.all([loadDashboardFromApi(), loadBookingsFromApi(), loadStandsFromApi()]);
                applyDefaultBookingPriceFromLocation();
            } catch (error) {
                bookingError.textContent = String(error.message || error);
            }
        });
    }

    const standForm = document.getElementById("stand-create-form");
    const standError = document.getElementById("stand-create-error");

    if (standForm) {
        standForm.addEventListener("submit", async event => {
            event.preventDefault();
            standError.textContent = "";

            const payload = {
                name: (document.getElementById("new-stand-name")?.value || "").trim(),
                city_id: document.getElementById("new-stand-city")?.value || "",
                user_id: document.getElementById("new-stand-user")?.value || "",
                price: document.getElementById("new-stand-price")?.value || "",
                rating: document.getElementById("new-stand-rating")?.value || "",
                max_dialog: document.getElementById("new-stand-dialog")?.value || "",
                is_sbb: Boolean(document.getElementById("new-stand-sbb")?.checked),
                note: (document.getElementById("new-stand-note")?.value || "").trim()
            };

            try {
                const response = await fetch(`${API_BASE}/api/stands`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                if (!response.ok) {
                    const err = await response.json().catch(() => ({}));
                    throw new Error(err.error || "Standplatz konnte nicht gespeichert werden");
                }

                standForm.reset();
                await Promise.all([loadMeta(), loadStandsFromApi()]);
            } catch (error) {
                standError.textContent = String(error.message || error);
            }
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const month = document.getElementById("stand-limit-month");
    if (month) {
        month.value = new Date().toISOString().slice(0, 7);
    }

    wireTabs();
    wireBookingFilters();
    wireStandFilters();
    wireSorting();
    wireCreateForms();

    loadFromApi().catch(error => {
        console.error(error);
        const bookingError = document.getElementById("booking-create-error");
        if (bookingError) {
            bookingError.textContent = "API nicht erreichbar oder Serverfehler.";
        }
    });
});
