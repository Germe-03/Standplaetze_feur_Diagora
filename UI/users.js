let userEditId = null;

function normalizeRole(role) {
    const value = String(role || "").trim().toLowerCase();
    if (value === "admin") {
        return "Admin";
    }
    if (value === "user") {
        return "User";
    }
    if (value === "viewer") {
        return "Viewer";
    }
    return String(role || "").trim();
}

function roleLabel(role) {
    const normalized = normalizeRole(role);
    if (normalized === "Admin") {
        return "Admin";
    }
    if (normalized === "User") {
        return "Benutzer";
    }
    if (normalized === "Viewer") {
        return "Betrachter";
    }
    return normalized || "-";
}

function setUserFormMode(isEdit) {
    const title = document.getElementById("user-form-title");
    const idLabel = document.getElementById("user-form-id-label");
    const cancelBtn = document.getElementById("user-cancel-btn");
    const deleteBtn = document.getElementById("user-delete-btn");
    const passwordLabel = document.querySelector('label[for="user-edit-password"]');
    if (title) {
        title.textContent = isEdit ? "Nutzer bearbeiten" : "Neuer Nutzer";
        if (idLabel) {
            title.appendChild(idLabel);
        }
    }
    if (idLabel) {
        idLabel.textContent = isEdit ? `(#${userEditId})` : "";
    }
    if (cancelBtn) {
        cancelBtn.classList.toggle("hidden", !isEdit);
    }
    if (deleteBtn) {
        deleteBtn.classList.toggle("hidden", !isEdit);
    }
    if (passwordLabel) {
        passwordLabel.textContent = isEdit ? "Passwort (leer lassen = unveraendert)" : "Passwort";
    }
}

function closeUserEditMode() {
    userEditId = null;
    const form = document.getElementById("user-edit-form");
    if (form) {
        form.reset();
    }
    const errorEl = document.getElementById("user-edit-error");
    if (errorEl) {
        errorEl.textContent = "";
    }
    const activeBox = document.getElementById("user-edit-active");
    const roleInput = document.getElementById("user-edit-role");
    if (activeBox) {
        activeBox.checked = true;
    }
    if (roleInput) {
        roleInput.value = "User";
    }
    setUserFormMode(false);
}

function startUserEdit(userId) {
    const user = (usersAdmin || []).find(item => Number(item.id) === Number(userId));
    if (!user) {
        return;
    }
    userEditId = Number(user.id);
    document.getElementById("user-edit-first-name").value = user.first_name || "";
    document.getElementById("user-edit-last-name").value = user.last_name || "";
    document.getElementById("user-edit-email").value = user.email || "";
    document.getElementById("user-edit-phone").value = user.phone || "";
    document.getElementById("user-edit-address-street").value = user.address_street || "";
    document.getElementById("user-edit-address-number").value = user.address_number || "";
    document.getElementById("user-edit-address-zip").value = user.address_zip || "";
    document.getElementById("user-edit-address-city").value = user.address_city || "";
    document.getElementById("user-edit-address-state").value = user.address_state || "";
    document.getElementById("user-edit-role").value = normalizeRole(user.role) || "User";
    document.getElementById("user-edit-password").value = "";
    const activeBox = document.getElementById("user-edit-active");
    if (activeBox) {
        activeBox.checked = Boolean(user.is_active);
    }
    setUserFormMode(true);
}

function initUserRoleFilter() {
    const roleFilter = document.getElementById("user-filter-role");
    if (!roleFilter) {
        return;
    }

    const roles = Array.from(
        new Set((usersAdmin || []).map(user => normalizeRole(user.role)).filter(value => value))
    ).sort((a, b) => a.localeCompare(b, "de", { sensitivity: "base" }));

    const currentRole = roleFilter.value;
    roleFilter.innerHTML = '<option value="">Alle Rollen</option>';
    roles.forEach(role => {
        const option = document.createElement("option");
        option.value = role;
        option.textContent = roleLabel(role);
        roleFilter.appendChild(option);
    });

    if (currentRole && Array.from(roleFilter.options).some(option => option.value === currentRole)) {
        roleFilter.value = currentRole;
    }
}

function getFilteredUsersAdmin() {
    const query = String(document.getElementById("user-search")?.value || "").trim().toLowerCase();
    const roleFilter = String(document.getElementById("user-filter-role")?.value || "").trim();
    const activeFilter = String(document.getElementById("user-filter-active")?.value || "active").trim();

    return (usersAdmin || [])
        .filter(user => {
            if (roleFilter && normalizeRole(user.role) !== roleFilter) {
                return false;
            }
            const isActive = Boolean(user.is_active);
            if (activeFilter === "active" && !isActive) {
                return false;
            }
            if (activeFilter === "inactive" && isActive) {
                return false;
            }
            if (!query) {
                return true;
            }
            const hay = `${user.first_name || ""} ${user.last_name || ""} ${user.full_name || ""} ${roleLabel(user.role)}`.toLowerCase();
            return hay.includes(query);
        })
        .sort((a, b) => compareValues(Number(a.id || 0), Number(b.id || 0), "asc"));
}

