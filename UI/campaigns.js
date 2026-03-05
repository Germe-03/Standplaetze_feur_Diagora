let campaignEditId = null;

function isCampaignActive(campaign) {
    const value = campaign?.is_active;
    if (value === false || value === 0 || value === "0") {
        return false;
    }
    return true;
}

function setCampaignFormMode(isEdit) {
    const title = document.getElementById("campaign-form-title");
    const idLabel = document.getElementById("campaign-form-id-label");
    const saveBtn = document.getElementById("campaign-save-btn");
    const cancelBtn = document.getElementById("campaign-cancel-btn");
    const deleteBtn = document.getElementById("campaign-delete-btn");
    if (title) {
        title.textContent = isEdit ? "Kampagne bearbeiten" : "Neue Kampagne";
        if (idLabel) {
            title.appendChild(idLabel);
        }
    }
    if (idLabel) {
        idLabel.textContent = isEdit ? `(#${campaignEditId})` : "";
    }
    // In create mode save stays enabled.
    if (saveBtn) {
        saveBtn.disabled = false;
    }
    if (cancelBtn) {
        cancelBtn.classList.toggle("hidden", !isEdit);
    }
    if (deleteBtn) {
        deleteBtn.classList.toggle("hidden", !isEdit);
    }
}

function closeCampaignEditMode() {
    campaignEditId = null;
    const form = document.getElementById("campaign-edit-form");
    if (form) {
        form.reset();
    }
    const errorEl = document.getElementById("campaign-edit-error");
    if (errorEl) {
        errorEl.textContent = "";
    }
    const yearInput = document.getElementById("campaign-edit-year");
    const budgetInput = document.getElementById("campaign-edit-budget");
    const activeBox = document.getElementById("campaign-edit-active");
    if (yearInput) {
        yearInput.value = String(new Date().getFullYear());
    }
    if (budgetInput) {
        budgetInput.value = "0.00";
    }
    if (activeBox) {
        activeBox.checked = true;
    }
    setCampaignFormMode(false);
}

function startCampaignEdit(campaignId) {
    const campaign = (campaigns || []).find(item => Number(item.id) === Number(campaignId));
    if (!campaign) {
        return;
    }
    campaignEditId = Number(campaign.id);
    document.getElementById("campaign-edit-name").value = campaign.name || "";
    document.getElementById("campaign-edit-year").value = campaign.year ?? "";
    document.getElementById("campaign-edit-budget").value = Number(campaign.budget || 0).toFixed(2);
    document.getElementById("campaign-edit-user").value = campaign.user_name || "";
    const activeBox = document.getElementById("campaign-edit-active");
    if (activeBox) {
        activeBox.checked = isCampaignActive(campaign);
    }
    setCampaignFormMode(true);
}

function initCampaignUserDatalist() {
    fillDatalist("campaign-user-list", meta.users || []);
}

function initCampaignFilters() {
    const yearSelect = document.getElementById("campaign-filter-year");
    const userSelect = document.getElementById("campaign-filter-user");
    if (!yearSelect || !userSelect) {
        return;
    }

    const years = Array.from(new Set((campaigns || []).map(c => Number(c.year)).filter(v => Number.isFinite(v)))).sort((a, b) => b - a);
    const users = Array.from(new Set((campaigns || []).map(c => String(c.user_name || "").trim()).filter(v => v)));

    const currentYear = yearSelect.value;
    const currentUser = userSelect.value;

    yearSelect.innerHTML = '<option value="">Alle Jahre</option>';
    years.forEach(y => {
        const option = document.createElement("option");
        option.value = String(y);
        option.textContent = String(y);
        yearSelect.appendChild(option);
    });

    userSelect.innerHTML = '<option value="">Alle Benutzer</option>';
    users.sort((a, b) => a.localeCompare(b, "de", { sensitivity: "base" })).forEach(user => {
        const option = document.createElement("option");
        option.value = user;
        option.textContent = user;
        userSelect.appendChild(option);
    });

    if (currentYear && Array.from(yearSelect.options).some(o => o.value === currentYear)) {
        yearSelect.value = currentYear;
    }
    if (currentUser && Array.from(userSelect.options).some(o => o.value === currentUser)) {
        userSelect.value = currentUser;
    }
}

function getFilteredCampaigns() {
    const query = String(document.getElementById("campaign-search")?.value || "").trim().toLowerCase();
    const yearFilter = String(document.getElementById("campaign-filter-year")?.value || "").trim();
    const userFilter = String(document.getElementById("campaign-filter-user")?.value || "").trim();
    const activeFilter = String(document.getElementById("campaign-filter-active")?.value || "active").trim();

    return (campaigns || [])
        .filter(campaign => {
            if (yearFilter && String(campaign.year) !== yearFilter) {
                return false;
            }
            if (userFilter && String(campaign.user_name || "") !== userFilter) {
                return false;
            }
            const isActive = isCampaignActive(campaign);
            if (activeFilter === "active" && !isActive) {
                return false;
            }
            if (activeFilter === "inactive" && isActive) {
                return false;
            }
            if (!query) {
                return true;
            }
            const hay = `${campaign.name || ""} ${campaign.user_name || ""}`.toLowerCase();
            return hay.includes(query);
        })
        .sort((a, b) => compareValues(Number(a.id || 0), Number(b.id || 0), "asc"));
}

