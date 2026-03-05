function getDaysInMonth(year, month) {
    return new Date(year, month, 0).getDate();
}

function toIsoDate(value) {
    const d = new Date(value.getFullYear(), value.getMonth(), value.getDate());
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
}

function addDays(value, amount) {
    const d = new Date(value.getFullYear(), value.getMonth(), value.getDate());
    d.setDate(d.getDate() + amount);
    return d;
}

function addMonths(value, amount) {
    return new Date(value.getFullYear(), value.getMonth() + amount, 1);
}

function startOfWeek(value) {
    const d = new Date(value.getFullYear(), value.getMonth(), value.getDate());
    const day = (d.getDay() + 6) % 7;
    d.setDate(d.getDate() - day);
    return d;
}

function sameDate(a, b) {
    return a.getFullYear() === b.getFullYear()
        && a.getMonth() === b.getMonth()
        && a.getDate() === b.getDate();
}

function formatDateLabel(value) {
    const dd = String(value.getDate()).padStart(2, "0");
    const mm = String(value.getMonth() + 1).padStart(2, "0");
    const yyyy = value.getFullYear();
    return `${dd}.${mm}.${yyyy}`;
}

function getCalendarMonthNames() {
    return getGermanMonthNames();
}

function getCalendarWeekdayNames() {
    return ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];
}

function getIsoWeekNumber(value) {
    const d = new Date(Date.UTC(value.getFullYear(), value.getMonth(), value.getDate()));
    d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
}

function getCalendarTitle() {
    const monthNames = getCalendarMonthNames();
    if (calendarViewMode === "month") {
        return `${monthNames[calendarAnchorDate.getMonth()]} ${calendarAnchorDate.getFullYear()}`;
    }

    const weekStart = startOfWeek(calendarAnchorDate);
    const weekEnd = addDays(weekStart, calendarViewMode === "workweek" ? 4 : 6);
    const weekNumber = getIsoWeekNumber(weekStart);
    return `Woche ${weekNumber}: ${formatDateLabel(weekStart)} - ${formatDateLabel(weekEnd)}`;
}

function groupBookingsByDate() {
    const grouped = {};
    (bookings || []).forEach(item => {
        if (Boolean(item.cancelled)) {
            return;
        }
        const iso = String(item.date || "").trim();
        if (!iso) {
            return;
        }
        if (!grouped[iso]) {
            grouped[iso] = [];
        }
        grouped[iso].push(item);
    });
    Object.keys(grouped).forEach(key => {
        grouped[key].sort((a, b) => String(a.stand || "").localeCompare(String(b.stand || ""), "de", { sensitivity: "base" }));
    });
    return grouped;
}

function getCalendarEventLabel(item) {
    const stand = String(item?.stand || "-");
    const city = String(item?.city || "-");
    const campaign = String(item?.campaign || "-");
    return `${stand} | ${city} | ${campaign}`;
}

function getCalendarEventClass(item) {
    const isConfirmed = Boolean(item?.confirmed);
    if (isConfirmed) {
        return "calendar-event-confirmed";
    }

    const rawDate = String(item?.date || "").trim();
    if (!rawDate) {
        return "calendar-event-unconfirmed";
    }
    const eventDate = new Date(`${rawDate}T00:00:00`);
    if (Number.isNaN(eventDate.getTime())) {
        return "calendar-event-unconfirmed";
    }

    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const msPerDay = 24 * 60 * 60 * 1000;
    const diffDays = Math.floor((eventDate.getTime() - today.getTime()) / msPerDay);
    const currentWeekStart = startOfWeek(today);
    const currentWeekEnd = addDays(currentWeekStart, 6);

    // Unbestaetigt innerhalb der aktuellen Woche (Mo-So) immer rot
    if (eventDate >= currentWeekStart && eventDate <= currentWeekEnd) {
        return "calendar-event-pending-this-week";
    }

    // Unbestaetigt und innerhalb der naechsten 7 Tage
    if (diffDays >= 0 && diffDays <= 7) {
        return "calendar-event-pending-soon";
    }
    // Unbestaetigt und in den letzten 14 Tagen
    if (diffDays < 0 && diffDays >= -14) {
        return "calendar-event-pending-recent";
    }

    return "calendar-event-unconfirmed";
}

