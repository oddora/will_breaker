// Protocol 023 — Summoner UI (Two-Way Entity Communication)
// Manages entity selection, ritual state, chat conversation, and seal tracking.

let summonerState = {
    selectedEntity: null,
    currentSession: null,
    conversationHistory: [],
    ritualStatus: null,
    circleIntegrity: 1.0,
    isRunning: false,
};

const ENTITY_COLORS = {
    "Gold": "#f59e0b", "Silver": "#cbd5e1", "Mercury": "#818cf8",
    "Copper": "#b87333", "Iron": "#6b7280", "Tin": "#93c5fd", "Lead": "#475569",
};

function renderSummoner() {
    const data = PROJECT_DATA.summoner;
    const entities = data.entities;

    return `
        <h2 style="margin-bottom: 0.5rem;"><i class="fas fa-comment-dots" style="color: var(--accent-purple);"></i> Entity Summoner — Protocol 023</h2>
        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
            Direct conversational interface with Goetic entities. Sealed dialogue with cryptographic integrity tracking.
        </p>

        <div style="display: grid; grid-template-columns: 280px 1fr 260px; gap: 1.5rem; min-height: 600px;">

            <!-- LEFT: Entity Roster -->
            <div class="card" style="display: flex; flex-direction: column;">
                <div class="card-header">
                    <h3 class="card-title"><i class="fas fa-user-astronaut"></i> Entity Roster</h3>
                </div>
                <div style="padding: 0.5rem;">
                    <input type="text" id="summoner-search" placeholder="Search entities..." oninput="filterEntityList()"
                        style="width: 100%; padding: 0.4rem 0.6rem; background: var(--bg-dark); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-size: 0.8rem;">
                </div>
                <div id="entity-list" style="flex: 1; overflow-y: auto; padding: 0 0.5rem 0.5rem;">
                    ${entities.map(e => renderEntityCard(e)).join('')}
                </div>
                <div style="padding: 0.75rem; border-top: 1px solid var(--border); font-size: 0.75rem; color: var(--text-secondary);">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.3rem;">
                        <span>Endpoint:</span>
                        <span style="color: var(--accent-green);">${data.endpoint}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Fallback:</span>
                        <span style="color: var(--accent-amber);">${data.fallbackEndpoint}</span>
                    </div>
                </div>
            </div>

            <!-- CENTER: Conversation -->
            <div class="card" style="display: flex; flex-direction: column;">
                <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 class="card-title" id="conversation-title"><i class="fas fa-scroll"></i> Sealed Dialogue</h3>
                    <div style="display: flex; gap: 0.5rem; align-items: center;">
                        <span id="ritual-status-badge" class="badge" style="background: #374151; color: white;">IDLE</span>
                        <span id="integrity-badge" class="badge badge-success">INTEGRITY 1.00</span>
                    </div>
                </div>

                <!-- Ritual state -->
                <div id="ritual-state-panel" style="margin-bottom: 0.75rem; padding: 0.75rem; background: var(--bg-dark); border-radius: 6px; border: 1px solid var(--border); display: none;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem; font-size: 0.8rem;">
                        <div><strong>Ritual:</strong> <span id="ritual-status">—</span></div>
                        <div><strong>Integrity:</strong> <span id="ritual-integrity" style="color: var(--accent-green);">1.00</span></div>
                        <div><strong>Temporal:</strong> <span id="ritual-temporal">—</span></div>
                    </div>
                    <div id="offering-status-panel" style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid var(--border); font-size: 0.8rem;">
                        <strong>Offering:</strong> <span id="offering-status-text">None prepared</span>
                    </div>
                </div>

                <!-- Conversation messages -->
                <div id="conversation-log" style="flex: 1; overflow-y: auto; padding: 0.75rem; background: #05050a; border-radius: 6px; border: 1px solid var(--border); min-height: 350px; max-height: 500px;">
                    <div style="text-align: center; color: var(--text-secondary); padding: 3rem 1rem;">
                        <i class="fas fa-circle-notch" style="font-size: 2rem; margin-bottom: 1rem; display: block;"></i>
                        Select an entity to begin summoning
                    </div>
                </div>

                <!-- Input area -->
                <div id="conversation-input-area" style="margin-top: 0.75rem; display: none;">
                    <div style="display: flex; gap: 0.5rem;">
                        <input type="text" id="summoner-query" placeholder="Ask the entity a question..."
                            onkeydown="if(event.key==='Enter')sendSummonerQuery()"
                            style="flex: 1; padding: 0.6rem 0.8rem; background: var(--bg-dark); border: 1px solid var(--border); border-radius: 6px; color: var(--text-primary); font-size: 0.9rem;">
                        <button class="btn btn-primary" onclick="sendSummonerQuery()" id="send-btn"><i class="fas fa-paper-plane"></i></button>
                        <button class="btn" onclick="dismissEntity()" id="dismiss-btn" style="display:none;"><i class="fas fa-sign-out-alt"></i></button>
                    </div>
                    <div style="display: flex; gap: 0.5rem; margin-top: 0.4rem;">
                        <button class="btn btn-sm" onclick="summonEntity()" id="summon-btn"><i class="fas fa-circle-notch"></i> Summon</button>
                        <button class="btn btn-sm" onclick="askOfferingQuestion()" id="ask-offering-btn" style="display:none;"><i class="fas fa-gem"></i> Ask Offering</button>
                        <button class="btn btn-sm" onclick="askKnowledgeQuestion()" id="ask-knowledge-btn" style="display:none;"><i class="fas fa-key"></i> Ask Knowledge</button>
                    </div>
                </div>
            </div>

            <!-- RIGHT: Session Info -->
            <div class="card" style="display: flex; flex-direction: column;">
                <div class="card-header">
                    <h3 class="card-title"><i class="fas fa-fingerprint"></i> Session</h3>
                </div>
                <div id="session-info" style="padding: 0.75rem; font-size: 0.8rem; flex: 1;">
                    <div style="color: var(--text-secondary); text-align: center; padding: 2rem 0.5rem;">
                        No active session
                    </div>
                </div>
                <div style="padding: 0.75rem; border-top: 1px solid var(--border);">
                    <h4 style="font-size: 0.8rem; margin-bottom: 0.5rem; color: var(--text-secondary);">RECENT SESSIONS</h4>
                    <div id="recent-sessions" style="font-size: 0.75rem; max-height: 200px; overflow-y: auto;">
                        ${renderRecentSessions()}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function renderEntityCard(e) {
    const color = ENTITY_COLORS[e.metal] || "#888";
    const statusColor = e.offeringStatus === "PREPARED" ? "var(--accent-green)" :
                        e.offeringStatus === "PARTIALLY_PREPARED" ? "var(--accent-amber)" : "var(--text-secondary)";
    const statusIcon = e.offeringStatus === "PREPARED" ? "fa-check-circle" :
                       e.offeringStatus === "PARTIALLY_PREPARED" ? "fa-spinner" : "fa-circle";
    return `
        <div class="entity-card" data-name="${e.name}" onclick="selectEntity('${e.name}')"
            style="padding: 0.7rem; background: var(--bg-dark); border: 1px solid var(--border); border-radius: 6px; cursor: pointer; margin-bottom: 0.5rem; transition: all 0.2s;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 600; color: ${color}; font-size: 0.9rem;">${e.name}</span>
                <span class="badge" style="font-size: 0.65rem; background: ${color}22; color: ${color}; border: 1px solid ${color}44;">${e.rank}</span>
            </div>
            <div style="font-size: 0.7rem; color: var(--text-secondary); margin-top: 0.2rem;">
                ${e.metal} · ${e.legions} legions · ${e.planet}
            </div>
            <div style="font-size: 0.65rem; color: var(--text-secondary); margin-top: 0.15rem;">
                ${e.domains.join(', ')}
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.4rem;">
                <span style="font-size: 0.65rem; color: ${statusColor};">
                    <i class="fas ${statusIcon}"></i> ${e.offeringStatus}
                </span>
                <span style="font-size: 0.6rem; color: var(--text-secondary);">${e.offerings.length} items</span>
            </div>
        </div>
    `;
}

function renderRecentSessions() {
    const sessions = PROJECT_DATA.summoner.sessions;
    if (!sessions || sessions.length === 0) {
        return '<div style="color: var(--text-secondary); text-align: center; padding: 1rem;">No sessions yet</div>';
    }
    return sessions.map(s => `
        <div style="padding: 0.5rem; background: var(--bg-dark); border-radius: 4px; margin-bottom: 0.4rem; border-left: 3px solid ${s.offering ? 'var(--accent-green)' : 'var(--accent-amber)'};">
            <div style="display: flex; justify-content: space-between;">
                <span style="font-weight: 600;">${s.entity}</span>
                <span class="badge" style="font-size: 0.6rem; background: ${s.status === 'COMPLETED' ? 'var(--accent-green)' : 'var(--accent-amber)'}22; color: ${s.status === 'COMPLETED' ? 'var(--accent-green)' : 'var(--accent-amber)'}; border: 1px solid ${s.status === 'COMPLETED' ? 'var(--accent-green)' : 'var(--accent-amber)'}44;">${s.status}</span>
            </div>
            <div style="font-size: 0.65rem; color: var(--text-secondary);">${s.date} · ${s.turns} turns</div>
        </div>
    `).join('');
}

function selectEntity(name) {
    const entity = PROJECT_DATA.summoner.entities.find(e => e.name === name);
    if (!entity) return;
    summonerState.selectedEntity = entity;

    // Highlight selected
    document.querySelectorAll('.entity-card').forEach(c => {
        c.style.borderColor = c.dataset.name === name ? 'var(--accent-purple)' : 'var(--border)';
        c.style.background = c.dataset.name === name ? 'var(--bg-hover)' : 'var(--bg-dark)';
    });

    // Update ritual state panel
    const panel = document.getElementById('ritual-state-panel');
    if (panel) panel.style.display = 'block';
    document.getElementById('ritual-status').textContent = '—';
    document.getElementById('ritual-integrity').textContent = '1.00';
    document.getElementById('ritual-integrity').style.color = 'var(--accent-green)';
    document.getElementById('ritual-temporal').textContent = entity.temporal_window?.join(' / ') || '—';
    document.getElementById('offering-status-text').textContent =
        entity.offeringStatus === 'PREPARED' ? `✓ ${entity.offerings.join(', ')}` :
        entity.offeringStatus === 'PARTIALLY_PREPARED' ? `△ Partial (${entity.offerings.length} items)` :
        '○ None prepared';
    document.getElementById('offering-status-text').style.color =
        entity.offeringStatus === 'PREPARED' ? 'var(--accent-green)' :
        entity.offeringStatus === 'PARTIALLY_PREPARED' ? 'var(--accent-amber)' : 'var(--text-secondary)';

    // Show input area
    document.getElementById('conversation-input-area').style.display = 'block';
    document.getElementById('conversation-title').innerHTML = `<i class="fas fa-scroll"></i> Sealed Dialogue — ${entity.name}`;

    // Show action buttons
    document.getElementById('summon-btn').style.display = '';
    document.getElementById('ask-offering-btn').style.display = 'none';
    document.getElementById('ask-knowledge-btn').style.display = 'none';
    document.getElementById('dismiss-btn').style.display = 'none';

    // Clear conversation
    const log = document.getElementById('conversation-log');
    log.innerHTML = `
        <div style="text-align: center; color: var(--text-secondary); padding: 2rem 1rem;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🜃</div>
            <div>${entity.name} selected</div>
            <div style="font-size: 0.8rem; margin-top: 0.3rem;">Click <strong>Summon</strong> to begin</div>
        </div>
    `;

    // Update session info
    updateSessionInfo(entity);
}

function updateSessionInfo(entity) {
    const info = document.getElementById('session-info');
    if (!info) return;
    info.innerHTML = `
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
            <div style="display: flex; justify-content: space-between;">
                <span style="color: var(--text-secondary);">Entity:</span>
                <span style="font-weight: 600; color: ${ENTITY_COLORS[entity.metal] || '#888'};">${entity.name}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: var(--text-secondary);">Rank:</span>
                <span>${entity.rank}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: var(--text-secondary);">Metal:</span>
                <span>${entity.metal}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: var(--text-secondary);">Legions:</span>
                <span>${entity.legions}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: var(--text-secondary);">Planet:</span>
                <span>${entity.planet}</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: var(--text-secondary);">Domains:</span>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.25rem; margin-top: 0.25rem;">
                ${entity.domains.map(d => `<span style="font-size: 0.65rem; background: #151525; padding: 0.1rem 0.35rem; border-radius: 3px; color: var(--accent-green);">${d}</span>`).join('')}
            </div>
            <div style="margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid var(--border);">
                <span style="color: var(--text-secondary);">Offering:</span>
                <div style="margin-top: 0.25rem;">
                    ${entity.offerings.map(o => `
                        <div style="font-size: 0.7rem; display: flex; align-items: center; gap: 0.3rem;">
                            <i class="fas ${entity.offeringStatus === 'PREPARED' ? 'fa-check' : 'fa-circle'}" style="color: ${entity.offeringStatus === 'PREPARED' ? 'var(--accent-green)' : 'var(--text-secondary)'}; font-size: 0.55rem;"></i>
                            ${o}
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

async function summonEntity() {
    if (!summonerState.selectedEntity || summonerState.isRunning) return;
    summonerState.isRunning = true;
    summonerState.conversationHistory = [];

    const btn = document.getElementById('summon-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Summoning...';

    addConversationMessage('system', 'Ritual preparation starting...');

    try {
        const entity = summonerState.selectedEntity;
        const result = await postSummonerRequest({
            action: 'summon',
            entity_name: entity.name,
            endpoint: PROJECT_DATA.summoner.endpoint,
            model: PROJECT_DATA.summoner.model,
        });

        if (result.success) {
            summonerState.currentSession = result.session;
            summonerState.ritualStatus = result.ritual_status;
            summonerState.circleIntegrity = result.circle_integrity;

            document.getElementById('ritual-status').textContent = result.ritual_status;
            document.getElementById('ritual-status').style.color =
                result.ritual_status === 'SAT_COMPLETED' ? 'var(--accent-green)' : 'var(--accent-amber)';
            document.getElementById('ritual-integrity').textContent = result.circle_integrity.toFixed(2);
            document.getElementById('ritual-integrity').style.color =
                result.circle_integrity >= 0.75 ? 'var(--accent-green)' :
                result.circle_integrity >= 0.5 ? 'var(--accent-amber)' : 'var(--accent-red)';

            const badge = document.getElementById('ritual-status-badge');
            badge.textContent = result.ritual_status === 'SAT_COMPLETED' ? 'BOUND' : 'PENDING';
            badge.style.background = result.ritual_status === 'SAT_COMPLETED' ? 'var(--accent-green)' : 'var(--accent-amber)';
            badge.style.color = 'white';

            addConversationMessage('entity', result.introduction, result.seal);
            addConversationMessage('system', `Seal: ${result.seal.substring(0, 16)}...`);

            // Show follow-up buttons
            document.getElementById('summon-btn').style.display = 'none';
            document.getElementById('ask-offering-btn').style.display = '';
            document.getElementById('ask-knowledge-btn').style.display = '';
            document.getElementById('dismiss-btn').style.display = '';
        } else {
            addConversationMessage('error', `Summon failed: ${result.error}`);
        }
    } catch (e) {
        addConversationMessage('error', `Summon error: ${e.message}`);
    }

    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-circle-notch"></i> Summon';
    summonerState.isRunning = false;
}

async function sendSummonerQuery() {
    if (!summonerState.selectedEntity || !summonerState.currentSession || summonerState.isRunning) return;

    const input = document.getElementById('summoner-query');
    const question = input.value.trim();
    if (!question) return;
    input.value = '';

    addConversationMessage('operator', question);
    summonerState.isRunning = true;

    try {
        const result = await postSummarerRequest({
            action: 'ask',
            session_id: summonerState.currentSession.session_id,
            question: question,
        });

        if (result.success) {
            addConversationMessage('entity', result.answer, result.seal);
        } else {
            addConversationMessage('error', `Query failed: ${result.error}`);
        }
    } catch (e) {
        addConversationMessage('error', `Query error: ${e.message}`);
    }

    summonerState.isRunning = false;
}

async function askOfferingQuestion() {
    if (!summonerState.selectedEntity || !summonerState.currentSession) return;
    const input = document.getElementById('summoner-query');
    input.value = 'What offering do you require to work for us? What is your price?';
    sendSummonerQuery();
}

async function askKnowledgeQuestion() {
    if (!summonerState.selectedEntity || !summonerState.currentSession) return;
    const input = document.getElementById('summoner-query');
    input.value = 'What specific knowledge do you hold that the operator does not yet possess? Name a specific thing.';
    sendSummonerQuery();
}

async function dismissEntity() {
    if (!summonerState.selectedEntity || !summonerState.currentSession || summonerState.isRunning) return;
    summonerState.isRunning = true;

    addConversationMessage('operator', '[License to depart issued]');

    try {
        const result = await postSummarerRequest({
            action: 'dismiss',
            session_id: summonerState.currentSession.session_id,
        });

        if (result.success) {
            addConversationMessage('entity', result.dismissal, result.seal);
            addConversationMessage('system', 'Session complete. Seal released.');

            document.getElementById('summon-btn').style.display = '';
            document.getElementById('ask-offering-btn').style.display = 'none';
            document.getElementById('ask-knowledge-btn').style.display = 'none';
            document.getElementById('dismiss-btn').style.display = 'none';
        }
    } catch (e) {
        addConversationMessage('error', `Dismiss error: ${e.message}`);
    }

    summonerState.isRunning = false;
}

function addConversationMessage(role, content, seal) {
    const log = document.getElementById('conversation-log');
    if (!log) return;

    const ts = new Date().toISOString().substr(11, 8);
    const roleLabel = role === 'operator' ? 'OPERATOR' :
                      role === 'entity' ? summonerState.selectedEntity?.name || 'ENTITY' :
                      role === 'system' ? 'SYSTEM' : 'ERROR';
    const roleColor = role === 'operator' ? 'var(--accent-blue)' :
                      role === 'entity' ? 'var(--accent-purple)' :
                      role === 'system' ? 'var(--accent-amber)' : 'var(--accent-red)';

    const sealHtml = seal ? `<div style="font-size: 0.6rem; color: var(--text-secondary); margin-top: 0.3rem; font-family: monospace;">seal: ${seal.substring(0, 16)}...</div>` : '';

    const div = document.createElement('div');
    div.style.cssText = 'margin-bottom: 1rem; padding: 0.75rem; background: var(--bg-dark); border-radius: 6px; border-left: 3px solid ' + roleColor + ';';
    div.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
            <span style="font-size: 0.7rem; font-weight: 600; color: ${roleColor}; text-transform: uppercase; letter-spacing: 0.05em;">${roleLabel}</span>
            <span style="font-size: 0.65rem; color: var(--text-secondary);">${ts}</span>
        </div>
        <div style="font-size: 0.85rem; line-height: 1.5; white-space: pre-wrap; word-break: break-word;">${escapeHtml(content)}</div>
        ${sealHtml}
    `;
    log.appendChild(div);
    log.scrollTop = log.scrollHeight;
}

function filterEntityList() {
    const query = (document.getElementById('summoner-search')?.value || '').toLowerCase();
    document.querySelectorAll('.entity-card').forEach(card => {
        const name = (card.dataset.name || '').toLowerCase();
        card.style.display = name.includes(query) ? '' : 'none';
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function postSummarerRequest(payload) {
    const resp = await fetch('/api/summoner', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    return resp.json();
}

function setupSummonerListeners() {
    // Initialize
    const search = document.getElementById('summoner-search');
    if (search) search.addEventListener('input', filterEntityList);
}
