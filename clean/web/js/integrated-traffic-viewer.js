// v2.1 railway backend
// ─── State ───────────────────────────────────────────────────────────────────
let map, marker, geocoder, trafficLayer;
let selectedLocation   = null;
let trafficLayerActive = false;
let activeTab = 'pavement';

const FGCU_CENTER = { lat: 26.4622, lng: -81.7758 };
const RAILWAY_BASE = 'https://quaketwin-production.up.railway.app';
const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : RAILWAY_BASE;
const USE_SIMULATED_QRL = false;

// ─── Map Init ────────────────────────────────────────────────────────────────
function initMap() {
    geocoder = new google.maps.Geocoder();

    map = new google.maps.Map(document.getElementById('map'), {
        center: FGCU_CENTER,
        zoom: 13,
        mapTypeId: 'roadmap',
        disableDefaultUI: true,
        zoomControl: true,
        zoomControlOptions: { position: google.maps.ControlPosition.RIGHT_BOTTOM },
        styles: [
            { featureType:'all',         elementType:'geometry',           stylers:[{color:'#242f3e'}] },
            { featureType:'all',         elementType:'labels.text.stroke', stylers:[{color:'#242f3e'}] },
            { featureType:'all',         elementType:'labels.text.fill',   stylers:[{color:'#746855'}] },
            { featureType:'road',        elementType:'geometry',           stylers:[{color:'#38414e'}] },
            { featureType:'road',        elementType:'geometry.stroke',    stylers:[{color:'#212a37'}] },
            { featureType:'road',        elementType:'labels.text.fill',   stylers:[{color:'#9ca5b3'}] },
            { featureType:'road.highway',elementType:'geometry',           stylers:[{color:'#746855'}] },
            { featureType:'water',       elementType:'geometry',           stylers:[{color:'#17263c'}] },
        ]
    });

    trafficLayer = new google.maps.TrafficLayer();

    map.addListener('click', e => selectLocation(e.latLng));

    updateStatus('Ready – click map to analyze');
    updateLastUpdate();
}

// ─── Tab Switching ───────────────────────────────────────────────────────────
function switchTab(name) {
    activeTab = name;
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    document.getElementById('tab-btn-' + name).classList.add('active');
    document.getElementById('tab-' + name).classList.add('active');

    if (name === 'security') {
        startSecuritySim();
    } else {
        stopSecuritySim();
    }
}

// ─── Location Selection (auto-analyze) ───────────────────────────────────────
function selectLocation(location) {
    selectedLocation = location;
    placeMarker(location);
    updateLocationDisplay(location);
    updateStreetViewThumbnail(location);
    showElement('location-info');
    switchTab('pavement');
    analyzePavement();
}

function updateStreetViewThumbnail(location) {
    const lat = location.lat();
    const lng = location.lng();
    const key = 'GOOGLE_MAPS_API_KEY_PLACEHOLDER';
    const url = `https://maps.googleapis.com/maps/api/streetview?size=260x160&location=${lat},${lng}&key=${key}`;
    const img = document.getElementById('sv-thumbnail');
    img.src = url;
    img.onerror = () => { document.getElementById('sv-thumb-wrap').style.display = 'none'; };
    img.onload  = () => { document.getElementById('sv-thumb-wrap').style.display = 'block'; };
    document.getElementById('sv-thumb-wrap').style.display = 'none'; // hide until loaded
}

function placeMarker(location) {
    if (marker) marker.setMap(null);
    marker = new google.maps.Marker({
        position: location,
        map,
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 10,
            fillColor: '#00d4ff',
            fillOpacity: 0.8,
            strokeColor: '#ffffff',
            strokeWeight: 2
        }
    });
}

function updateLocationDisplay(location) {
    document.getElementById('location-coords').textContent =
        `${location.lat().toFixed(6)}, ${location.lng().toFixed(6)}`;
    geocoder.geocode({ location }, (results, status) => {
        document.getElementById('location-address').textContent =
            (status === 'OK' && results[0]) ? results[0].formatted_address : 'Address unavailable';
    });
}

