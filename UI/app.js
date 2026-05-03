const apiBase = window.__API_BASE__ || "";

const statusEl = document.getElementById("status");
const bookingRows = document.getElementById("booking-rows");
const campaignOwner = document.getElementById("campaign-owner");
const bookingLocation = document.getElementById("booking-location");
const bookingCampaign = document.getElementById("booking-campaign");
const bookingUser = document.getElementById("booking-user");

const userForm = document.getElementById("user-form");
const locationForm = document.getElementById("location-form");
const campaignForm = document.getElementById("campaign-form");
const bookingForm = document.getElementById("booking-form");

function setStatus(message, tone = "") {
    if (!statusEl) {
        return;
    }
    statusEl.textContent = message;
    statusEl.dataset.tone = tone;
}

async function request(path, options = {}) {
    const response = await fetch(`${apiBase}${path}`, {
        headers: {
            "Content-Type": "application/json",
        },
        ...options,
    });
    if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        const message = body.detail || body.error || "Unbekannter Fehler";
        throw new Error(message);
    }
    return response.json();
}

function fillSelect(select, items, labelBuilder) {
    select.innerHTML = "";
    items.forEach((item) => {
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = labelBuilder(item);
        select.appendChild(option);
    });
}

function renderBookings(bookings, users, campaigns, locations) {
    if (!bookingRows) {
        return;
    }
    bookingRows.innerHTML = "";
    bookings.forEach((booking) => {
        const row = document.createElement("tr");
        const user = users.find((item) => item.id === booking.user_id);
        const campaign = campaigns.find((item) => item.id === booking.campaign_id);
        const location = locations.find((item) => item.id === booking.location_id);
        row.innerHTML = `
            <td>${booking.id}</td>
            <td>${booking.event_date}</td>
            <td>${booking.status}</td>
            <td>${booking.price.toFixed(2)}</td>
            <td>${location ? location.name : "-"}</td>
            <td>${campaign ? campaign.name : "-"}</td>
            <td>${user ? user.name : "-"}</td>
        `;
        bookingRows.appendChild(row);
    });
}

async function loadAll() {
    const [users, locations, campaigns, bookings] = await Promise.all([
        request("/api/users"),
        request("/api/locations"),
        request("/api/campaigns"),
        request("/api/bookings"),
    ]);

    fillSelect(campaignOwner, users, (user) => `${user.name} (${user.email})`);
    fillSelect(bookingUser, users, (user) => user.name);
    fillSelect(bookingLocation, locations, (location) => `${location.name} - ${location.city}`);
    fillSelect(bookingCampaign, campaigns, (campaign) => `${campaign.name} (${campaign.year})`);

    renderBookings(bookings, users, campaigns, locations);
}

async function handleSubmit(form, handler) {
    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        setStatus("");
        try {
            await handler(new FormData(form));
            form.reset();
            await loadAll();
            setStatus("Gespeichert.", "success");
        } catch (error) {
            setStatus(error.message, "error");
        }
    });
}

handleSubmit(userForm, async (data) => {
    await request("/api/users", {
        method: "POST",
        body: JSON.stringify({
            name: data.get("name"),
            email: data.get("email"),
            phone: data.get("phone") || null,
            address: data.get("address") || null,
        }),
    });
});

handleSubmit(locationForm, async (data) => {
    await request("/api/locations", {
        method: "POST",
        body: JSON.stringify({
            name: data.get("name"),
            city: data.get("city"),
            price: Number(data.get("price")),
        }),
    });
});

handleSubmit(campaignForm, async (data) => {
    await request("/api/campaigns", {
        method: "POST",
        body: JSON.stringify({
            name: data.get("name"),
            year: Number(data.get("year")),
            budget: Number(data.get("budget")),
            owner_id: Number(data.get("owner_id")),
        }),
    });
});

handleSubmit(bookingForm, async (data) => {
    await request("/api/bookings", {
        method: "POST",
        body: JSON.stringify({
            event_date: data.get("event_date"),
            price: Number(data.get("price")),
            status: data.get("status"),
            location_id: Number(data.get("location_id")),
            campaign_id: Number(data.get("campaign_id")),
            user_id: Number(data.get("user_id")),
        }),
    });
});

loadAll().catch((error) => {
    setStatus(error.message || "Fehler beim Laden.", "error");
});
