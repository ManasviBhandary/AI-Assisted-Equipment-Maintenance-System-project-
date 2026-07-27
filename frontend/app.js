document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide Icons
    if (window.lucide) {
        lucide.createIcons();
    }

    // Tab Switching Logic
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const pageTitle = document.getElementById('page-title');

    const tabTitles = {
        'dashboard': 'Smart Factory Equipment Analytics & BI Dashboard',
        'ai-assistant': 'AI / RAG Operations Assistant',
        'equipment': 'Equipment Status & Predictive Maintenance Windows',
        'predictive-alerts': 'Module 5 — Predictive Failure Alert System & Risk Engine',
        'data-warehouse': 'Relational Data Warehouse & Star Schema Browser',
        'er-diagram': 'Star Schema Entity-Relationship (ER) Model'
    };

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');

            navButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(`tab-${targetTab}`).classList.add('active');
            if (pageTitle && tabTitles[targetTab]) {
                pageTitle.textContent = tabTitles[targetTab];
            }
        });
    });

    // Chart Instances
    let downtimeChartInstance = null;
    let defectChartInstance = null;

    // Load Initial Data
    loadMetrics();
    loadDowntimeTrend();
    loadDefectRates();
    loadEquipmentStatus();
    loadPredictiveAlerts();
    loadStarSchema();

    // ETL Trigger
    const btnRunEtl = document.getElementById('btn-run-etl');
    if (btnRunEtl) {
        btnRunEtl.addEventListener('click', runEtlPipeline);
    }

    // Chat Event Listeners
    const btnSendChat = document.getElementById('btn-send-chat');
    const chatInput = document.getElementById('chat-input');
    if (btnSendChat && chatInput) {
        btnSendChat.addEventListener('click', sendChatMessage);
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendChatMessage();
        });
    }

    // Toast Notification Utility
    function showToast(message) {
        const toast = document.getElementById('toast');
        if (toast) {
            toast.textContent = message;
            toast.classList.remove('hidden');
            setTimeout(() => toast.classList.add('hidden'), 3500);
        }
    }

    // 1. Fetch High Level Metrics
    async function loadMetrics() {
        try {
            const res = await fetch('/api/metrics');
            const data = await res.json();
            document.getElementById('kpi-downtime').textContent = `${data.total_downtime_hours} hrs`;
            document.getElementById('kpi-cost').textContent = `$${data.total_maintenance_cost.toLocaleString()}`;
            document.getElementById('kpi-defects').textContent = data.defect_count;
            document.getElementById('kpi-mttr').textContent = `${data.mttr_hours} hrs`;
        } catch (err) {
            console.error('Failed to load metrics:', err);
        }
    }

    // 2. Load Downtime Trend Chart
    async function loadDowntimeTrend() {
        try {
            const res = await fetch('/api/downtime-trend');
            const data = await res.json();

            const dates = [...new Set(data.map(d => d.date_str))].sort();
            const machines = [...new Set(data.map(d => d.equipment_id))];

            const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
            const datasets = machines.map((m, idx) => {
                const machineData = dates.map(dt => {
                    const found = data.find(d => d.date_str === dt && d.equipment_id === m);
                    return found ? found.downtime : 0;
                });
                return {
                    label: m,
                    data: machineData,
                    borderColor: colors[idx % colors.length],
                    backgroundColor: colors[idx % colors.length],
                    tension: 0.3,
                    fill: false
                };
            });

            const ctx = document.getElementById('chart-downtime').getContext('2d');
            if (downtimeChartInstance) downtimeChartInstance.destroy();

            downtimeChartInstance = new Chart(ctx, {
                type: 'line',
                data: { labels: dates, datasets: datasets },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#9ca3af', font: { family: 'Plus Jakarta Sans' } } }
                    },
                    scales: {
                        x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                        y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' }, title: { display: true, text: 'Downtime (Hours)', color: '#9ca3af' } }
                    }
                }
            });
        } catch (err) {
            console.error('Failed to load downtime trend:', err);
        }
    }

    // 3. Load Defect Rates Bar Chart
    async function loadDefectRates() {
        try {
            const res = await fetch('/api/defect-rate');
            const data = await res.json();

            const labels = data.map(d => `${d.equipment_id} (${d.machine_type})`);
            const avgTemps = data.map(d => d.avg_temp ? d.avg_temp.toFixed(1) : 0);
            const avgVibs = data.map(d => d.avg_vibration ? (d.avg_vibration * 10).toFixed(1) : 0); // Scale up for visual clarity

            const ctx = document.getElementById('chart-defect').getContext('2d');
            if (defectChartInstance) defectChartInstance.destroy();

            defectChartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [
                        { label: 'Avg Temperature (°C)', data: avgTemps, backgroundColor: 'rgba(245, 158, 11, 0.7)', borderRadius: 6 },
                        { label: 'Avg Vibration (x10 mm/s)', data: avgVibs, backgroundColor: 'rgba(239, 68, 68, 0.7)', borderRadius: 6 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#9ca3af', font: { family: 'Plus Jakarta Sans' } } }
                    },
                    scales: {
                        x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                        y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } }
                    }
                }
            });
        } catch (err) {
            console.error('Failed to load defect rates:', err);
        }
    }

    // 4. Load Equipment Health Table
    async function loadEquipmentStatus() {
        try {
            const res = await fetch('/api/equipment-status');
            const data = await res.json();
            const tbody = document.getElementById('table-equipment-body');

            if (!tbody) return;
            tbody.innerHTML = '';

            data.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${item.equipment_id}</strong></td>
                    <td>${item.name}</td>
                    <td><span class="chart-badge">${item.type}</span></td>
                    <td>${item.location_plant} (${item.location_sector})</td>
                    <td>${item.temperature_c ? item.temperature_c + ' °C' : 'N/A'}</td>
                    <td>${item.vibration_mm_s ? item.vibration_mm_s + ' mm/s' : 'N/A'}</td>
                    <td>${item.pressure_bar ? item.pressure_bar + ' bar' : 'N/A'}</td>
                    <td><span class="health-badge ${item.health_status}">${item.health_status}</span></td>
                    <td><strong>${item.maintenance_window}</strong></td>
                `;
                tbody.appendChild(tr);
            });
        } catch (err) {
            console.error('Failed to load equipment status:', err);
        }
    }

    // 5. Star Schema Explorer
    let starSchemaData = null;

    async function loadStarSchema() {
        try {
            const res = await fetch('/api/star-schema');
            starSchemaData = await res.json();

            const btnContainer = document.getElementById('schema-table-buttons');
            if (!btnContainer) return;
            btnContainer.innerHTML = '';

            Object.keys(starSchemaData).forEach((tableName, idx) => {
                const btn = document.createElement('button');
                btn.className = `schema-tab-btn ${idx === 0 ? 'active' : ''}`;
                btn.textContent = tableName;
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.schema-tab-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    renderTableSchema(tableName);
                });
                btnContainer.appendChild(btn);
            });

            if (Object.keys(starSchemaData).length > 0) {
                renderTableSchema(Object.keys(starSchemaData)[0]);
            }
        } catch (err) {
            console.error('Failed to load star schema:', err);
        }
    }

    function renderTableSchema(tableName) {
        if (!starSchemaData || !starSchemaData[tableName]) return;
        const tblData = starSchemaData[tableName];

        const thead = document.getElementById('schema-thead');
        const tbody = document.getElementById('schema-tbody');

        thead.innerHTML = `<tr>${tblData.columns.map(col => `<th>${col}</th>`).join('')}</tr>`;
        tbody.innerHTML = tblData.rows.map(row => {
            return `<tr>${tblData.columns.map(col => `<td>${row[col] !== null ? row[col] : 'NULL'}</td>`).join('')}</tr>`;
        }).join('');
    }

    // 5.5 Module 5: Predictive Failure Alert System Engine
    async function loadPredictiveAlerts() {
        try {
            const res = await fetch('/api/predictive-alerts');
            const data = await res.json();

            const summary = data.summary;
            const alerts = data.alerts;

            // Update Summary KPI Banner
            if (document.getElementById('pred-total-assets')) {
                document.getElementById('pred-total-assets').textContent = summary.total_monitored;
            }
            if (document.getElementById('pred-high-risk')) {
                document.getElementById('pred-high-risk').textContent = summary.high_risk_alerts;
            }
            if (document.getElementById('pred-avg-risk')) {
                document.getElementById('pred-avg-risk').textContent = `${summary.avg_system_risk_pct}%`;
            }

            const container = document.getElementById('predictive-alerts-container');
            if (!container) return;
            container.innerHTML = '';

            alerts.forEach(item => {
                const card = document.createElement('div');
                const riskLevelLower = item.risk_level.toLowerCase();
                card.className = `pred-alert-card risk-${riskLevelLower}`;

                const fillWidth = Math.min(100, Math.max(8, item.risk_score_pct));

                card.innerHTML = `
                    <div class="pred-card-header">
                        <div>
                            <span class="pred-eq-id">${item.equipment_id}</span>
                            <h4 class="pred-eq-name">${item.name}</h4>
                            <span class="pred-eq-type">${item.type} • ${item.location}</span>
                        </div>
                        <div class="risk-badge-box ${riskLevelLower}">
                            <span class="risk-badge-label">${item.risk_level} RISK</span>
                            <span class="risk-score-value">${item.risk_score_pct}%</span>
                        </div>
                    </div>

                    <div class="risk-progress-bar-container">
                        <div class="risk-progress-bar-fill ${riskLevelLower}" style="width: ${fillWidth}%;"></div>
                    </div>

                    <div class="pred-metrics-grid">
                        <div class="pred-metric-item">
                            <span>Predicted Failure Window</span>
                            <strong>In ${item.predicted_hours_to_failure} hrs</strong>
                        </div>
                        <div class="pred-metric-item">
                            <span>Vibration</span>
                            <strong>${item.vibration_mm_s} mm/s</strong>
                        </div>
                        <div class="pred-metric-item">
                            <span>Temperature</span>
                            <strong>${item.temperature_c} °C</strong>
                        </div>
                        <div class="pred-metric-item">
                            <span>Runtime</span>
                            <strong>${item.runtime_hours} hrs</strong>
                        </div>
                    </div>

                    <div class="pred-driver-box">
                        <strong><i data-lucide="alert-circle"></i> Root Cause Risk Driver:</strong>
                        <p>${item.primary_driver}</p>
                    </div>

                    <div class="pred-action-box">
                        <strong><i data-lucide="wrench"></i> Recommended Preventive Action:</strong>
                        <p>${item.recommended_action}</p>
                    </div>

                    <button class="btn-dispatch-maint" onclick="dispatchPreventiveMaintenance('${item.equipment_id}', '${item.recommended_action.replace(/'/g, "\\'")}')">
                        <i data-lucide="calendar"></i> Dispatch Preventive Maintenance Order
                    </button>
                `;

                container.appendChild(card);
            });

            if (window.lucide) lucide.createIcons();

        } catch (err) {
            console.error('Failed to load predictive alerts:', err);
        }
    }

    window.dispatchPreventiveMaintenance = async function(equipmentId, recommendedAction) {
        try {
            const res = await fetch('/api/trigger-maintenance', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    equipment_id: equipmentId,
                    recommended_action: recommendedAction
                })
            });
            const data = await res.json();
            showToast(data.message || `Preventive Maintenance order dispatched for ${equipmentId}!`);
            loadMetrics();
            loadEquipmentStatus();
            loadPredictiveAlerts();
            loadStarSchema();
        } catch (err) {
            showToast(`Failed to dispatch maintenance for ${equipmentId}!`);
            console.error(err);
        }
    };

    // 6. Run ETL Trigger
    async function runEtlPipeline() {
        const spinner = document.getElementById('etl-spinner');
        if (spinner) spinner.classList.add('pulse');

        try {
            const res = await fetch('/api/run-etl', { method: 'POST' });
            const data = await res.json();
            showToast(data.message || 'ETL Pipeline executed!');
            
            // Reload all dashboard data
            loadMetrics();
            loadDowntimeTrend();
            loadDefectRates();
            loadEquipmentStatus();
            loadPredictiveAlerts();
            loadStarSchema();
        } catch (err) {
            showToast('ETL Execution failed!');
            console.error(err);
        } finally {
            if (spinner) spinner.classList.remove('pulse');
        }
    }

    // 7. RAG AI Chat Message Sending
    async function sendChatMessage() {
        const chatInput = document.getElementById('chat-input');
        const query = chatInput.value.trim();
        if (!query) return;

        appendMessage('user', query);
        chatInput.value = '';

        // Thinking indicator
        const thinkingId = appendThinkingMessage();

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: query })
            });
            const data = await res.json();

            removeThinkingMessage(thinkingId);
            appendMessage('bot', data.answer, data.sources);
        } catch (err) {
            removeThinkingMessage(thinkingId);
            appendMessage('bot', 'Error retrieving response from RAG Assistant server.');
            console.error(err);
        }
    }

    window.sendSampleQuery = function(queryText) {
        // Switch to AI tab if not active
        const aiNavBtn = document.querySelector('[data-tab="ai-assistant"]');
        if (aiNavBtn) aiNavBtn.click();

        const chatInput = document.getElementById('chat-input');
        if (chatInput) {
            chatInput.value = queryText;
            sendChatMessage();
        }
    };

    function appendMessage(sender, text, sources = []) {
        const chatMessages = document.getElementById('chat-messages');
        if (!chatMessages) return;

        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}-message`;

        const avatarIcon = sender === 'user' ? 'user' : 'bot';
        let formattedText = text
            .replace(/### (.*?)\n/g, '<h4 style="color:#60a5fa; margin: 10px 0 6px 0;">$1</h4>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/`([^`]+)`/g, '<code style="background:rgba(255,255,255,0.1); padding:2px 6px; border-radius:4px; font-family:monospace;">$1</code>')
            .replace(/\n/g, '<br>');

        let sourcesHtml = '';
        if (sources && sources.length > 0) {
            sourcesHtml = `<div style="margin-top:10px; padding-top:8px; border-top:1px solid var(--border-color); font-size:0.75rem; color:var(--text-dim);">
                <strong>Sources Referenced:</strong> ${sources.join(' | ')}
            </div>`;
        }

        msgDiv.innerHTML = `
            <div class="msg-avatar"><i data-lucide="${avatarIcon}"></i></div>
            <div class="msg-body">
                <strong>${sender === 'user' ? 'You' : 'Smart Factory AI Assistant'}</strong>
                <div>${formattedText}</div>
                ${sourcesHtml}
            </div>
        `;

        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        if (window.lucide) lucide.createIcons();
    }

    function appendThinkingMessage() {
        const chatMessages = document.getElementById('chat-messages');
        const id = 'thinking-' + Date.now();
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot-message';
        msgDiv.id = id;

        msgDiv.innerHTML = `
            <div class="msg-avatar"><i data-lucide="bot"></i></div>
            <div class="msg-body">
                <strong>Smart Factory AI Assistant</strong>
                <p style="color:var(--text-muted); font-style:italic;">Searching SQLite Star Schema & Equipment Manuals...</p>
            </div>
        `;
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        if (window.lucide) lucide.createIcons();
        return id;
    }

    function removeThinkingMessage(id) {
        const elem = document.getElementById(id);
        if (elem) elem.remove();
    }
});