function getCalendarEventHtml(item) {
    const label = getCalendarEventLabel(item);
    const bookingId = Number(item?.id);
    const bookingAttr = Number.isFinite(bookingId) ? ` data-booking-id="${bookingId}"` : "";
    const eventClass = getCalendarEventClass(item);
    return `<div class="calendar-event ${eventClass}"${bookingAttr} title="${escapeHtml(label)}">${escapeHtml(label)}</div>`;
}

function buildCalendarDays() {
    if (calendarViewMode === "month") {
        const monthStart = new Date(calendarAnchorDate.getFullYear(), calendarAnchorDate.getMonth(), 1);
        const firstGridDay = startOfWeek(monthStart);
        return Array.from({ length: 42 }, (_, index) => addDays(firstGridDay, index));
    }

    const weekStart = startOfWeek(calendarAnchorDate);
    const dayCount = calendarViewMode === "workweek" ? 5 : 7;
    return Array.from({ length: dayCount }, (_, index) => addDays(weekStart, index));
}

function renderCalendarWeekdays(days) {
    const container = document.getElementById("calendar-weekdays");
    if (!container) {
        return;
    }

    const weekdayNames = getCalendarWeekdayNames();
    if (calendarViewMode === "month") {
        container.style.gridTemplateColumns = "repeat(7, minmax(0, 1fr))";
        container.innerHTML = weekdayNames
            .map(name => `<div class="calendar-weekday">${name}</div>`)
            .join("");
        return;
    }

    const columns = days.length || 1;
    container.style.gridTemplateColumns = `repeat(${columns}, minmax(0, 1fr))`;
    container.innerHTML = days.map(day => {
        const dayIndex = (day.getDay() + 6) % 7;
        return `<div class="calendar-weekday">${weekdayNames[dayIndex]} ${formatDateLabel(day)}</div>`;
    }).join("");
}

function renderCalendarGrid() {
    const title = document.getElementById("calendar-title");
    const grid = document.getElementById("calendar-grid");
    if (!title || !grid) {
        return;
    }
    closeCalendarMorePopup();

    title.textContent = getCalendarTitle();
    const days = buildCalendarDays();
    renderCalendarWeekdays(days);

    const grouped = groupBookingsByDate();
    calendarItemsByDate = {};
    const today = new Date();
    const activeMonth = calendarAnchorDate.getMonth();
    const activeYear = calendarAnchorDate.getFullYear();
    grid.classList.toggle("calendar-grid-month", calendarViewMode === "month");
    grid.classList.toggle("calendar-grid-week", calendarViewMode !== "month");
    grid.innerHTML = "";

    days.forEach(day => {
        const iso = toIsoDate(day);
        const list = grouped[iso] || [];
        const visibleItems = calendarViewMode === "month" ? list.slice(0, 2) : list;

        const cell = document.createElement("article");
        const inCurrentMonth = day.getMonth() === activeMonth && day.getFullYear() === activeYear;
        cell.className = "calendar-cell";
        if (!inCurrentMonth && calendarViewMode === "month") {
            cell.classList.add("calendar-cell-muted");
        }
        if (sameDate(day, today)) {
            cell.classList.add("calendar-cell-today");
        }

        const dayLabel = String(day.getDate());
        const eventsHtml = visibleItems
            .map(item => getCalendarEventHtml(item))
            .join("");
        const hiddenItems = list.slice(2);
        const moreHtml = calendarViewMode === "month" && hiddenItems.length > 0
            ? `<div class="calendar-event-more" data-calendar-more="${iso}">+${hiddenItems.length}</div>`
            : "";
        if (list.length > 0) {
            calendarItemsByDate[iso] = list;
        }

        cell.innerHTML = `
            <div class="calendar-cell-head">${dayLabel}</div>
            <div class="calendar-events">${eventsHtml}${moreHtml}</div>
        `;
        grid.appendChild(cell);
    });
}

