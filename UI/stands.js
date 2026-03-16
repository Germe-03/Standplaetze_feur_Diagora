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

function wireStandsForm() {
    const standForm = document.getElementById("stand-create-form");
    const standError = document.getElementById("stand-create-error");
    const standCityInput = document.getElementById("new-stand-city");
    const standClose = document.getElementById("stand-close-btn");
    const standDelete = document.getElementById("stand-delete-btn");

    if (standCityInput) {
        standCityInput.addEventListener("input", updateStandCityRequirement);
        standCityInput.addEventListener("change", updateStandCityRequirement);
    }

    if (standClose) {
        standClose.addEventListener("click", () => {
            closeStandEditMode();
        });
    }
    if (standDelete) {
        standDelete.addEventListener("click", async () => {
            if (standEditId == null) {
                return;
            }
            const yes = window.confirm("Standplatz wirklich loeschen?");
            if (!yes) {
                return;
            }
            standError.textContent = "";
            try {
                const response = await fetch(`${API_BASE}/api/stands/${standEditId}`, { method: "DELETE" });
                if (!response.ok) {
                    const err = await response.json().catch(() => null);
                    const fallback = `HTTP ${response.status} beim Loeschen.`;
                    throw new Error((err && err.error) ? err.error : fallback);
                }
                await Promise.all([loadMeta(), loadStandsFromApi(), loadBookingsFromApi()]);
                closeStandEditMode();
            } catch (error) {
                standError.textContent = String(error.message || error);
            }
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
