function startBookingEdit(bookingId) {
    const booking = bookings.find(item => Number(item.id) === Number(bookingId));
    if (!booking) {
        return;
    }

    bookingEditId = Number(booking.id);

    document.getElementById("new-booking-date").value = booking.date || "";
    document.getElementById("new-booking-location").value = booking.stand || "";
    const campaign = (meta.campaigns || []).find(item => Number(item.id) === Number(booking.campaign_id));
    document.getElementById("new-booking-campaign").value = campaign ? formatCampaignDisplay(campaign) : (booking.campaign || "");
    const user = (meta.users || []).find(item => Number(item.id) === Number(booking.user_id));
    document.getElementById("new-booking-user").value = user ? user.name : "";
    document.getElementById("new-booking-price").value = Number(booking.price || 0).toFixed(2);
    document.getElementById("new-booking-confirmed").checked = Boolean(booking.confirmed);
    document.getElementById("new-booking-cancelled").checked = Boolean(booking.cancelled);

    setBookingFormMode(true);
    updateBookingCampaignCreateBox();
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
        tr.setAttribute("data-booking-row-id", String(booking.id));
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

function applyDefaultBookingPriceFromLocation() {
    const locationInput = document.getElementById("new-booking-location");
    const priceInput = document.getElementById("new-booking-price");
    if (!locationInput || !priceInput) {
        return;
    }

    const selectedLocation = findLocationByInputValue(locationInput.value);
    if (!selectedLocation) {
        priceInput.value = "0.00";
        return;
    }

    if (locationInput.value !== selectedLocation.name) {
        locationInput.value = selectedLocation.name;
    }

    if (selectedLocation.price == null) {
        priceInput.value = "0.00";
        return;
    }

    priceInput.value = Number(selectedLocation.price).toFixed(2);
}

function updateBookingCampaignCreateBox() {
    const campaignInput = document.getElementById("new-booking-campaign");
    const box = document.getElementById("booking-campaign-create-box");
    const nameInput = document.getElementById("new-campaign-name");
    const yearInput = document.getElementById("new-campaign-year");
    const budgetInput = document.getElementById("new-campaign-budget");
    const userInput = document.getElementById("new-campaign-user");
    const saveMsg = document.getElementById("new-campaign-save-msg");
    const bookingUserInput = document.getElementById("new-booking-user");
    const bookingDateInput = document.getElementById("new-booking-date");
    if (!campaignInput || !box || !nameInput || !yearInput || !budgetInput || !userInput) {
        return;
    }

    const campaignName = String(campaignInput.value || "").trim();
    const selectedCampaign = findCampaignByInputValue(campaignName);
    const shouldShow = campaignName !== "" && !selectedCampaign;
    box.classList.toggle("hidden", !shouldShow);
    nameInput.readOnly = shouldShow;

    if (shouldShow) {
        nameInput.value = parseCampaignInput(campaignName).name;
        if (!yearInput.value) {
            const bookingDate = String(bookingDateInput?.value || "");
            const y = bookingDate.length >= 4 ? Number(bookingDate.slice(0, 4)) : new Date().getFullYear();
            yearInput.value = Number.isNaN(y) ? String(new Date().getFullYear()) : String(y);
        }
        if (!budgetInput.value) {
            budgetInput.value = "0.00";
        }
        if (!userInput.value && bookingUserInput?.value) {
            userInput.value = bookingUserInput.value;
        }
    } else {
        yearInput.value = "";
        budgetInput.value = "";
        userInput.value = "";
        if (saveMsg) {
            saveMsg.textContent = "";
        }
    }
}

let bookingValidationTimer = null;
let bookingValidationRequestId = 0;

function setBookingLiveLimitError(message) {
    const msgEl = document.getElementById("booking-live-limit-error");
    if (msgEl) {
        msgEl.textContent = String(message || "");
    }
    const saveBtn = document.getElementById("booking-save-btn");
    if (saveBtn) {
        saveBtn.disabled = Boolean(message);
    }
}

function buildBookingValidationPayload() {
    const selectedLocation = findLocationByInputValue(document.getElementById("new-booking-location")?.value || "");
    const eventDate = String(document.getElementById("new-booking-date")?.value || "").trim();
    if (!eventDate || !selectedLocation) {
        return null;
    }

    const payload = {
        date_of_event: eventDate,
        location_id: selectedLocation.id,
    };
    if (bookingEditId != null) {
        payload.booking_id = bookingEditId;
    }
    const selectedCampaign = findCampaignByInputValue(document.getElementById("new-booking-campaign")?.value || "");
    if (selectedCampaign) {
        payload.campaign_id = selectedCampaign.id;
    }
    return payload;
}

async function runBookingLiveValidation() {
    const payload = buildBookingValidationPayload();
    if (!payload) {
        setBookingLiveLimitError("");
        return;
    }
    const requestId = ++bookingValidationRequestId;
    try {
        const response = await fetch(`${API_BASE}/api/bookings/validate-limits`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        if (requestId !== bookingValidationRequestId) {
            return;
        }
        if (!response.ok) {
            const err = await response.json().catch(() => ({}));
            setBookingLiveLimitError(String(err.error || "Buchung nicht gueltig."));
            return;
        }
        setBookingLiveLimitError("");
    } catch (error) {
        if (requestId !== bookingValidationRequestId) {
            return;
        }
        setBookingLiveLimitError(String(error.message || error));
    }
}

function scheduleBookingLiveValidation() {
    if (bookingValidationTimer) {
        clearTimeout(bookingValidationTimer);
    }
    bookingValidationTimer = setTimeout(() => {
        runBookingLiveValidation();
    }, 250);
}

function wireBookingForm() {
    const bookingForm = document.getElementById("booking-create-form");
    const bookingError = document.getElementById("booking-create-error");
    const bookingLocation = document.getElementById("new-booking-location");
    const bookingCampaignInput = document.getElementById("new-booking-campaign");
    const bookingDateInput = document.getElementById("new-booking-date");
    const bookingUserInput = document.getElementById("new-booking-user");
    const bookingClose = document.getElementById("booking-close-btn");
    const campaignSaveBtn = document.getElementById("new-campaign-save-btn");
    const campaignSaveMsg = document.getElementById("new-campaign-save-msg");

    if (bookingLocation) {
        bookingLocation.addEventListener("change", () => {
            applyDefaultBookingPriceFromLocation();
            scheduleBookingLiveValidation();
        });
        bookingLocation.addEventListener("input", scheduleBookingLiveValidation);
    }

    if (bookingCampaignInput) {
        bookingCampaignInput.addEventListener("blur", updateBookingCampaignCreateBox);
        bookingCampaignInput.addEventListener("blur", scheduleBookingLiveValidation);
        bookingCampaignInput.addEventListener("input", scheduleBookingLiveValidation);
    }
    if (bookingDateInput) {
        bookingDateInput.addEventListener("change", updateBookingCampaignCreateBox);
        bookingDateInput.addEventListener("change", scheduleBookingLiveValidation);
        bookingDateInput.addEventListener("input", scheduleBookingLiveValidation);
    }
    if (bookingUserInput) {
        bookingUserInput.addEventListener("change", updateBookingCampaignCreateBox);
        bookingUserInput.addEventListener("change", scheduleBookingLiveValidation);
        bookingUserInput.addEventListener("input", scheduleBookingLiveValidation);
    }

    if (bookingClose) {
        bookingClose.addEventListener("click", () => {
            closeBookingEditMode();
            setBookingLiveLimitError("");
        });
    }

    const bookingPriceInput = document.getElementById("new-booking-price");
    const campaignYearInput = document.getElementById("new-campaign-year");
    const campaignBudgetInput = document.getElementById("new-campaign-budget");
    const campaignUserInput = document.getElementById("new-campaign-user");
    [bookingPriceInput, campaignYearInput, campaignBudgetInput, campaignUserInput].forEach(el => {
        if (!el) {
            return;
        }
        el.addEventListener("input", scheduleBookingLiveValidation);
        el.addEventListener("change", scheduleBookingLiveValidation);
    });

    if (campaignSaveBtn) {
        campaignSaveBtn.addEventListener("click", async () => {
            if (campaignSaveMsg) {
                campaignSaveMsg.textContent = "";
            }

            const campaignInputValue = String(document.getElementById("new-booking-campaign")?.value || "").trim();
            const parsedCampaignInput = parseCampaignInput(campaignInputValue);
            const campaignYearRaw = String(document.getElementById("new-campaign-year")?.value || "").trim();
            const campaignBudgetRaw = String(document.getElementById("new-campaign-budget")?.value || "").trim();
            const campaignUserName = String(document.getElementById("new-campaign-user")?.value || "").trim();

            if (!parsedCampaignInput.name) {
                if (campaignSaveMsg) {
                    campaignSaveMsg.textContent = "Bitte Kampagne eingeben.";
                }
                return;
            }
            if (findCampaignByInputValue(campaignInputValue)) {
                if (campaignSaveMsg) {
                    campaignSaveMsg.textContent = "Kampagne existiert bereits.";
                }
                updateBookingCampaignCreateBox();
                return;
            }
            if (!campaignYearRaw) {
                if (campaignSaveMsg) {
                    campaignSaveMsg.textContent = "Bitte Jahr fuer die neue Kampagne eingeben.";
                }
                return;
            }
            if (!campaignBudgetRaw) {
                if (campaignSaveMsg) {
                    campaignSaveMsg.textContent = "Bitte Budget fuer die neue Kampagne eingeben (0 erlaubt).";
                }
                return;
            }

            const campaignUser = findItemByName(meta.users || [], campaignUserName);
            if (!campaignUser) {
                if (campaignSaveMsg) {
                    campaignSaveMsg.textContent = "Bitte Kampagnen-Benutzer aus der Vorschlagsliste waehlen.";
                }
                return;
            }

            try {
                const response = await fetch(`${API_BASE}/api/campaigns`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        name: parsedCampaignInput.name,
                        year: Number(campaignYearRaw),
                        budget: Number(campaignBudgetRaw),
                        user_id: campaignUser.id
                    })
                });
                if (!response.ok) {
                    const err = await response.json().catch(() => ({}));
                    throw new Error(err.error || "Kampagne konnte nicht gespeichert werden");
                }

                const result = await response.json().catch(() => ({}));
                const savedName = String(result.name || parsedCampaignInput.name).trim();
                const savedId = Number(result.id);
                const savedYear = Number(result.year ?? campaignYearRaw);
                const savedBudget = Number(result.budget ?? campaignBudgetRaw);
                const existingCampaign = (meta.campaigns || []).find(item =>
                    normalizeText(item.name) === normalizeText(savedName)
                    && Number(item.year) === Number(savedYear)
                );
                if (!existingCampaign) {
                    meta.campaigns.push({
                        id: Number.isFinite(savedId) ? savedId : null,
                        name: savedName,
                        year: Number.isFinite(savedYear) ? savedYear : null,
                        budget: Number.isFinite(savedBudget) ? savedBudget : 0
                    });
                }
                fillDatalist("new-booking-campaign-list", meta.campaigns || []);
                const campaignInput = document.getElementById("new-booking-campaign");
                if (campaignInput) {
                    campaignInput.value = formatCampaignDisplay({
                        name: savedName,
                        year: savedYear
                    });
                }
                updateBookingCampaignCreateBox();
                if (campaignSaveMsg) {
                    campaignSaveMsg.textContent = "Kampagne gespeichert.";
                }
                scheduleBookingLiveValidation();
            } catch (error) {
                if (campaignSaveMsg) {
                    campaignSaveMsg.textContent = String(error.message || error);
                }
            }
        });
    }

    if (bookingForm) {
        bookingForm.addEventListener("submit", async event => {
            event.preventDefault();
            bookingError.textContent = "";
            if (document.getElementById("booking-save-btn")?.disabled) {
                return;
            }

            const selectedLocation = findLocationByInputValue(document.getElementById("new-booking-location")?.value || "");
            const selectedCampaign = findCampaignByInputValue(document.getElementById("new-booking-campaign")?.value || "");
            const selectedUser = findItemByName(meta.users || [], document.getElementById("new-booking-user")?.value || "");
            const missingRefs = [];
            if (!selectedLocation) {
                missingRefs.push("Standplatz");
            }
            if (!selectedUser) {
                missingRefs.push("Benutzer");
            }
            if (missingRefs.length > 0) {
                bookingError.textContent = `Bitte ${missingRefs.join(" und ")} aus der Vorschlagsliste waehlen.`;
                return;
            }

            const campaignInputValue = String(document.getElementById("new-booking-campaign")?.value || "").trim();
            const parsedCampaignInput = parseCampaignInput(campaignInputValue);
            if (!parsedCampaignInput.name) {
                bookingError.textContent = "Bitte Kampagne eingeben.";
                return;
            }

            const payload = {
                date_of_event: document.getElementById("new-booking-date")?.value || "",
                price: document.getElementById("new-booking-price")?.value || "",
                location_id: selectedLocation.id,
                user_id: selectedUser.id,
                confirmed: Boolean(document.getElementById("new-booking-confirmed")?.checked),
                cancelled: Boolean(document.getElementById("new-booking-cancelled")?.checked)
            };
            if (selectedCampaign) {
                payload.campaign_id = selectedCampaign.id;
            } else {
                const campaignName = parsedCampaignInput.name;
                const campaignYearRaw = String(document.getElementById("new-campaign-year")?.value || "").trim();
                const campaignBudgetRaw = String(document.getElementById("new-campaign-budget")?.value || "").trim();
                const campaignUserName = String(document.getElementById("new-campaign-user")?.value || "").trim();

                if (!campaignName) {
                    bookingError.textContent = "Bitte Namen fuer die neue Kampagne eingeben.";
                    return;
                }
                if (!campaignYearRaw) {
                    bookingError.textContent = "Bitte Jahr fuer die neue Kampagne eingeben.";
                    return;
                }
                if (!campaignBudgetRaw) {
                    bookingError.textContent = "Bitte Budget fuer die neue Kampagne eingeben (0 erlaubt).";
                    return;
                }

                const campaignUser = findItemByName(meta.users || [], campaignUserName);
                if (!campaignUser) {
                    bookingError.textContent = "Bitte Kampagnen-Benutzer aus der Vorschlagsliste waehlen.";
                    return;
                }

                payload.campaign_name = campaignName;
                payload.create_campaign_if_missing = true;
                payload.campaign_year = Number(campaignYearRaw);
                payload.campaign_budget = Number(campaignBudgetRaw);
                payload.campaign_user_id = campaignUser.id;
            }

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
                setBookingLiveLimitError("");
            } catch (error) {
                bookingError.textContent = String(error.message || error);
            }
        });
    }

    scheduleBookingLiveValidation();
}
