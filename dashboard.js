/**
 * Student Performance Prediction System
 * Admin Dashboard Chart.js Visualizations
 */

document.addEventListener("DOMContentLoaded", function () {
    fetch("/api/chart-data")
        .then((response) => response.json())
        .then((data) => {
            renderCategoryChart(data.category_distribution);
            renderAttendanceChart(data.attendance_vs_marks);
            renderInternalMarksChart(data.internal_vs_marks);
            renderScoreRangesChart(data.score_ranges);
        })
        .catch((error) => {
            console.error("Failed to load dashboard chart data:", error);
        });
});

/**
 * 1. Category Distribution Doughnut Chart
 */
function renderCategoryChart(catData) {
    const ctx = document.getElementById("categoryChart");
    if (!ctx) return;

    new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: catData.labels,
            datasets: [
                {
                    data: catData.data,
                    backgroundColor: catData.colors,
                    borderColor: "#ffffff",
                    borderWidth: 2,
                    hoverOffset: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: {
                        boxWidth: 12,
                        font: { size: 11, family: "'Plus Jakarta Sans', sans-serif" }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            const val = context.raw || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                            return ` ${context.label}: ${val} students (${pct}%)`;
                        }
                    }
                }
            },
            cutout: "68%"
        }
    });
}

/**
 * 2. Attendance % vs Predicted Marks (Scatter Plot)
 */
function renderAttendanceChart(points) {
    const ctx = document.getElementById("attendanceChart");
    if (!ctx) return;

    new Chart(ctx, {
        type: "scatter",
        data: {
            datasets: [
                {
                    label: "Students",
                    data: points.map((p) => ({ x: p.x, y: p.y, name: p.label, category: p.category })),
                    backgroundColor: points.map((p) => {
                        if (p.category === "Excellent") return "#16a34a";
                        if (p.category === "Good") return "#0284c7";
                        if (p.category === "Average") return "#d97706";
                        return "#dc2626";
                    }),
                    pointRadius: 6,
                    pointHoverRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    min: 30,
                    max: 100,
                    title: {
                        display: true,
                        text: "Attendance Percentage (%)",
                        font: { weight: "600" }
                    },
                    grid: { color: "rgba(0, 0, 0, 0.05)" }
                },
                y: {
                    min: 20,
                    max: 100,
                    title: {
                        display: true,
                        text: "Predicted Marks (0–100)",
                        font: { weight: "600" }
                    },
                    grid: { color: "rgba(0, 0, 0, 0.05)" }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            const raw = ctx.raw;
                            return ` ${raw.name} | Att: ${raw.x}% | Predicted: ${raw.y} (${raw.category})`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * 3. Internal Marks vs Predicted Marks (Scatter Plot)
 */
function renderInternalMarksChart(points) {
    const ctx = document.getElementById("internalMarksChart");
    if (!ctx) return;

    new Chart(ctx, {
        type: "scatter",
        data: {
            datasets: [
                {
                    label: "Students",
                    data: points.map((p) => ({ x: p.x, y: p.y, name: p.label, category: p.category })),
                    backgroundColor: "#1e40af",
                    borderColor: "#3b82f6",
                    pointRadius: 6,
                    pointHoverRadius: 8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    min: 20,
                    max: 100,
                    title: {
                        display: true,
                        text: "Internal Assessment Marks (/100)",
                        font: { weight: "600" }
                    },
                    grid: { color: "rgba(0, 0, 0, 0.05)" }
                },
                y: {
                    min: 20,
                    max: 100,
                    title: {
                        display: true,
                        text: "Predicted Marks (/100)",
                        font: { weight: "600" }
                    },
                    grid: { color: "rgba(0, 0, 0, 0.05)" }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (ctx) {
                            const raw = ctx.raw;
                            return ` ${raw.name} | Internal: ${raw.x} | Predicted: ${raw.y}`;
                        }
                    }
                }
            }
        }
    });
}

/**
 * 4. Score Ranges Distribution Histogram (Bar Chart)
 */
function renderScoreRangesChart(rangeData) {
    const ctx = document.getElementById("scoreRangesChart");
    if (!ctx) return;

    new Chart(ctx, {
        type: "bar",
        data: {
            labels: rangeData.labels,
            datasets: [
                {
                    label: "Number of Students",
                    data: rangeData.data,
                    backgroundColor: [
                        "#dc2626",
                        "#d97706",
                        "#0284c7",
                        "#16a34a",
                        "#059669"
                    ],
                    borderRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 },
                    title: {
                        display: true,
                        text: "Student Count",
                        font: { weight: "600" }
                    },
                    grid: { color: "rgba(0, 0, 0, 0.05)" }
                },
                x: {
                    grid: { display: false }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}
