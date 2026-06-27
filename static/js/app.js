// Global Chart Instance
let priceChartInstance = null;

document.addEventListener("DOMContentLoaded", () => {
    // DOM Elements
    const searchForm = document.getElementById("search-form");
    const tickerInput = document.getElementById("ticker-input");
    const periodSelect = document.getElementById("period-select");
    const modeToggle = document.getElementById("mode-toggle");
    const modelInputContainer = document.getElementById("model-input-container");
    const modelInput = document.getElementById("model-input");
    const rulesLabel = document.querySelector(".rules-label");
    const aiLabel = document.querySelector(".ai-label");
    
    const loadingContainer = document.getElementById("loading-container");
    const loaderTitle = document.getElementById("loader-title");
    const errorContainer = document.getElementById("error-container");
    const errorMessage = document.getElementById("error-message");
    const dashboardContent = document.getElementById("dashboard-content");
    
    // Toggle input visibility based on AI vs Rule mode
    modeToggle.addEventListener("change", () => {
        if (modeToggle.checked) {
            modelInputContainer.classList.remove("hidden");
            aiLabel.classList.add("active");
            rulesLabel.classList.remove("active");
        } else {
            modelInputContainer.classList.add("hidden");
            rulesLabel.classList.add("active");
            aiLabel.classList.remove("active");
        }
    });

    // Form submission
    searchForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const ticker = tickerInput.value.trim().toUpperCase();
        if (ticker) {
            runAnalysis(ticker);
        }
    });

    // Load default stock on startup
    runAnalysis("AAPL");
});

// Tab switcher logic
window.switchTab = function(event, tabId) {
    // Get all tab buttons and content panels
    const tabBtns = document.querySelectorAll(".tab-btn");
    const tabContents = document.querySelectorAll(".tab-content");
    
    // Deactivate all
    tabBtns.forEach(btn => btn.classList.remove("active"));
    tabContents.forEach(content => content.classList.remove("active"));
    
    // Activate clicked tab and panel
    event.currentTarget.classList.add("active");
    document.getElementById(tabId).classList.add("active");
};

// Error handling
window.dismissError = function() {
    document.getElementById("error-container").classList.add("hidden");
};