// ─── Traffic Layer ───────────────────────────────────────────────────────────
function toggleTraffic() {
    trafficLayerActive = !trafficLayerActive;
    const btn = document.getElementById('traffic-btn');
    if (trafficLayerActive) {
        trafficLayer.setMap(map);
        btn.textContent = '🚦 Hide Traffic Layer';
        btn.classList.add('active');
        updateStatus('Traffic layer on');
    } else {
        trafficLayer.setMap(null);
        btn.textContent = '🚦 Show Traffic Layer';
        btn.classList.remove('active');
        updateStatus('Traffic layer off');
    }
}

// ─── Pavement Analysis ───────────────────────────────────────────────────────
async function analyzePavement() {
    if (!selectedLocation) return;

    showElement('loading');
    hideElement('pavement-results');
    hideElement('analysis-details');
    document.getElementById('pci-value').textContent        = '--';
    document.getElementById('condition-rating').textContent = '--';
    updateStatus('⚛️ Running QRL analysis…');

    try {
        if (USE_SIMULATED_QRL) {
            const mock = getSimulatedQRLData(selectedLocation);
            displayPavementCondition(mock, true);
            updateStatus('✅ QRL analysis complete');
            return;
        }

        const controller = new AbortController();
        const timeoutId  = setTimeout(() => controller.abort(), 10000);

        const t0 = performance.now();
        const pavementUrl = API_BASE + '/api/pavement-condition-direct';
        const response = await fetch(pavementUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                latitude:  selectedLocation.lat(),
                longitude: selectedLocation.lng()
            }),
            signal: controller.signal
        });
        const responseTimeMs = performance.now() - t0;
        clearTimeout(timeoutId);
        applyMeasuredNetworkConditions(responseTimeMs);

        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        console.log(data);
        if (!data?.pci) throw new Error('Invalid response');

        displayPavementCondition(data, false);

        updateStatus('✅ QRL analysis complete');

    } catch (err) {
        console.error('Analysis error:', err);
        hideElement('loading');
        showToast('QRL analysis unavailable – API connection failed.');
        updateStatus('❌ Analysis unavailable');
    } finally {
        hideElement('loading');
    }
}


function displayTrafficData(data) {
    showElement('traffic-data');
    document.getElementById('traffic-volume').textContent = data.current_volume || '--';
    document.getElementById('traffic-level').textContent  = data.risk_label     || '--';
    document.getElementById('traffic-speed').textContent  = data.speed          || '--';
}

function displayPavementCondition(data, isSimulated = false) {
    showElement('pavement-results');
    document.getElementById('pci-value').textContent        = Math.round(data.pci);
    document.getElementById('condition-rating').textContent = data.condition;

    const cls = getConditionColorClass(data.pci);
    document.getElementById('pci-value').className        = `pci-number ${cls}`;
    document.getElementById('condition-rating').className = `condition-pill ${cls}`;

    if (data.details?.qrl_analysis) {
        displayQRLAnalysis(data.details.qrl_analysis, data.details, isSimulated);
    } else {
        displayBasicDetails(data.details || {});
    }
}

