(function () {
    function formatChf(value) {
        return `CHF ${Number(value || 0).toFixed(2)}`;
    }

    function clearCanvas(ctx, width, height) {
        ctx.clearRect(0, 0, width, height);
        ctx.fillStyle = "#ffffff";
        ctx.fillRect(0, 0, width, height);
    }

    function drawAxes(ctx, area) {
        ctx.strokeStyle = "#8fb4dc";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(area.left, area.top);
        ctx.lineTo(area.left, area.bottom);
        ctx.lineTo(area.right, area.bottom);
        ctx.stroke();
    }

    function drawGrid(ctx, area, steps) {
        ctx.strokeStyle = "#d4e6f8";
        ctx.lineWidth = 1;
        for (let i = 1; i <= steps; i++) {
            const y = area.bottom - (i * (area.bottom - area.top) / steps);
            ctx.beginPath();
            ctx.moveTo(area.left, y);
            ctx.lineTo(area.right, y);
            ctx.stroke();
        }
    }

    function drawLine(ctx, points, color) {
        if (points.length === 0) {
            return;
        }
        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        for (let i = 1; i < points.length; i++) {
            ctx.lineTo(points[i].x, points[i].y);
        }
        ctx.stroke();

        ctx.fillStyle = color;
        points.forEach(p => {
            ctx.beginPath();
            ctx.arc(p.x, p.y, 2.6, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    function drawLabels(ctx, labels, area) {
        if (!labels.length) {
            return;
        }
        const stepX = labels.length > 1 ? (area.right - area.left) / (labels.length - 1) : 0;
        ctx.fillStyle = "#406792";
        ctx.font = "11px Manrope, sans-serif";
        ctx.textAlign = "center";
        labels.forEach((label, idx) => {
            const x = area.left + stepX * idx;
            ctx.fillText(String(label), x, area.bottom + 16);
        });
    }

    function drawYAxisValues(ctx, maxValue, area, formatValue) {
        const steps = 4;
        ctx.fillStyle = "#406792";
        ctx.font = "11px Manrope, sans-serif";
        ctx.textAlign = "right";
        for (let i = 0; i <= steps; i++) {
            const value = (maxValue / steps) * i;
            const y = area.bottom - (i * (area.bottom - area.top) / steps);
            ctx.fillText(formatValue(value), area.left - 8, y + 3);
        }
    }

    function buildPoints(values, area, maxValue) {
        if (!values.length) {
            return [];
        }
        const stepX = values.length > 1 ? (area.right - area.left) / (values.length - 1) : 0;
        return values.map((v, idx) => {
            const x = area.left + stepX * idx;
            const ratio = maxValue > 0 ? (Number(v || 0) / maxValue) : 0;
            const y = area.bottom - ratio * (area.bottom - area.top);
            return { x, y };
        });
    }

    function renderLineChart(canvasId, labels, values, options) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            return;
        }

        const dpr = window.devicePixelRatio || 1;
        const rect = canvas.getBoundingClientRect();
        const width = Math.max(320, Math.floor(rect.width || canvas.clientWidth || 640));
        const height = Math.max(220, Math.floor(rect.height || canvas.clientHeight || 260));
        canvas.width = Math.floor(width * dpr);
        canvas.height = Math.floor(height * dpr);

        const ctx = canvas.getContext("2d");
        if (!ctx) {
            return;
        }
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        clearCanvas(ctx, width, height);

        const area = { left: 52, top: 18, right: width - 12, bottom: height - 30 };
        const maxValue = Math.max(1, ...values.map(v => Number(v || 0)));

        drawGrid(ctx, area, 4);
        drawAxes(ctx, area);
        drawYAxisValues(ctx, maxValue, area, options.formatValue);
        drawLabels(ctx, labels, area);
        const points = buildPoints(values, area, maxValue);
        drawLine(ctx, points, options.color || "#2f6fb0");
    }

    window.DashboardCharts = {
        renderCountChart(canvasId, labels, values) {
            renderLineChart(canvasId, labels, values, {
                formatValue: v => String(Math.round(v)),
                color: "#2d66a8"
            });
        },
        renderCostChart(canvasId, labels, values) {
            renderLineChart(canvasId, labels, values, {
                formatValue: v => formatChf(v),
                color: "#3a8db8"
            });
        }
    };
})();