function openCalendarMorePopup(isoDate) {
    const popup = document.getElementById("calendar-more-popup");
    const title = document.getElementById("calendar-more-popup-title");
    const list = document.getElementById("calendar-more-popup-list");
    if (!popup || !title || !list) {
        return;
    }

    const items = calendarItemsByDate[isoDate] || [];
    const [y, m, d] = String(isoDate || "").split("-");
    if (!y || !m || !d) {
        return;
    }

    title.textContent = `Weitere Standplaetze am ${d}.${m}.${y}`;
    list.innerHTML = items.length
        ? items.map(item => getCalendarEventHtml(item)).join("")
        : "<p>Keine weiteren Eintraege.</p>";
    popup.classList.remove("hidden");
}

function closeCalendarMorePopup() {
    const popup = document.getElementById("calendar-more-popup");
    if (popup) {
        popup.classList.add("hidden");
    }
}

function navigateCalendar(step) {
    if (calendarViewMode === "month") {
        calendarAnchorDate = addMonths(calendarAnchorDate, step);
    } else {
        calendarAnchorDate = addDays(calendarAnchorDate, step * 7);
    }
    renderCalendarGrid();
}

function wireCalendarControls() {
    const modeSelect = document.getElementById("calendar-view-mode");
    const prevBtn = document.getElementById("calendar-prev-btn");
    const nextBtn = document.getElementById("calendar-next-btn");
    const todayBtn = document.getElementById("calendar-today-btn");

    if (modeSelect) {
        modeSelect.value = calendarViewMode;
        modeSelect.addEventListener("change", () => {
            const nextMode = String(modeSelect.value || "month");
            calendarViewMode = nextMode === "week" || nextMode === "workweek" ? nextMode : "month";
            renderCalendarGrid();
        });
    }
    if (prevBtn) {
        prevBtn.addEventListener("click", () => navigateCalendar(-1));
    }
    if (nextBtn) {
        nextBtn.addEventListener("click", () => navigateCalendar(1));
    }
    if (todayBtn) {
        todayBtn.addEventListener("click", () => {
            calendarAnchorDate = new Date();
            renderCalendarGrid();
        });
    }

    const grid = document.getElementById("calendar-grid");
    if (grid) {
        grid.addEventListener("click", event => {
            const target = event.target;
            const moreBtn = target?.closest?.("[data-calendar-more]");
            if (!moreBtn) {
                return;
            }

            const key = String(moreBtn.getAttribute("data-calendar-more") || "");
            if (!key) {
                return;
            }
            openCalendarMorePopup(key);
            event.preventDefault();
        });
        grid.addEventListener("dblclick", event => {
            const target = event.target;
            const eventNode = target?.closest?.("[data-booking-id]");
            if (!eventNode) {
                return;
            }
            const bookingId = Number(eventNode.getAttribute("data-booking-id"));
            if (!Number.isFinite(bookingId) || bookingId <= 0) {
                return;
            }
            closeCalendarMorePopup();
            jumpToBookingFromCalendar(bookingId);
            event.preventDefault();
        });
    }

    const popupCloseBtn = document.getElementById("calendar-more-popup-close");
    if (popupCloseBtn) {
        popupCloseBtn.addEventListener("click", () => {
            closeCalendarMorePopup();
        });
    }
    const popup = document.getElementById("calendar-more-popup");
    if (popup) {
        popup.addEventListener("click", event => {
            if (event.target === popup) {
                closeCalendarMorePopup();
            }
        });
        popup.addEventListener("dblclick", event => {
            const target = event.target;
            const eventNode = target?.closest?.("[data-booking-id]");
            if (!eventNode) {
                return;
            }
            const bookingId = Number(eventNode.getAttribute("data-booking-id"));
            if (!Number.isFinite(bookingId) || bookingId <= 0) {
                return;
            }
            closeCalendarMorePopup();
            jumpToBookingFromCalendar(bookingId);
            event.preventDefault();
        });
    }
}