function renderUsersAdmin() {
    initUserRoleFilter();
    const body = document.getElementById("user-rows");
    if (!body) {
        return;
    }
    body.innerHTML = "";
    const rows = getFilteredUsersAdmin();
    rows.forEach(user => {
        const tr = document.createElement("tr");
        tr.style.cursor = "pointer";
        tr.title = "Doppelklick zum Bearbeiten";
        tr.innerHTML = `
            <td>#${user.id}</td>
            <td>${user.first_name || "-"}</td>
            <td>${user.last_name || "-"}</td>
            <td>${roleLabel(user.role)}</td>
            <td>${user.is_active ? "Ja" : "Nein"}</td>
            <td>${user.full_name || "-"}</td>
        `;
        tr.addEventListener("dblclick", () => startUserEdit(user.id));
        body.appendChild(tr);
    });
}

function wireUsersManagement() {
    setUserFormMode(false);

    const search = document.getElementById("user-search");
    const roleFilter = document.getElementById("user-filter-role");
    const activeFilter = document.getElementById("user-filter-active");
    if (activeFilter && !activeFilter.value) {
        activeFilter.value = "active";
    }
    if (roleFilter && !roleFilter.value) {
        roleFilter.value = "";
    }
    [search, roleFilter, activeFilter].forEach(el => {
        if (!el) {
            return;
        }
        el.addEventListener("input", renderUsersAdmin);
        el.addEventListener("change", renderUsersAdmin);
    });

    const cancelBtn = document.getElementById("user-cancel-btn");
    if (cancelBtn) {
        cancelBtn.addEventListener("click", () => {
            closeUserEditMode();
        });
    }
    const form = document.getElementById("user-edit-form");
    const errorEl = document.getElementById("user-edit-error");
    if (!form || !errorEl) {
        return;
    }
    const deleteBtn = document.getElementById("user-delete-btn");
    if (deleteBtn) {
        deleteBtn.addEventListener("click", async () => {
            if (userEditId == null) {
                return;
            }
            const yes = window.confirm("Nutzer wirklich loeschen?");
            if (!yes) {
                return;
            }
            errorEl.textContent = "";
            try {
                const response = await fetch(`${API_BASE}/api/users/${userEditId}`, { method: "DELETE" });
                if (!response.ok) {
                    const err = await response.json().catch(() => null);
                    const fallback = `HTTP ${response.status} beim Loeschen.`;
                    throw new Error((err && err.error) ? err.error : fallback);
                }
                await Promise.all([loadUsersAdminFromApi(), loadMeta(), loadCampaignsFromApi(), loadBookingsFromApi(), loadStandsFromApi()]);
                closeUserEditMode();
            } catch (error) {
                errorEl.textContent = String(error.message || error);
            }
        });
    }
    form.addEventListener("submit", async event => {
        event.preventDefault();
        errorEl.textContent = "";

        const payload = {
            first_name: String(document.getElementById("user-edit-first-name")?.value || "").trim(),
            last_name: String(document.getElementById("user-edit-last-name")?.value || "").trim(),
            email: String(document.getElementById("user-edit-email")?.value || "").trim(),
            phone: String(document.getElementById("user-edit-phone")?.value || "").trim(),
            address_street: String(document.getElementById("user-edit-address-street")?.value || "").trim(),
            address_number: String(document.getElementById("user-edit-address-number")?.value || "").trim(),
            address_zip: String(document.getElementById("user-edit-address-zip")?.value || "").trim(),
            address_city: String(document.getElementById("user-edit-address-city")?.value || "").trim(),
            address_state: String(document.getElementById("user-edit-address-state")?.value || "").trim(),
            role: String(document.getElementById("user-edit-role")?.value || "").trim(),
            password: String(document.getElementById("user-edit-password")?.value || ""),
            is_active: Boolean(document.getElementById("user-edit-active")?.checked),
        };

        if (!payload.first_name) {
            errorEl.textContent = "Bitte Vorname eingeben.";
            return;
        }
        if (!payload.last_name) {
            errorEl.textContent = "Bitte Nachname eingeben.";
            return;
        }
        if (!payload.email) {
            errorEl.textContent = "Bitte E-Mail eingeben.";
            return;
        }
        if (!payload.email.includes("@") || !payload.email.includes(".")) {
            errorEl.textContent = "Bitte gueltige E-Mail eingeben.";
            return;
        }
        if (!payload.role) {
            errorEl.textContent = "Bitte Rolle eingeben.";
            return;
        }
        payload.role = normalizeRole(payload.role);
        if (userEditId == null && payload.password.length < 4) {
            errorEl.textContent = "Passwort muss mindestens 4 Zeichen haben.";
            return;
        }

        try {
            const isEdit = userEditId != null;
            const requestPayload = isEdit && payload.password.length === 0
                ? {
                    first_name: payload.first_name,
                    last_name: payload.last_name,
                    email: payload.email,
                    phone: payload.phone,
                    address_street: payload.address_street,
                    address_number: payload.address_number,
                    address_zip: payload.address_zip,
                    address_city: payload.address_city,
                    address_state: payload.address_state,
                    role: payload.role,
                    is_active: payload.is_active
                }
                : payload;
            const response = await fetch(isEdit ? `${API_BASE}/api/users/${userEditId}` : `${API_BASE}/api/users`, {
                method: isEdit ? "PUT" : "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(requestPayload),
            });
            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.error || "Nutzer konnte nicht gespeichert werden.");
            }
            await Promise.all([loadUsersAdminFromApi(), loadMeta(), loadCampaignsFromApi()]);
            closeUserEditMode();
        } catch (error) {
            errorEl.textContent = String(error.message || error);
        }
    });

    closeUserEditMode();
}
