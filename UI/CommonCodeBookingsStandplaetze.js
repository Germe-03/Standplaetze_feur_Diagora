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

function fillDatalist(listId, items) {
    const list = document.getElementById(listId);
    if (!list) {
        return;
    }

    list.innerHTML = "";

    items.forEach(item => {
        const option = document.createElement("option");
        option.value = item.name;
        if (listId === "new-booking-location-list") {
            const city = String(item.city || "").trim();
            if (city) {
                const visibleText = `${item.name} (${city})`;
                option.value = visibleText;
                option.label = visibleText;
                option.textContent = visibleText;
            }
        }
        if (listId === "new-booking-campaign-list") {
            const visibleText = formatCampaignDisplay(item);
            option.value = visibleText;
            option.label = visibleText;
            option.textContent = visibleText;
        }
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

function parseCampaignInput(typedValue) {
    const raw = String(typedValue || "").trim();
    if (!raw) {
        return { name: "", year: null };
    }
    const match = raw.match(/^(.*)\s+\((\d{4})\)$/);
    if (!match) {
        return { name: raw, year: null };
    }
    return {
        name: String(match[1] || "").trim(),
        year: Number(match[2])
    };
}

function formatCampaignDisplay(campaign) {
    const name = String(campaign?.name || "").trim();
    const year = Number(campaign?.year);
    if (name && Number.isFinite(year)) {
        return `${name} (${year})`;
    }
    return name;
}

function findCampaignByInputValue(typedValue) {
    const parsed = parseCampaignInput(typedValue);
    if (!parsed.name) {
        return null;
    }
    const campaigns = meta.campaigns || [];
    if (parsed.year != null && Number.isFinite(parsed.year)) {
        return campaigns.find(item =>
            normalizeText(item.name) === normalizeText(parsed.name)
            && Number(item.year) === Number(parsed.year)
        ) || null;
    }
    const byName = campaigns.filter(item => normalizeText(item.name) === normalizeText(parsed.name));
    if (byName.length === 1) {
        return byName[0];
    }
    return null;
}

function findLocationByInputValue(typedValue) {
    const raw = String(typedValue || "").trim();
    if (!raw) {
        return null;
    }

    const direct = findItemByName(meta.locations || [], raw);
    if (direct) {
        return direct;
    }

    const match = raw.match(/^(.*)\s+\((.*)\)$/);
    if (!match) {
        return null;
    }
    const namePart = String(match[1] || "").trim();
    const cityPart = String(match[2] || "").trim();
    if (!namePart) {
        return null;
    }

    return (meta.locations || []).find(item =>
        normalizeText(item.name) === normalizeText(namePart)
        && normalizeText(item.city || "") === normalizeText(cityPart)
    ) || null;
}