function displayQRLAnalysis(qrlData, details, isSimulated = false) {
    const container = document.getElementById('analysis-details');
    showElement('analysis-details');

    const riskEmoji  = { NORMAL:'🟢', WATCH:'🟡', CONGESTED:'🟠', CRITICAL:'🔴' }[qrlData.risk_label] || '⚪';
    const riskColors = { NORMAL:'#00ff00', WATCH:'#ffd700', CONGESTED:'#ff8c00', CRITICAL:'#ff4444' };

    let html = `
        <div style="font-size:10px;color:#666;text-transform:uppercase;letter-spacing:.8px;margin-bottom:10px;font-weight:600;">
            ⚛️ Quantum ML Analysis ${isSimulated ? '· <span style="color:#ffa500;">Demo</span>' : ''}
        </div>
        <div class="risk-indicator">
            <span class="risk-emoji">${riskEmoji}</span>
            <div>
                <div style="font-size:15px;font-weight:700;">${qrlData.risk_label}</div>
                <div style="font-size:11px;color:#888;">Confidence: ${(qrlData.quantum_confidence * 100).toFixed(1)}%</div>
            </div>
        </div>
        <div style="font-size:10px;color:#555;margin:10px 0 5px;">Risk Probabilities</div>
    `;

    ['NORMAL','WATCH','CONGESTED','CRITICAL'].forEach(level => {
        const prob = qrlData.risk_probabilities[level] || 0;
        const pct  = (prob * 100).toFixed(1);
        const emoji = { NORMAL:'🟢', WATCH:'🟡', CONGESTED:'🟠', CRITICAL:'🔴' }[level];
        html += `
            <div style="margin:5px 0;font-size:11px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:2px;">
                    <span>${emoji} ${level}</span><span>${pct}%</span>
                </div>
                <div class="probability-bar">
                    <div class="probability-fill" style="width:${pct}%;background:${riskColors[level]};"></div>
                </div>
            </div>
        `;
    });

    if (details.distress_types?.length) {
        html += `
            <div style="font-size:10px;color:#555;margin:10px 0 4px;">Detected Issues</div>
            <ul class="distress-list">${details.distress_types.map(d => `<li>${d}</li>`).join('')}</ul>
        `;
    }
    if (details.recommended_action) {
        html += `
            <div style="margin-top:8px;padding:8px 10px;background:rgba(255,165,0,.08);border-radius:6px;border-left:2px solid #ffa500;font-size:11px;">
                <strong>Recommendation:</strong><br>${details.recommended_action}
            </div>
        `;
    }

    container.innerHTML = html;
}

function displayBasicDetails(details) {
    const container = document.getElementById('analysis-details');
    showElement('analysis-details');
    let html = '<div style="color:#aaa;font-size:12px;">';
    if (details.distress_types)     html += `<strong>Distress:</strong> ${details.distress_types.join(', ')}<br>`;
    if (details.severity)           html += `<strong>Severity:</strong> ${details.severity}<br>`;
    if (details.recommended_action) html += `<strong>Action:</strong> ${details.recommended_action}`;
    html += '</div>';
    container.innerHTML = html;
}

function getConditionColorClass(pci) {
    if (pci >= 85) return 'condition-excellent';
    if (pci >= 70) return 'condition-good';
    if (pci >= 55) return 'condition-fair';
    if (pci >= 40) return 'condition-poor';
    return 'condition-critical';
}

function getConditionRating(pci) {
    if (pci >= 85) return 'Excellent';
    if (pci >= 70) return 'Good';
    if (pci >= 55) return 'Fair';
    if (pci >= 40) return 'Poor';
    return 'Critical';
}

function getSimulatedQRLData(location) {
    const seed = location.lat() * location.lng() * 10000;
    const pci  = 40 + Math.abs(Math.sin(seed)) * 50;

    let riskLabel = 'NORMAL';
    let riskProbs = { NORMAL:0.70, WATCH:0.20, CONGESTED:0.08, CRITICAL:0.02 };
    let distress  = ['Minor Surface Wear'];
    let action    = 'No intervention needed';

    if (pci < 55) {
        riskLabel = 'CRITICAL';
        riskProbs = { NORMAL:0.05, WATCH:0.15, CONGESTED:0.30, CRITICAL:0.50 };
        distress  = ['Severe Cracking', 'Potholes', 'Structural Damage'];
        action    = 'Immediate repair required';
    } else if (pci < 70) {
        riskLabel = 'CONGESTED';
        riskProbs = { NORMAL:0.10, WATCH:0.25, CONGESTED:0.50, CRITICAL:0.15 };
        distress  = ['Cracking', 'Rutting', 'Edge Deterioration'];
        action    = 'Plan maintenance within 6 months';
    } else if (pci < 85) {
        riskLabel = 'WATCH';
        riskProbs = { NORMAL:0.25, WATCH:0.48, CONGESTED:0.20, CRITICAL:0.07 };
        distress  = ['Light Cracking', 'Surface Oxidation'];
        action    = 'Schedule routine inspection';
    }

    return {
        pci,
        condition:  getConditionRating(pci),
        confidence: 0.85 + Math.random() * 0.15,
        timestamp:  new Date().toISOString(),
        location:   { latitude: location.lat(), longitude: location.lng() },
        details: {
            distress_types:     distress,
            severity:           riskLabel === 'CRITICAL' ? 'High' : riskLabel === 'CONGESTED' ? 'Medium' : 'Low',
            recommended_action: action,
            qrl_analysis: {
                risk_label:          riskLabel,
                risk_probabilities:  riskProbs,
                quantum_confidence:  riskProbs[riskLabel],
                analysis_method:     'Quantum Reinforcement Learning'
            }
        }
    };
}

