document.addEventListener("DOMContentLoaded", () => {
    setBookingFormMode(false);
    setStandFormMode(false);
    installDashboardChartsFallback();
    initDashboardYearOptions();
    initDashboardMonthOptions();

    wireTabs();
    wireSorting();
    wireColumnFilterPopover();
    wireCalendarControls();
    wireBookingForm();
    wireStandsForm();
    wireCampaignsManagement();
    wireUsersManagement();

    const dashboardYear = document.getElementById("dashboard-year");
    const dashboardMonth = document.getElementById("dashboard-month");
    const dashboardCampaignYear = document.getElementById("dashboard-campaign-year");
    const dashboardCampaignMonth = document.getElementById("dashboard-campaign-month");
    if (dashboardYear) {
        dashboardYear.addEventListener("change", () => {
            initDashboardMonthOptions();
            initDashboardChartPeriodOptions();
            renderDashboardFromBookings();
        });
    }
    if (dashboardMonth) {
        dashboardMonth.addEventListener("change", () => {
            renderDashboardFromBookings();
        });
    }
    if (dashboardCampaignYear) {
        dashboardCampaignYear.addEventListener("change", () => {
            renderDashboardFromBookings();
        });
    }
    if (dashboardCampaignMonth) {
        dashboardCampaignMonth.addEventListener("change", () => {
            renderDashboardFromBookings();
        });
    }
    const dashboardChartPeriod = document.getElementById("dashboard-chart-period");
    if (dashboardChartPeriod) {
        dashboardChartPeriod.addEventListener("change", () => {
            renderDashboardCharts();
        });
    }
    const dashboardChartCampaign = document.getElementById("dashboard-chart-campaign");
    if (dashboardChartCampaign) {
        dashboardChartCampaign.addEventListener("change", () => {
            renderDashboardCharts();
        });
    }

    window.addEventListener("resize", () => {
        renderDashboardCharts();
    });

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