function renderCampaigns() {
    initCampaignUserDatalist();
    initCampaignFilters();
    const body = document.getElementById("campaign-rows");
    if (!body) {
        return;
    }
    body.innerHTML = "";
    const rows = getFilteredCampaigns();
    rows.forEach(campaign => {
        const tr = document.createElement("tr");
        tr.style.cursor = "pointer";
        tr.title = "Doppelklick zum Bearbeiten";
        tr.innerHTML = `
            <td>#${campaign.id}</td>
            <td>${campaign.name || "-"}</td>
            <td>${campaign.year ?? "-"}</td>
            <td>CHF ${Number(campaign.budget || 0).toFixed(2)}</td>
            <td>${campaign.user_name || "-"}</td>
            <td>${isCampaignActive(campaign) ? "Ja" : "Nein"}</td>
        `;
        tr.addEventListener("dblclick", () => startCampaignEdit(campaign.id));
        body.appendChild(tr);
    });
}

function wireCampaignsManagement() {
    setCampaignFormMode(false);

    const search = document.getElementById("campaign-search");
    const yearFilter = document.getElementById("campaign-filter-year");
    const userFilter = document.getElementById("campaign-filter-user");
    const activeFilter = document.getElementById("campaign-filter-active");
    if (activeFilter && !activeFilter.value) {
        activeFilter.value = "active";
    }
    [search, yearFilter, userFilter, activeFilter].forEach(el => {
        if (!el) {
            return;
        }
        el.addEventListener("input", renderCampaigns);
        el.addEventListener("change", renderCampaigns);
    });

    const cancelBtn = document.getElementById("campaign-cancel-btn");
    if (cancelBtn) {
        cancelBtn.addEventListener("click", () => {
            closeCampaignEditMode();
        });
    }
    const form = document.getElementById("campaign-edit-form");
    const errorEl = document.getElementById("campaign-edit-error");
    if (!form || !errorEl) {
        return;
    }
    const deleteBtn = document.getElementById("campaign-delete-btn");
    if (deleteBtn) {
        deleteBtn.addEventListener("click", async () => {
            if (campaignEditId == null) {
                return;
            }
            const yes = window.confirm("Kampagne wirklich loeschen?");
            if (!yes) {
                return;
            }
            errorEl.textContent = "";
            try {
                const response = await fetch(`${API_BASE}/api/campaigns/${campaignEditId}`, { method: "DELETE" });
                if (!response.ok) {
                    const err = await response.json().catch(() => null);
                    const fallback = `HTTP ${response.status} beim Loeschen.`;
                    throw new Error((err && err.error) ? err.error : fallback);
                }
                await Promise.all([loadCampaignsFromApi(), loadMeta(), loadBookingsFromApi()]);
                closeCampaignEditMode();
            } catch (error) {
                errorEl.textContent = String(error.message || error);
            }
        });
    }

    form.addEventListener("submit", async event => {
        event.preventDefault();
        errorEl.textContent = "";

        const userName = String(document.getElementById("campaign-edit-user")?.value || "").trim();
        const user = findItemByName(meta.users || [], userName);
        if (!user) {
            errorEl.textContent = "Bitte Benutzer aus der Vorschlagsliste waehlen.";
            return;
        }

        const payload = {
            name: String(document.getElementById("campaign-edit-name")?.value || "").trim(),
            year: Number(document.getElementById("campaign-edit-year")?.value || ""),
            budget: Number(document.getElementById("campaign-edit-budget")?.value || ""),
            user_id: user.id,
            is_active: Boolean(document.getElementById("campaign-edit-active")?.checked),
        };
        if (!payload.name) {
            errorEl.textContent = "Bitte Kampagnennamen eingeben.";
            return;
        }
        if (!Number.isFinite(payload.year)) {
            errorEl.textContent = "Bitte gueltiges Jahr eingeben.";
            return;
        }
        if (!Number.isFinite(payload.budget)) {
            errorEl.textContent = "Bitte gueltiges Budget eingeben.";
            return;
        }

        try {
            const isEdit = campaignEditId != null;
            const response = await fetch(isEdit ? `${API_BASE}/api/campaigns/${campaignEditId}` : `${API_BASE}/api/campaigns`, {
                method: isEdit ? "PUT" : "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload),
            });
            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.error || "Kampagne konnte nicht gespeichert werden.");
            }
            await Promise.all([loadCampaignsFromApi(), loadMeta(), loadBookingsFromApi()]);
            closeCampaignEditMode();
        } catch (error) {
            errorEl.textContent = String(error.message || error);
        }
    });

    closeCampaignEditMode();
}