// ─── Utilities ───────────────────────────────────────────────────────────────
function updateStatus(message) {
    document.getElementById('status-text').textContent = message;
}

function updateLastUpdate() {
    const el = document.getElementById('last-update');
    if (el) el.textContent = new Date().toLocaleTimeString('en-US', { hour:'2-digit', minute:'2-digit' });
}

function showElement(id) { document.getElementById(id).style.display = 'block'; }
function hideElement(id) { document.getElementById(id).style.display = 'none';  }

function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => document.body.removeChild(toast), 300);
    }, 3500);
}

setInterval(updateLastUpdate, 60000);

window.addEventListener('error', e => {
    if (e.message.includes('Google Maps')) alert('Error loading Google Maps. Please check your API key.');
});

// ─── Real network conditions from API measurement ────────────────────────────
function applyMeasuredNetworkConditions(latencyMs) {
    // Clamp to the simulation's valid range
    netState.latency = Math.max(10, Math.min(220, latencyMs));

    // Derive packet loss: grows non-linearly above 100 ms
    netState.packetLoss = Math.max(0, Math.min(18, (latencyMs - 30) / 20));

    // Derive QBER: low latency → clean channel; high latency → degraded channel
    // Maps 10 ms → ~1.5 %,  150 ms → ~7 %,  220 ms → ~10 %
    netState.qber = Math.max(0.5, Math.min(12, 1.5 + (latencyMs / 220) * 9));
    netState.eavesdrop    = netState.qber > 8.5;
    netState.qkdOk        = netState.qber < 6;
    netState.secureChannels = netState.qkdOk ? 4
        : Math.max(1, Math.floor(4 * (1 - (netState.qber - 6) / 6)));

    // Re-render immediately if the security tab is open
    if (activeTab === 'security') renderSecurityPanel();
}

// ─── Network Security Simulation ─────────────────────────────────────────────
let securitySimInterval = null;

const netState = {
    latency:        24,
    packetLoss:     1.2,
    nodes:          Array.from({ length: 12 }, (_, i) => ({ id: i, status: 'online' })),
    threatLevel:    'LOW',
    spoofed:        0,
    intercepted:    0,
    dos:            0,
    threatLog:      [],
    keyRate:        128,
    qber:           1.8,
    eavesdrop:      false,
    qkdOk:          true,
    secureChannels: 4
};

function startSecuritySim() {
    if (securitySimInterval) return;
    renderSecurityPanel();
    securitySimInterval = setInterval(() => { evolveNetState(); renderSecurityPanel(); }, 2500);
}

function stopSecuritySim() {
    clearInterval(securitySimInterval);
    securitySimInterval = null;
}

function evolveNetState() {
    netState.latency    = Math.max(10,  Math.min(220, netState.latency    + (Math.random() - 0.48) * 12));
    netState.packetLoss = Math.max(0,   Math.min(18,  netState.packetLoss + (Math.random() - 0.48) * 0.8));

    if (Math.random() < 0.25) {
        const idx  = Math.floor(Math.random() * netState.nodes.length);
        const roll = Math.random();
        netState.nodes[idx].status = roll < 0.75 ? 'online' : roll < 0.90 ? 'degraded' : 'offline';
    }

    if (Math.random() < 0.12) { netState.spoofed++;     pushThreatLog('warn', `Spoofed sensor detected (node ${Math.floor(Math.random()*12)})`); }
    if (Math.random() < 0.08) { netState.intercepted++; pushThreatLog('crit', 'Interception attempt blocked'); }
    if (Math.random() < 0.06) { netState.dos++;          pushThreatLog('warn', 'DoS probe detected – rate-limited'); }

    const score = netState.spoofed + netState.intercepted * 2 + netState.dos;
    netState.threatLevel = score < 3 ? 'LOW' : score < 8 ? 'MEDIUM' : 'HIGH';

    netState.keyRate      = Math.max(32,  Math.min(512, netState.keyRate + (Math.random() - 0.5) * 20));
    netState.qber         = Math.max(0.5, Math.min(12,  netState.qber   + (Math.random() - 0.48) * 0.3));
    netState.eavesdrop    = netState.qber > 8.5;
    netState.qkdOk        = netState.qber < 6;
    netState.secureChannels = netState.qkdOk ? 4 : Math.max(1, Math.floor(4 * (1 - (netState.qber - 6) / 6)));
}

