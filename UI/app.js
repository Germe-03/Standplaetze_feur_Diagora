let bookings = [];
let stands = [];
let meta = { locations: [], campaigns: [], cities: [], users: [] };

const API_BASE = window.__API_BASE__ || "";
const bookingSort = { key: "id", dir: "desc" };
const standSort = { key: "id", dir: "asc" };

let bookingEditId = null;
let standEditId = null;
let nextBookingId = null;
let nextStandId = null;

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
    const search = (document.getElementById("booking-search")?.value || "").trim().toLowerCase();
    const dateFrom = document.getElementById("booking-date-from")?.value || "";
    const dateTo = document.getElementById("booking-date-to")?.value || "";
    const status = getBookingStatusCode();

    const filtered = bookings.filter(booking => {
        const bookingDate = booking.date || "";
        const bySearch =
            !search ||
            String(booking.stand || "").toLowerCase().includes(search) ||
            String(booking.city || "").toLowerCase().includes(search) ||
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

    const sbbFilter = getStandSbbCode();

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

function getBookingStatusCode() {
    const raw = normalizeText(document.getElementById("booking-status")?.value || "");
    if (!raw || raw === "alle") {
        return "all";
    }
    if (raw === "bestaetigt") {
        return "confirmed";
    }
    if (raw === "offen") {
        return "open";
    }
    if (raw === "storniert") {
        return "cancelled";
    }
    return "all";
}

function getStandSbbCode() {
    const raw = normalizeText(document.getElementById("stand-sbb")?.value || "");
    if (!raw || raw === "sbb: alle") {
        return "all";
    }
    if (raw === "sbb: ja") {
        return "yes";
    }
    if (raw === "sbb: nein") {
        return "no";
    }
    return "all";
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

    document.getElementById("new-booking-location").value = currentBookingLocation;
    document.getElementById("new-booking-campaign").value = currentBookingCampaign;
    document.getElementById("new-booking-user").value = currentBookingUser;
    document.getElementById("new-stand-user").value = currentStandUser;

    updateStandCityRequirement();
    setBookingFormMode(bookingEditId != null);
    setStandFormMode(standEditId != null);
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
    renderDashboard(await response.json());
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
    await Promise.all([loadDashboardFromApi(), loadBookingsFromApi(), loadStandsFromApi()]);
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
        "stand-name", "stand-city-kanton", "stand-price-min", "stand-price-max",
        "stand-rating-min", "stand-rating-max", "stand-dialog-min", "stand-dialog-max", "stand-sbb"
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
            loadStandsFromApi().catch(console.error);
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

                await Promise.all([loadDashboardFromApi(), loadBookingsFromApi(), loadStandsFromApi()]);
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
    const month = document.getElementById("stand-limit-month");
    if (month) {
        month.value = new Date().toISOString().slice(0, 7);
    }

    setBookingFormMode(false);
    setStandFormMode(false);

    wireTabs();
    wireBookingFilters();
    wireStandFilters();
    wireSorting();
    wireCreateForms();

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