// Core API analysis function
async function runAnalysis(ticker) {
    const loadingContainer = document.getElementById("loading-container");
    const loaderTitle = document.getElementById("loader-title");
    const errorContainer = document.getElementById("error-container");
    const dashboardContent = document.getElementById("dashboard-content");
    
    const period = document.getElementById("period-select").value;
    const rulesOnly = !document.getElementById("mode-toggle").checked;
    const model = document.getElementById("model-input").value.trim();

    // Show loading, hide contents & errors
    loaderTitle.textContent = `Analyzing ${ticker}...`;
    loadingContainer.classList.remove("hidden");
    errorContainer.classList.add("hidden");
    dashboardContent.classList.add("hidden");

    try {
        let url = `/api/analyze?ticker=${encodeURIComponent(ticker)}&period=${encodeURIComponent(period)}&rules_only=${rulesOnly}`;
        if (!rulesOnly && model) {
            url += `&model=${encodeURIComponent(model)}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || `Server responded with status ${response.status}`);
        }

        // Successfully received analysis
        updateDashboard(data);
        
        // Hide loader and show content
        loadingContainer.classList.add("hidden");
        dashboardContent.classList.remove("hidden");
    } catch (err) {
        console.error(err);
        document.getElementById("error-message").textContent = err.message;
        loadingContainer.classList.add("hidden");
        errorContainer.classList.remove("hidden");
    }
}

// Update DOM elements with fetched data
function updateDashboard(data) {
    const ticker = data.ticker;
    const name = data.company_name;
    const market = data.market_data;
    const analysis = data.analysis;
    
    const price = market.price_action;
    const fundamentals = market.fundamentals;
    const technicals = market.technical_indicators;
    
    const currencySymbol = fundamentals.currency_symbol || "$";
    
    // Update Header
    document.getElementById("company-name").textContent = name;
    document.getElementById("ticker-display").textContent = `${ticker} // ${fundamentals.sector || 'N/A'}`;
    document.getElementById("company-sector-badge").textContent = fundamentals.sector || "N/A";
    document.getElementById("current-price").textContent = `${currencySymbol}${formatNumber(price.current_price)}`;
    
    // Price changes tags
    const dayChangeTag = document.getElementById("day-change");
    const monthChangeTag = document.getElementById("month-change");
    
    setPriceChangeTag(dayChangeTag, price.day_change_pct, "Day");
    setPriceChangeTag(monthChangeTag, price.month_change_pct, "Month");
    
    // 52 Week Range Bar
    const low52 = fundamentals.fifty_two_week_low !== "N/A" ? parseFloat(fundamentals.fifty_two_week_low) : price.low_52w;
    const high52 = fundamentals.fifty_two_week_high !== "N/A" ? parseFloat(fundamentals.fifty_two_week_high) : price.high_52w;
    const currentPrice = price.current_price;
    
    document.getElementById("low-52w-text").textContent = `${currencySymbol}${formatNumber(low52)}`;
    document.getElementById("high-52w-text").textContent = `${currencySymbol}${formatNumber(high52)}`;
    
    if (low52 && high52 && high52 !== low52) {
        const pct = ((currentPrice - low52) / (high52 - low52)) * 100;
        const boundedPct = Math.min(Math.max(pct, 0), 100);
        document.getElementById("range-52w-dot").style.left = `${boundedPct}%`;
        document.getElementById("range-52w-fill").style.left = `0%`;
        document.getElementById("range-52w-fill").style.width = `${boundedPct}%`;
    } else {
        document.getElementById("range-52w-dot").style.left = `50%`;
        document.getElementById("range-52w-fill").style.width = `0%`;
    }
    
    // Recommendation card
    const recCard = document.getElementById("rec-card");
    const recValue = document.getElementById("rec-value");
    const confidenceValue = document.getElementById("confidence-value");
    const recReasoning = document.getElementById("rec-reasoning");
    
    const recommendation = (analysis.recommendation || "HOLD").toUpperCase();
    recValue.textContent = recommendation;
    
    // Reset recommendation classes
    recCard.className = "rec-section grid-col-4 glass-card";
    if (recommendation.includes("BUY")) {
        recCard.classList.add("rec-buy");
    } else if (recommendation.includes("SELL")) {
        recCard.classList.add("rec-sell");
    } else {
        recCard.classList.add("rec-hold");
    }
    
    // Confidence value
    const confidence = analysis.confidence || "Medium";
    confidenceValue.textContent = confidence;
    confidenceValue.className = "confidence-badge";
    if (confidence.toLowerCase() === "high") {
        confidenceValue.classList.add("badge-high");
    } else if (confidence.toLowerCase() === "low") {
        confidenceValue.classList.add("badge-low");
    } else {
        confidenceValue.classList.add("badge-medium");
    }
    
    recReasoning.textContent = analysis.reasoning || "No reasoning details provided.";
    
    // Key Metrics Grid
    document.getElementById("m-sector").textContent = fundamentals.sector || "N/A";
    document.getElementById("m-market-cap").textContent = fundamentals.market_cap || "N/A";
    document.getElementById("m-pe").textContent = fundamentals.pe_ratio !== undefined ? fundamentals.pe_ratio : "N/A";
    document.getElementById("m-eps").textContent = fundamentals.eps !== undefined ? fundamentals.eps : "N/A";
    
    const rsiVal = technicals.rsi_14;
    const rsiSig = technicals.rsi_signal;
    document.getElementById("m-rsi").textContent = rsiVal !== "N/A" ? `${rsiVal} (${rsiSig})` : "N/A";
    document.getElementById("m-trend").textContent = technicals.trend || "N/A";
    
    const betaVal = fundamentals.beta;
    document.getElementById("m-beta").textContent = betaVal !== undefined ? betaVal : "N/A";
    
    const macdInterp = technicals.macd_signal_interpretation;
    document.getElementById("m-macd").textContent = macdInterp || "N/A";
    
    // Detailed analysis paragraphs
    document.getElementById("technical-analysis-text").textContent = analysis.technical_analysis || "No technical analysis report generated.";
    document.getElementById("fundamental-analysis-text").textContent = analysis.fundamental_analysis || "No fundamental analysis report generated.";
    document.getElementById("sentiment-analysis-text").textContent = analysis.news_sentiment || "No news sentiment report generated.";
    
    // Bullets (Bullish, Bearish, Risks)
    populateList("bullish-list", analysis.bullish_factors);
    populateList("bearish-list", analysis.bearish_factors);
    populateList("risks-list", analysis.risks);
    
    // Short-Term Outlook
    document.getElementById("outlook-text").textContent = analysis.price_outlook || "No price outlook details available.";
    
    // Footer metadata
    const engineLabel = data.engine || "Rules Engine";
    const modelLabel = data.model;
    document.getElementById("meta-engine").textContent = modelLabel ? `${engineLabel} (${modelLabel})` : engineLabel;
    
    // Format timestamp
    const fetchedDate = new Date(data.fetched_at);
    document.getElementById("meta-time").textContent = isNaN(fetchedDate.getTime()) ? data.fetched_at : fetchedDate.toLocaleString();
    document.getElementById("meta-disclaimer").textContent = data.disclaimer || "";
    
    // Update Period Tag in Chart Header
    const periodMap = {
        "1mo": "1 Month",
        "3mo": "3 Months",
        "6mo": "6 Months",
        "1y": "1 Year",
        "2y": "2 Years"
    };
    document.getElementById("chart-period-display").textContent = periodMap[market.data_period] || market.data_period;
    
    // Render Chart
    renderChart(data.chart_data);
}

// Set price change tag indicators and colors
function setPriceChangeTag(element, value, label) {
    if (value === undefined || value === null || value === "N/A") {
        element.className = "change-tag neutral";
        element.innerHTML = `<i class="fa-solid fa-minus"></i> N/A (${label})`;
        return;
    }
    
    const floatVal = parseFloat(value);
    if (floatVal > 0) {
        element.className = "change-tag positive";
        element.innerHTML = `<i class="fa-solid fa-caret-up"></i> +${floatVal.toFixed(2)}% (${label})`;
    } else if (floatVal < 0) {
        element.className = "change-tag negative";
        element.innerHTML = `<i class="fa-solid fa-caret-down"></i> ${floatVal.toFixed(2)}% (${label})`;
    } else {
        element.className = "change-tag neutral";
        element.innerHTML = `<i class="fa-solid fa-minus"></i> 0.00% (${label})`;
    }
}

// Populate unordered lists cleanly
function populateList(elementId, items) {
    const listElement = document.getElementById(elementId);
    listElement.innerHTML = "";
    
    if (!items || items.length === 0) {
        const li = document.createElement("li");
        li.textContent = "No factors identified in the data.";
        listElement.appendChild(li);
        return;
    }
    
    items.forEach(item => {
        const li = document.createElement("li");
        li.textContent = item;
        listElement.appendChild(li);
    });
}

// Render dynamic stock chart
function renderChart(chartData) {
    const ctx = document.getElementById("priceChart").getContext("2d");
    
    if (!chartData || chartData.length === 0) {
        console.warn("No chart data available to render");
        return;
    }
    
    const labels = chartData.map(d => d.date);
    const closePrices = chartData.map(d => d.close);
    const volumes = chartData.map(d => d.volume);
    
    // Destroy previous chart instance if exists
    if (priceChartInstance) {
        priceChartInstance.destroy();
    }
    
    // Gradient fill for price line chart
    const gradient = ctx.createLinearGradient(0, 0, 0, 350);
    gradient.addColorStop(0, "rgba(99, 102, 241, 0.35)");
    gradient.addColorStop(1, "rgba(99, 102, 241, 0.0)");
    
    // Color volume bars based on price movement (green if close >= open, else red)
    const volumeColors = chartData.map(d => {
        return d.close >= d.open ? "rgba(16, 185, 129, 0.15)" : "rgba(239, 68, 68, 0.15)";
    });
    
    const maxVolume = Math.max(...volumes);
    
    // Create new Chart instance
    priceChartInstance = new Chart(ctx, {
        data: {
            labels: labels,
            datasets: [
                {
                    type: "line",
                    label: "Closing Price",
                    data: closePrices,
                    borderColor: "#6366f1",
                    borderWidth: 2,
                    pointRadius: labels.length > 100 ? 0 : 2,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: "#6366f1",
                    pointHoverBorderColor: "#ffffff",
                    pointHoverBorderWidth: 2,
                    fill: true,
                    backgroundColor: gradient,
                    tension: 0.15,
                    yAxisID: "y"
                },
                {
                    type: "bar",
                    label: "Volume",
                    data: volumes,
                    backgroundColor: volumeColors,
                    borderWidth: 0,
                    yAxisID: "y1",
                    barPercentage: 0.8
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: "index",
                intersect: false
            },
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        color: "#94a3b8",
                        font: {
                            family: "Inter",
                            size: 11
                        }
                    }
                },
                tooltip: {
                    backgroundColor: "rgba(15, 23, 42, 0.95)",
                    titleColor: "#ffffff",
                    bodyColor: "#94a3b8",
                    borderColor: "rgba(255, 255, 255, 0.1)",
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    titleFont: {
                        family: "Outfit",
                        weight: "bold",
                        size: 13
                    },
                    bodyFont: {
                        family: "Inter",
                        size: 12
                    },
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.datasetIndex === 0) {
                                label += `$${context.raw.toFixed(2)}`;
                            } else {
                                label += context.raw.toLocaleString();
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: "#64748b",
                        font: {
                            family: "Inter",
                            size: 10
                        },
                        maxTicksLimit: 12
                    }
                },
                y: {
                    position: "left",
                    grid: {
                        color: "rgba(255, 255, 255, 0.03)"
                    },
                    ticks: {
                        color: "#94a3b8",
                        font: {
                            family: "Space Grotesk",
                            size: 11
                        },
                        callback: function(value) {
                            return "$" + value;
                        }
                    }
                },
                y1: {
                    position: "right",
                    grid: {
                        display: false
                    },
                    ticks: {
                        display: false
                    },
                    // Push volume bars down by setting a large max limit relative to volume values
                    max: maxVolume * 4,
                    min: 0
                }
            }
        }
    });
}

// Utility function to format numbers
function formatNumber(num) {
    if (num === undefined || num === null || num === "N/A") return "N/A";
    const parsed = parseFloat(num);
    return isNaN(parsed) ? num : parsed.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