function pushThreatLog(level, msg) {
    const t = new Date().toLocaleTimeString('en-US', { hour:'2-digit', minute:'2-digit', second:'2-digit' });
    netState.threatLog.unshift({ level, msg, time: t });
    if (netState.threatLog.length > 6) netState.threatLog.pop();
}

function renderSecurityPanel() {
    // Latency
    const latMs = Math.round(netState.latency);
    document.getElementById('net-latency').textContent = `${latMs} ms`;
    const latBar = document.getElementById('net-latency-bar');
    latBar.style.width      = `${Math.min(100, (latMs / 220) * 100)}%`;
    latBar.style.background = latMs < 60 ? '#00b478' : latMs < 120 ? '#ffd700' : '#ff4444';

    // Packet loss
    const pl = netState.packetLoss.toFixed(1);
    document.getElementById('net-packet-loss').textContent = `${pl} %`;
    const plBar = document.getElementById('net-packet-bar');
    plBar.style.width      = `${Math.min(100, (netState.packetLoss / 18) * 100)}%`;
    plBar.style.background = netState.packetLoss < 3 ? '#00b478' : netState.packetLoss < 8 ? '#ffd700' : '#ff4444';

    // Nodes
    const online   = netState.nodes.filter(n => n.status === 'online').length;
    const degraded = netState.nodes.filter(n => n.status === 'degraded').length;
    const offline  = netState.nodes.filter(n => n.status === 'offline').length;
    document.getElementById('net-nodes').textContent = `${online} on · ${degraded} deg · ${offline} off`;
    document.getElementById('node-status-grid').innerHTML = netState.nodes.map(n =>
        `<div class="node-dot node-${n.status}" title="Node ${n.id}: ${n.status}"></div>`
    ).join('');

    // Threat
    const badge = document.getElementById('threat-level-badge');
    badge.textContent = netState.threatLevel;
    badge.className   = 'sec-badge ' + (netState.threatLevel === 'LOW' ? 'badge-secure' : netState.threatLevel === 'MEDIUM' ? 'badge-warning' : 'badge-critical');

    document.getElementById('spoofed-sensors').textContent  = netState.spoofed;
    document.getElementById('intercept-events').textContent = netState.intercepted;
    document.getElementById('dos-attempts').textContent     = netState.dos;

    const log = document.getElementById('threat-log');
    log.innerHTML = netState.threatLog.length
        ? netState.threatLog.map(e => `<div class="threat-log-entry ${e.level}">[${e.time}] ${e.msg}</div>`).join('')
        : '<div style="color:#3a3a3a;font-size:10px;">No events recorded</div>';

    // QKD
    const qBadge = document.getElementById('qkd-status-badge');
    qBadge.textContent = netState.qkdOk ? 'SECURE' : netState.eavesdrop ? 'COMPROMISED' : 'DEGRADED';
    qBadge.className   = 'sec-badge ' + (netState.qkdOk ? 'badge-secure' : netState.eavesdrop ? 'badge-critical' : 'badge-warning');

    document.getElementById('qkd-key-rate').textContent  = `${Math.round(netState.keyRate)} kbps`;
    document.getElementById('qkd-qber').textContent      = `${netState.qber.toFixed(2)} %`;
    document.getElementById('qkd-eavesdrop').textContent = netState.eavesdrop ? '⚠️ YES' : 'No';
    document.getElementById('qkd-channels').textContent  = `${netState.secureChannels} / 4`;

    document.getElementById('sec-last-update').textContent =
        new Date().toLocaleTimeString('en-US', { hour:'2-digit', minute:'2-digit', second:'2-digit' });
}
