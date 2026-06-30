document.addEventListener("DOMContentLoaded", () => {
    const resourceContainer = document.getElementById("resource-container");
    const alertContainer = document.getElementById("alert-container");
    const alertCount = document.getElementById("alert-count");
    const template = document.getElementById("resource-card-template");

    // Format metric keys to readable labels
    const formatLabel = (key) => {
        return key.replace(/_/g, ' ').toUpperCase();
    };

    // Format metric values (add units)
    const formatValue = (key, value) => {
        if (key.includes('utilization') || key.includes('usage')) return `${value}%`;
        if (key.includes('gb')) return `${value} GB`;
        if (key.includes('network')) return `${value} MB/s`;
        return value.toLocaleString();
    };

    const updateDashboard = async () => {
        try {
            const response = await fetch('/api/status');
            if (!response.ok) throw new Error("Network response was not ok");
            const data = await response.json();
            
            renderResources(data.resources);
            renderAlerts(data.alerts);
            updateGlobalStatus(data.alerts.length === 0);
            
        } catch (error) {
            console.error("Error fetching status:", error);
            updateGlobalStatus(false, "Connection Lost");
        }
    };

    const renderResources = (resources) => {
        // Clear existing to redraw (in a real React app this would be diffed, but here we just re-render or update)
        // To prevent layout thrashing and keep animations smooth, we will update existing DOM nodes if they exist.
        
        resources.forEach(res => {
            let card = document.getElementById(`resource-${res.resource_id}`);
            
            if (!card) {
                // Create new card from template
                const clone = template.content.cloneNode(true);
                card = clone.querySelector('.resource-card');
                card.id = `resource-${res.resource_id}`;
                resourceContainer.appendChild(clone);
                // Re-fetch the newly appended card
                card = document.getElementById(`resource-${res.resource_id}`);
            }
            
            // Update Card State
            card.className = `glass-panel resource-card ${res.status}`;
            
            card.querySelector('.resource-name').textContent = res.name;
            card.querySelector('.resource-type').textContent = res.type;
            card.querySelector('.status-badge').textContent = res.status;
            card.querySelector('.region-label').textContent = `📍 ${res.region}`;
            card.querySelector('.id-label').textContent = res.resource_id;
            
            // Update Metrics
            const metricsGrid = card.querySelector('.metrics-grid');
            metricsGrid.innerHTML = ''; // Clear metrics
            for (const [key, value] of Object.entries(res.metrics)) {
                const metricHtml = `
                    <div class="metric-item">
                        <span class="metric-label">${formatLabel(key)}</span>
                        <span class="metric-value">${formatValue(key, value)}</span>
                    </div>
                `;
                metricsGrid.insertAdjacentHTML('beforeend', metricHtml);
            }
            
            // Update Tags (Highlight the bug!)
            const tagsContainer = card.querySelector('.tags-container');
            tagsContainer.innerHTML = '';
            res.tags.forEach(tag => {
                const isBuggedTag = res.name !== 'web-server-01' && tag === 'environment:production';
                const bugClass = isBuggedTag ? 'bug-highlight' : '';
                tagsContainer.insertAdjacentHTML('beforeend', `<span class="tag ${bugClass}">${tag}</span>`);
            });
        });
    };

    const renderAlerts = (alerts) => {
        alertCount.textContent = alerts.length;
        if (alerts.length === 0) {
            alertCount.classList.add('zero');
            alertContainer.innerHTML = `<div class="empty-state">No active alerts. System healthy.</div>`;
        } else {
            alertCount.classList.remove('zero');
            alertContainer.innerHTML = '';
            alerts.forEach(alert => {
                alertContainer.insertAdjacentHTML('beforeend', `
                    <div class="alert-item">
                        <strong>Alert:</strong> ${alert}
                    </div>
                `);
            });
        }
    };

    const updateGlobalStatus = (isHealthy, textOverride = null) => {
        const pulse = document.querySelector('.pulse-indicator');
        const text = document.getElementById('global-status-text');
        
        if (isHealthy) {
            pulse.style.backgroundColor = 'var(--color-healthy)';
            pulse.style.boxShadow = '0 0 10px var(--color-healthy)';
            pulse.style.animation = 'pulse 2s infinite';
            text.textContent = textOverride || 'System Healthy';
            text.style.color = 'var(--color-healthy)';
        } else {
            pulse.style.backgroundColor = 'var(--color-offline)';
            pulse.style.boxShadow = '0 0 10px var(--color-offline)';
            pulse.style.animation = 'flash 1s infinite alternate';
            text.textContent = textOverride || 'Issues Detected';
            text.style.color = 'var(--color-offline)';
        }
    };

    // Poll every 1.5 seconds
    setInterval(updateDashboard, 1500);
    // Initial fetch
    updateDashboard();
});
