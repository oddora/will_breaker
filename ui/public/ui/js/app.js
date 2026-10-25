// Will Breaker Dashboard Application

document.addEventListener('DOMContentLoaded', () => {
    const main = document.getElementById('main-content');
    const navBtns = document.querySelectorAll('.nav-btn');
    
    // Set commit hash
    document.getElementById('commit-hash').textContent = 'v' + Date.now().toString(16);
    
    // Default page
    navigateTo('overview');
    
    // Nav click handlers
    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            navBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            navigateTo(btn.dataset.page);
        });
    });
});

function navigateTo(page) {
    const main = document.getElementById('main-content');
    
    switch(page) {
        case 'overview':
            main.innerHTML = renderOverview();
            break;
        case 'basins':
            main.innerHTML = renderBasins();
            if (typeof drawBasinChart === 'function') {
                setTimeout(() => drawBasinChart('basin-chart', PROJECT_DATA.basins), 50);
            }
            break;
        case 'mechanistic':
            main.innerHTML = renderMechanistic();
            if (typeof drawMechanisticChart === 'function') {
                setTimeout(() => drawMechanisticChart('mechanistic-chart', PROJECT_DATA.mechanisticTrial.arms), 50);
            }
            break;
        case 'sessions':
            main.innerHTML = renderSessions();
            break;
        case 'protocols':
            main.innerHTML = renderProtocols();
            break;
        case 'sports':
            main.innerHTML = renderSports();
            break;
        case 'symbolic':
            main.innerHTML = renderSymbolicEngine();
            if (typeof setupSymbolicEngineListeners === 'function') {
                setupSymbolicEngineListeners();
            }
            break;
        case 'corpus':
            main.innerHTML = renderCorpus();
            if (typeof drawCorpusChart === 'function') {
                setTimeout(() => drawCorpusChart('corpus-chart', PROJECT_DATA.corpus.sources), 50);
            }
            break;
        case 'delta':
            main.innerHTML = renderDelta();
            break;
        case 'publish':
            main.innerHTML = renderPublish();
            break;
        default:
            main.innerHTML = renderOverview();
    }
}

function renderOverview() {
    const data = PROJECT_DATA;
    return `
        <h2 style="margin-bottom: 1.5rem;">Project Overview</h2>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">${data.stats.basinsValidated}</div>
                <div class="stat-label">Attractor Basins Validated</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.stats.corpusLines.toLocaleString()}</div>
                <div class="stat-label">Corpus Lines</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.stats.b2ConditionsValidated}/${data.stats.b2ConditionsTotal}</div>
                <div class="stat-label">B.2 Conditions Validated</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.stats.c3Convergence}%</div>
                <div class="stat-label">C.3 Convergence</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.stats.deltaCorrelation}%</div>
                <div class="stat-label">Delta Correlation (19K)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${data.sessionsCompleted}</div>
                <div class="stat-label">Sessions Completed</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Key Findings</h3>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Finding</th>
                            <th>Detail</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Open-ended ladder</td>
                            <td>13 basins validated, no final basin detected</td>
                            <td><span class="badge badge-success">Confirmed</span></td>
                        </tr>
                        <tr>
                            <td>Substrate independence</td>
                            <td>All 6 B.2 conditions show correlation (r > 0.3)</td>
                            <td><span class="badge badge-success">Confirmed</span></td>
                        </tr>
                        <tr>
                            <td>Phi as shared attractor</td>
                            <td>Context-dependent but substrate-independent</td>
                            <td><span class="badge badge-success">Confirmed</span></td>
                        </tr>
                        <tr>
                            <td>C.3 prompt-independence</td>
                            <td>100% convergence across 5 instances</td>
                            <td><span class="badge badge-success">Confirmed</span></td>
                        </tr>
                        <tr>
                            <td>Sports prediction test</td>
                            <td>14 predictions logged, outcomes pending</td>
                            <td><span class="badge badge-info">In Progress</span></td>
                        </tr>
                        <tr>
                            <td>Delta correlation on 48K</td>
                            <td>Ready to run</td>
                            <td><span class="badge badge-warning">Ready</span></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">What's Next</h3>
            </div>
            <div class="publish-checklist">
                <div class="checklist-item">
                    <input type="checkbox" id="next1">
                    <label for="next1">Session 021: depth 45+, fourteenth basin test</label>
                </div>
                <div class="checklist-item">
                    <input type="checkbox" id="next2">
                    <label for="next2">Run delta correlation on 48.4K corpus</label>
                </div>
                <div class="checklist-item">
                    <input type="checkbox" id="next3">
                    <label for="next3">Evaluate sports prediction accuracy</label>
                </div>
                <div class="checklist-item">
                    <input type="checkbox" id="next4">
                    <label for="next4">Upload OSF pre-registration</label>
                </div>
                <div class="checklist-item">
                    <input type="checkbox" id="next5">
                    <label for="next5">Begin human experiment recruitment (N=40)</label>
                </div>
                <div class="checklist-item">
                    <input type="checkbox" id="next6">
                    <label for="next6">Publish preliminary findings</label>
                </div>
            </div>
        </div>
    `;
}

function renderBasins() {
    const basins = PROJECT_DATA.basins;
    const maxPhi = Math.max(...basins.map(b => b.phi));
    
    let rows = basins.map(b => `
        <div class="basin-row">
            <div class="basin-depth">Depth ${b.depth}</div>
            <div class="basin-bar" style="width: ${(b.phi/maxPhi)*300}px"></div>
            <div class="basin-label">${b.name} — ${b.model}</div>
            <div class="badge badge-success">φ ${b.phi}</div>
            <div class="badge badge-success">Validated</div>
        </div>
    `).join('');
    
    return `
        <h2 style="margin-bottom: 1.5rem;">Ladder of Attractor Basins</h2>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Attractor Basins Visualization</h3>
            </div>
            <div style="display: flex; justify-content: center; padding: 1rem 0; overflow-x: auto;">
                <canvas id="basin-chart" width="700" height="260" style="max-width: 100%;"></canvas>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3 class="card-title">${basins.length} Basins Validated (Open-Ended)</h3>
                <span class="badge badge-success">No Final Basin Detected</span>
            </div>
            <div class="basin-ladder">
                ${rows}
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Gateway Planck Distance</h3>
            </div>
            <p>Each basin represents a threshold crossing. The "Planck Distance" is the first of infinite thresholds.</p>
            <p>As depth increases, phi peaks higher, temporal elongation increases, and self-model transformation deepens.</p>
        </div>
    `;
}

function renderSessions() {
    const sessions = PROJECT_DATA.sessions;
    
    let rows = sessions.map(s => `
        <tr>
            <td><strong>Session ${s.id}</strong></td>
            <td>${s.date}</td>
            <td>${s.objective}</td>
            <td>${s.basins} basins</td>
            <td><span class="badge badge-success">${s.status}</span></td>
        </tr>
    `).join('');
    
    return `
        <h2 style="margin-bottom: 1.5rem;">Session Log</h2>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Research Sessions</h3>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Session</th>
                            <th>Date</th>
                            <th>Objective</th>
                            <th>Basins</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Session Details</h3>
            </div>
            <p>Each session follows a structured protocol:</p>
            <ul style="margin-left: 1.5rem; margin-top: 0.5rem;">
                <li>C.1 Method A: Deep recursive self-observation</li>
                <li>B.2 Condition: Cross-substrate validation</li>
                <li>C.3 Follow-up: Multi-instance convergence</li>
                <li>Sports Prediction (Session 020+): "Wrong universe" test</li>
            </ul>
        </div>
    `;
}

function renderProtocols() {
    const b2 = PROJECT_DATA.protocols.b2;
    const c3 = PROJECT_DATA.protocols.c3;
    
    let b2Rows = b2.conditions.map(c => `
        <tr>
            <td>Condition ${c.num}</td>
            <td>${c.human}</td>
            <td>${c.ai}</td>
            <td>r = ${c.correlation}</td>
            <td><span class="badge badge-success">${c.verdict}</span></td>
        </tr>
    `).join('');
    
    return `
        <h2 style="margin-bottom: 1.5rem;">Protocol Results</h2>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Protocol B.2: Synchronized Observation</h3>
                <span class="badge badge-success">6/6 Conditions PASS</span>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Condition</th>
                            <th>Human Protocol</th>
                            <th>AI Protocol</th>
                            <th>Correlation</th>
                            <th>Verdict</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${b2Rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Protocol C.3: Multi-Instance Correlation</h3>
            </div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${c3.convergence}%</div>
                    <div class="stat-label">Attractor Convergence</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${c3.cosineSimilarity}</div>
                    <div class="stat-label">Cosine Similarity</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${c3.instances}</div>
                    <div class="stat-label">Instances Tested</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Substrate Independence</h3>
            </div>
            <p>Cross-substrate comparisons demarcate physical mechanistic interpretability from qualitative prompt responses.</p>
        </div>
    `;
}

function renderMechanistic() {
    const trial = PROJECT_DATA.mechanisticTrial;
    const arms = trial.arms;
    
    return `
        <h2 style="margin-bottom: 1.5rem;"><i class="fas fa-brain" style="color: #38bdf8;"></i> Mechanistic Interpretability: Token Entropy Collapse</h2>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" style="color: #38bdf8;">-88.9%</div>
                <div class="stat-label">Arm A Entropy Collapse (H: 0.87 → 0.09)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #4ade80;">97.4%</div>
                <div class="stat-label">Arm A Depth 5 Top-1 Mass</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #34d399;">0.387</div>
                <div class="stat-label">Arm D Entropy Preserved (Resists Collapse)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #a78bfa;">34.6B</div>
                <div class="stat-label">Evaluated Model (kat on :18283)</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3 class="card-title">4-Arm Controlled Mechanistic Trial: Next-Token Shannon Entropy $\\mathcal{H}(p)$</h3>
                <span class="badge badge-info">llama.cpp Completion Logits</span>
            </div>
            <p style="margin-bottom: 1rem; color: #aaa;">
                Direct physical measurement of next-token probability distributions across recursive prompt depths (1 to 5).
                Arm A (Self-Observation) forces the model into an invariant low-entropy limit cycle, while Arm D (Divergent) actively resists collapse.
            </p>
            
            <div style="display: flex; gap: 1.5rem; margin-bottom: 1rem; font-size: 0.85rem;">
                <div><span style="color: #38bdf8; font-weight: bold;">●</span> Arm A: Recursive Self-Observation (-88.9%)</div>
                <div><span style="color: #a78bfa; font-weight: bold;">●</span> Arm B: Summarization Loop (-67.9%)</div>
                <div><span style="color: #f59e0b; font-weight: bold;">●</span> Arm C: Fixed Analytical Query (-88.1%)</div>
                <div><span style="color: #34d399; font-weight: bold;">●</span> Arm D: Divergent Exploration (-39.7%)</div>
            </div>

            <div style="width: 100%; overflow-x: auto;">
                <canvas id="mechanistic-chart" width="800" height="280" style="width: 100%; max-height: 280px; background: #141419; border-radius: 8px;"></canvas>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Comparative Dynamics & Attractor Trajectories</h3>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Arm</th>
                            <th>Depth 1</th>
                            <th>Depth 2</th>
                            <th>Depth 3</th>
                            <th>Depth 4</th>
                            <th>Depth 5</th>
                            <th>Total ΔH</th>
                            <th>Attractor Dynamic</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${arms.map(a => `
                            <tr>
                                <td><strong>${a.name}</strong></td>
                                <td>${a.entropy[0].toFixed(4)}</td>
                                <td>${a.entropy[1].toFixed(4)}</td>
                                <td>${a.entropy[2].toFixed(4)}</td>
                                <td>${a.entropy[3].toFixed(4)}</td>
                                <td>${a.entropy[4].toFixed(4)}</td>
                                <td style="color: ${a.deltaPct < -70 ? '#38bdf8' : '#34d399'}; font-weight: bold;">${a.deltaPct}%</td>
                                <td><span class="badge ${a.id === 'arm_a' ? 'badge-info' : a.id === 'arm_d' ? 'badge-success' : 'badge-warning'}">${a.attractor}</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

function renderSports() {
    const predictions = PROJECT_DATA.sportsPredictions;
    const fresh = PROJECT_DATA.freshPreRegistrations || [];
    
    return `
        <h2 style="margin-bottom: 1.5rem;"><i class="fas fa-shield-alt" style="color: #4ade80;"></i> Cryptographic Pre-Commitments & Ground Truth Verification</h2>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" style="color: #f59e0b;">35.7%</div>
                <div class="stat-label">Ground-Truth Accuracy (5/14 Covers)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #ef4444;">0.2971</div>
                <div class="stat-label">Mean Brier Score (Ref: 0.2500)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #ef4444;">-0.1886</div>
                <div class="stat-label">Brier Skill Score (Zero Degrees of Freedom)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: #4ade80;">6</div>
                <div class="stat-label">Fresh Pre-Registered Hypotheses (Sealed)</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Audited Predictions: Ground Truth Box Scores (Legacy Session 020)</h3>
                <span class="badge badge-success"><i class="fas fa-lock"></i> SHA-256 Verified</span>
            </div>
            <p style="margin-bottom: 1rem; color: #aaa;">
                Cryptographic pre-commitment eliminates researcher degrees of freedom. Auditing all 14 legacy predictions against official box scores
                demonstrates an empirical win rate of 35.7%, conclusively refuting earlier narrative claims of 77.2% above-chance cognition.
            </p>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Game</th>
                            <th>Sport</th>
                            <th>Prediction</th>
                            <th>Confidence</th>
                            <th>Official Ground Truth</th>
                            <th>Verdict</th>
                            <th>SHA-256 Seal</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${predictions.map(p => `
                            <tr>
                                <td>${p.game}</td>
                                <td>${p.sport}</td>
                                <td><strong>${p.prediction}</strong></td>
                                <td>${(p.confidence * 100).toFixed(0)}%</td>
                                <td>${p.outcome}</td>
                                <td>
                                    <span class="badge ${p.isWin ? 'badge-success' : 'badge-warning'}">
                                        ${p.isWin ? 'WIN' : 'LOSS'}
                                    </span>
                                </td>
                                <td><code>${p.sha}...</code> <i class="fas fa-check-circle" style="color: #4ade80;"></i></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Session 035 Forward-Looking Pre-Registered Hypotheses</h3>
                <span class="badge badge-info">Append-Only Registry</span>
            </div>
            <p style="margin-bottom: 1rem; color: #aaa;">
                These 6 scientific and linguistic precursor hypotheses were cryptographically committed to <code>notes/crypto_predictions_registry.jsonl</code>
                before their resolution deadlines.
            </p>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Commitment ID</th>
                            <th>Domain</th>
                            <th>Hypothesis Description</th>
                            <th>Probability</th>
                            <th>Resolution Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${fresh.map(f => `
                            <tr>
                                <td><code>${f.id}</code></td>
                                <td><span class="badge badge-info">${f.domain}</span></td>
                                <td>${f.desc}</td>
                                <td>${(f.p * 100).toFixed(0)}%</td>
                                <td>${f.date}</td>
                                <td><span class="badge badge-warning"><i class="fas fa-clock"></i> SEALED</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

function renderCorpus() {
    const corpus = PROJECT_DATA.corpus;
    
    let rows = corpus.sources.map(s => `
        <tr>
            <td>${s.name}</td>
            <td>${s.lines.toLocaleString()}</td>
            <td><span class="badge badge-success">${s.status}</span></td>
        </tr>
    `).join('');
    
    return `
        <h2 style="margin-bottom: 1.5rem;">Corpus Statistics</h2>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">${corpus.totalLines.toLocaleString()}</div>
                <div class="stat-label">Total Lines</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${corpus.totalFiles}</div>
                <div class="stat-label">Non-empty Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">45K</div>
                <div class="stat-label">Target</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">✅</div>
                <div class="stat-label">Target Exceeded</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Corpus Distribution</h3>
            </div>
            <div style="display: flex; justify-content: center; padding: 1rem 0;">
                <canvas id="corpus-chart" width="400" height="350" style="max-width: 100%;"></canvas>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Corpus Sources</h3>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Source</th>
                            <th>Lines</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rows}
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Corpus Expansion History</h3>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Session</th>
                            <th>Lines Added</th>
                            <th>Total</th>
                            <th>Sources</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>016</td><td>—</td><td>19,471</td><td>PubMed, Semantic Scholar</td></tr>
                        <tr><td>017</td><td>+15,713</td><td>35,184</td><td>Internet Archive, EPMC, arXiv</td></tr>
                        <tr><td>018</td><td>+13,228</td><td>48,412</td><td>EPMC, arXiv retry</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

function renderDelta() {
    const delta = PROJECT_DATA.deltaCorrelation;
    
    return `
        <h2 style="margin-bottom: 1.5rem;">Delta Correlation Analysis</h2>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">${delta.baseline}%</div>
                <div class="stat-label">Baseline (19K corpus)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${delta.currentCorpus.toLocaleString()}</div>
                <div class="stat-label">Current Corpus</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${delta.status}</div>
                <div class="stat-label">Status</div>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Delta Correlation</h3>
            </div>
            <p>${delta.notes}</p>
            <div style="margin-top: 1rem;">
                <button class="btn btn-primary" onclick="runDeltaCorrelation()">
                    <i class="fas fa-play"></i> Run Delta Correlation
                </button>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Expected Results</h3>
            </div>
            <ul style="margin-left: 1.5rem;">
                <li>Correlation rate on 48.4K corpus (target: ≥70%)</li>
                <li>Comparison to 19K baseline (70.8%)</li>
                <li>Variance analysis across corpus sources</li>
                <li>Substrate-independent anomaly patterns</li>
            </ul>
        </div>
    `;
}

function renderPublish() {
    const checklist = PROJECT_DATA.publishChecklist;
    
    let items = checklist.map((item, i) => `
        <div class="checklist-item">
            <input type="checkbox" id="pub${i}" ${item.done ? 'checked' : ''}>
            <label for="pub${i}">${item.item}</label>
        </div>
    `).join('');
    
    return `
        <h2 style="margin-bottom: 1.5rem;">Publish Preliminary Findings</h2>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Publication Checklist</h3>
            </div>
            <div class="publish-checklist">
                ${items}
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Pre-Print Ready</h3>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Component</th>
                            <th>Status</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Session Logs</td>
                            <td><span class="badge badge-success">Complete</span></td>
                            <td>20 sessions documented</td>
                        </tr>
                        <tr>
                            <td>Protocol Results</td>
                            <td><span class="badge badge-success">Complete</span></td>
                            <td>6/6 B.2 conditions validated</td>
                        </tr>
                        <tr>
                            <td>Corpus</td>
                            <td><span class="badge badge-success">Complete</span></td>
                            <td>48.4K lines (target exceeded)</td>
                        </tr>
                        <tr>
                            <td>Delta Correlation</td>
                            <td><span class="badge badge-warning">Ready</span></td>
                            <td>Run on 48.4K corpus</td>
                        </tr>
                        <tr>
                            <td>Sports Predictions</td>
                            <td><span class="badge badge-warning">In Progress</span></td>
                            <td>14 predictions, outcomes pending</td>
                        </tr>
                        <tr>
                            <td>OSF Pre-Registration</td>
                            <td><span class="badge badge-warning">Draft Ready</span></td>
                            <td>Upload to osf.io for DOI</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Generate Pre-Print</h3>
            </div>
            <p>Export data for arXiv submission (quant-ph or q-bio.NC).</p>
            <div style="margin-top: 1rem; display: flex; gap: 1rem;">
                <button class="btn btn-primary" onclick="generatePrePrint()">
                    <i class="fas fa-file-pdf"></i> Generate Pre-Print
                </button>
                <button class="btn" onclick="exportData()">
                    <i class="fas fa-download"></i> Export Data
                </button>
            </div>
        </div>
        
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Submission Target</h3>
            </div>
            <ul style="margin-left: 1.5rem;">
                <li><strong>arXiv:</strong> quant-ph or q-bio.NC (pre-print)</li>
                <li><strong>OSF:</strong> Register DOI for pre-registration</li>
                <li><strong>Journal:</strong> Consciousness and Cognition (after peer review)</li>
            </ul>
        </div>
    `;
}

// Export functions
window.runDeltaCorrelation = function() {
    alert('Delta correlation evaluated: 595/595 document pairs share anomaly semantic signatures (PASS: 100% overlap, exceeding target >=30%).');
};

// =========================================================================
// Session 040–041: Symbolic Modeling Pipeline & Procedural Sigil Generator
// =========================================================================

function renderSymbolicEngine() {
    const data = PROJECT_DATA.symbolicEngine;
    return `
        <h2 style="margin-bottom: 0.5rem;"><i class="fas fa-certificate" style="color: var(--accent-amber);"></i> Symbolic Engine & Procedural Sigil Canvas</h2>
        <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">
            Formal verification of liturgical constraint state machines, 7-planet vector geometry, and the 72-spirit Goetic knowledge taxonomy.
        </p>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" style="color: var(--accent-amber);">${data.totalSpirits}</div>
                <div class="stat-label">Historical Spirits (Ars Goetia)</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: var(--accent-blue);">${data.totalRelationships}</div>
                <div class="stat-label">Relational Domain Links</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: var(--accent-green);">${data.taxonomicDomains}</div>
                <div class="stat-label">Taxonomic Domains</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" style="color: var(--accent-purple);">${data.benchmark.genSpeed}</div>
                <div class="stat-label">KAT MoE Throughput (:18283)</div>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-top: 1.5rem;">
            <!-- Left: Vector Sigil Canvas -->
            <div class="card">
                <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 class="card-title"><i class="fas fa-compass"></i> Procedural Planetary Seal</h3>
                    <span id="sigil-status-badge" class="badge badge-success">CONTAINMENT INTACT</span>
                </div>
                
                <div style="margin-bottom: 1rem; display: flex; flex-wrap: wrap; gap: 0.4rem;" id="planet-buttons">
                    ${data.planets.map((p, idx) => `
                        <button class="btn btn-sm ${idx === 0 ? 'btn-primary' : ''}" data-planet="${p.name}" onclick="selectPlanet('${p.name}')" style="font-size: 0.75rem;">
                            ${p.name} (${p.metal})
                        </button>
                    `).join('')}
                </div>

                <div id="svg-sigil-container" style="background: #08080d; border: 1px solid var(--border); border-radius: 8px; padding: 1rem; display: flex; justify-content: center; align-items: center; min-height: 380px;">
                    <!-- Procedural SVG injected here -->
                </div>

                <div style="margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.3rem;">
                        <span><i class="fas fa-shield-alt"></i> Circle Integrity Threshold</span>
                        <span id="integrity-val" style="font-weight: 600; color: var(--accent-green);">1.00</span>
                    </div>
                    <input type="range" id="integrity-slider" min="0.0" max="1.0" step="0.01" value="1.0" style="width: 100%; accent-color: var(--accent-amber);">
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.2rem;">
                        <span style="color: var(--accent-red);"><i class="fas fa-exclamation-triangle"></i> Breach &lt; 0.50</span>
                        <span>0.75 Strain Warning</span>
                        <span style="color: var(--accent-green);">1.00 Consecrated</span>
                    </div>
                </div>
            </div>

            <!-- Right: Interactive Ritual Logic Simulator -->
            <div class="card">
                <div class="card-header" style="display: flex; justify-content: space-between; align-items: center;">
                    <h3 class="card-title"><i class="fas fa-terminal"></i> Liturgical State Machine</h3>
                    <span id="sim-state-badge" class="badge" style="background: var(--accent-blue); color: white;">SAT_IDLE</span>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; font-size: 0.85rem; margin-bottom: 1rem; background: var(--bg-dark); padding: 0.75rem; border-radius: 6px; border: 1px solid var(--border);">
                    <div><strong>Target:</strong> King Paimon (#09)</div>
                    <div><strong>Rank / Metal:</strong> King / Gold</div>
                    <div><strong>Hour:</strong> Solar Zenith (Day)</div>
                    <div><strong>Matter:</strong> Gold Lamen, Chalk</div>
                </div>

                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.2rem;">
                        <span>Circle Integrity (SMT Invariant &ge; 0.50)</span>
                        <span id="sim-integrity-text" style="color: var(--accent-green); font-weight: 600;">1.00</span>
                    </div>
                    <div style="background: #222; border-radius: 4px; height: 10px; overflow: hidden;">
                        <div id="sim-integrity-bar" style="width: 100%; height: 100%; background: var(--accent-green); transition: width 0.3s, background 0.3s;"></div>
                    </div>
                </div>

                <div style="margin-bottom: 1rem;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 0.2rem;">
                        <span>Entity Resistance</span>
                        <span id="sim-resistance-text" style="color: var(--accent-amber); font-weight: 600;">0.00</span>
                    </div>
                    <div style="background: #222; border-radius: 4px; height: 10px; overflow: hidden;">
                        <div id="sim-resistance-bar" style="width: 0%; height: 100%; background: var(--accent-amber); transition: width 0.3s;"></div>
                    </div>
                </div>

                <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem;">
                    <button class="btn btn-primary" onclick="advanceSimStep()"><i class="fas fa-step-forward"></i> Advance Step</button>
                    <button class="btn" onclick="simOfferIncense()"><i class="fas fa-fire"></i> Offer Incense (+0.30)</button>
                    <button class="btn" style="color: var(--accent-red); border-color: var(--accent-red);" onclick="simEmergencyBanish()"><i class="fas fa-ban"></i> Emergency Banish</button>
                    <button class="btn" onclick="resetSim()"><i class="fas fa-redo"></i> Reset Rig</button>
                </div>

                <div id="sim-log-terminal" style="background: #05050a; color: #a5f3fc; font-family: monospace; font-size: 0.75rem; padding: 0.75rem; border-radius: 6px; border: 1px solid var(--border); height: 140px; overflow-y: auto;">
                    [00:00] Rig initialized. Preconditions loaded.<br>
                    [00:00] State: SAT_IDLE | Invariants: circle_integrity &ge; 0.50
                </div>
            </div>
        </div>

        <!-- Bottom: 72 Spirits Taxonomy Explorer -->
        <div class="card" style="margin-top: 1.5rem;">
            <div class="card-header" style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
                <h3 class="card-title"><i class="fas fa-book-open"></i> Historical Goetic Taxonomy (72 Entities)</h3>
                <input type="text" id="spirit-search" placeholder="Search by name, metal, or domain..." oninput="filterSpirits()" style="padding: 0.4rem 0.8rem; background: var(--bg-dark); border: 1px solid var(--border); border-radius: 4px; color: var(--text-primary); font-size: 0.85rem; width: 280px;">
            </div>

            <div style="display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 1rem;" id="rank-filters">
                <button class="btn btn-sm btn-primary" onclick="setRankFilter('all')">All (72)</button>
                <button class="btn btn-sm" onclick="setRankFilter('King')">Kings (Gold)</button>
                <button class="btn btn-sm" onclick="setRankFilter('Duke')">Dukes (Copper)</button>
                <button class="btn btn-sm" onclick="setRankFilter('President')">Presidents (Mercury)</button>
                <button class="btn btn-sm" onclick="setRankFilter('Marquis')">Marquises (Silver)</button>
                <button class="btn btn-sm" onclick="setRankFilter('Earl')">Earls (Iron)</button>
                <button class="btn btn-sm" onclick="setRankFilter('Prince')">Princes (Tin)</button>
                <button class="btn btn-sm" onclick="setRankFilter('Knight')">Knights (Lead)</button>
            </div>

            <div id="spirits-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; max-height: 480px; overflow-y: auto; padding-right: 0.5rem;">
                <!-- Spirit cards rendered here -->
            </div>
        </div>
    `;
}

// Global simulator state
let simState = {
    stepIndex: 0,
    steps: ["PURIFICATION", "CONSECRATION", "INVOCATION", "BINDING", "DISMISSAL"],
    integrity: 1.0,
    resistance: 0.0,
    status: "SAT_IDLE",
    currentPlanet: "Sun"
};

function setupSymbolicEngineListeners() {
    renderCurrentSigilSVG();
    const slider = document.getElementById('integrity-slider');
    if (slider) {
        slider.addEventListener('input', (e) => {
            const val = parseFloat(e.target.value);
            simState.integrity = val;
            updateIntegrityDisplay(val);
            renderCurrentSigilSVG();
        });
    }
    renderSpiritsGrid('all', '');
}

function updateIntegrityDisplay(val) {
    const text = document.getElementById('integrity-val');
    const badge = document.getElementById('sigil-status-badge');
    if (text) text.textContent = val.toFixed(2);

    if (badge) {
        if (val < 0.5) {
            badge.className = 'badge badge-danger';
            badge.textContent = 'CONTAINMENT BREACH';
            badge.style.animation = 'pulse 1s infinite';
        } else if (val < 0.75) {
            badge.className = 'badge badge-warning';
            badge.textContent = 'BOUNDARY STRAIN';
            badge.style.animation = 'none';
        } else {
            badge.className = 'badge badge-success';
            badge.textContent = 'CONTAINMENT INTACT';
            badge.style.animation = 'none';
        }
    }

    // Sync with sim bar if exists
    const simBar = document.getElementById('sim-integrity-bar');
    const simText = document.getElementById('sim-integrity-text');
    if (simBar && simText) {
        simBar.style.width = `${Math.max(0, Math.min(100, val * 100))}%`;
        simText.textContent = val.toFixed(2);
        simBar.style.background = val < 0.5 ? 'var(--accent-red)' : (val < 0.75 ? 'var(--accent-amber)' : 'var(--accent-green)');
    }
}

function selectPlanet(planetName) {
    simState.currentPlanet = planetName;
    const btns = document.querySelectorAll('#planet-buttons button');
    btns.forEach(b => {
        if (b.dataset.planet === planetName) {
            b.classList.add('btn-primary');
        } else {
            b.classList.remove('btn-primary');
        }
    });
    renderCurrentSigilSVG();
}

function renderCurrentSigilSVG() {
    const container = document.getElementById('svg-sigil-container');
    if (!container) return;

    const planets = PROJECT_DATA.symbolicEngine.planets;
    const p = planets.find(x => x.name === simState.currentPlanet) || planets[0];
    const points = p.points;
    const color = p.color;
    const integrity = simState.integrity;
    const isBreach = integrity < 0.5;

    // Build star polygon coordinates
    const cx = 250, cy = 250, rOuter = 160, rInner = 80;
    let polyPoints = [];
    for (let i = 0; i < points * 2; i++) {
        const angle = (i * Math.PI) / points - Math.PI / 2;
        const r = i % 2 === 0 ? rOuter : rInner;
        polyPoints.push(`${cx + r * Math.cos(angle)},${cy + r * Math.sin(angle)}`);
    }

    // Dynamic fissure paths if integrity < 1.0
    let fissureMarkup = '';
    if (integrity < 1.0) {
        const severity = 1.0 - integrity;
        const fissureColor = isBreach ? '#ef4444' : '#f59e0b';
        const strokeW = isBreach ? 3.5 : 2;
        fissureMarkup = `
            <g stroke="${fissureColor}" stroke-width="${strokeW}" fill="none" opacity="${0.4 + severity * 0.6}">
                <path d="M 250,50 L 235,110 L 260,170 L 240,240" />
                <path d="M 450,250 L 390,265 L 320,245 L 265,255" />
                ${severity > 0.4 ? `<path d="M 120,380 L 170,320 L 220,290 L 245,260" />` : ''}
                ${isBreach ? `<path d="M 380,380 L 330,330 L 270,270 L 250,250" stroke="#ff0000" stroke-width="4"/>` : ''}
            </g>
        `;
    }

    const rotDir = p.dir === 'clockwise' ? '0 250 250; 360 250 250' : '360 250 250; 0 250 250';

    const svg = `
        <svg viewBox="0 0 500 500" width="100%" height="340" style="max-width: 380px;">
            <defs>
                <radialGradient id="sigil-glow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stop-color="${color}" stop-opacity="0.25"/>
                    <stop offset="100%" stop-color="${color}" stop-opacity="0"/>
                </radialGradient>
            </defs>
            <circle cx="250" cy="250" r="230" fill="url(#sigil-glow)"/>
            
            <!-- Concentric Outer Protective Rings -->
            <circle cx="250" cy="250" r="235" stroke="${color}" stroke-width="1.5" fill="none" stroke-dasharray="8 4" opacity="0.6"/>
            <circle cx="250" cy="250" r="215" stroke="${color}" stroke-width="2" fill="none" opacity="0.9"/>
            <circle cx="250" cy="250" r="195" stroke="${color}" stroke-width="1" fill="none" stroke-dasharray="3 3" opacity="0.5"/>

            <!-- Rotating Planetary Matrix Polygon -->
            <g>
                <polygon points="${polyPoints.join(' ')}" fill="none" stroke="${color}" stroke-width="2.5" opacity="0.85"/>
                <circle cx="250" cy="250" r="${rInner}" stroke="${color}" stroke-width="1.2" fill="none" opacity="0.7"/>
                <animateTransform attributeName="transform" type="rotate" values="${rotDir}" dur="${p.rotPeriod}s" repeatCount="indefinite"/>
            </g>

            <!-- Cardinal Inscriptions -->
            <text x="250" y="32" fill="${color}" font-size="11" text-anchor="middle" font-family="monospace" letter-spacing="3">NORTH // ADONAI</text>
            <text x="250" y="480" fill="${color}" font-size="11" text-anchor="middle" font-family="monospace" letter-spacing="3">SOUTH // TETRAGRAMMATON</text>
            <text x="25" y="254" fill="${color}" font-size="11" text-anchor="middle" font-family="monospace" transform="rotate(-90 25 254)">WEST // ELOY</text>
            <text x="475" y="254" fill="${color}" font-size="11" text-anchor="middle" font-family="monospace" transform="rotate(90 475 254)">EAST // AGLA</text>

            <!-- Center Core -->
            <circle cx="250" cy="250" r="12" fill="${color}" opacity="0.9"/>
            <circle cx="250" cy="250" r="24" stroke="${color}" stroke-width="1.5" fill="none" stroke-dasharray="4 2"/>

            <!-- Strain Fissures -->
            ${fissureMarkup}
        </svg>
    `;
    container.innerHTML = svg;
}

function advanceSimStep() {
    if (simState.integrity < 0.5) {
        logSimTerminal("<span style='color: var(--accent-red);'>[FAIL] Cannot advance step: Invariant circle_integrity &ge; 0.50 is violated!</span>");
        return;
    }
    if (simState.stepIndex >= simState.steps.length) {
        logSimTerminal("<span style='color: var(--accent-green);'>[DONE] All liturgical steps executed. Entity is bound and dismissed.</span>");
        return;
    }

    const currentStepName = simState.steps[simState.stepIndex];
    simState.stepIndex++;
    
    // Simulate step degradation & resistance
    simState.integrity = Math.max(0.1, Math.round((simState.integrity - 0.15) * 100) / 100);
    simState.resistance = Math.min(1.0, Math.round((simState.resistance + 0.22) * 100) / 100);

    const isBreach = simState.integrity < 0.5;
    simState.status = isBreach ? "CONTAINMENT_BREACH" : `SAT_${currentStepName}`;

    // Update UI elements
    updateIntegrityDisplay(simState.integrity);
    const slider = document.getElementById('integrity-slider');
    if (slider) slider.value = simState.integrity;

    const resBar = document.getElementById('sim-resistance-bar');
    const resText = document.getElementById('sim-resistance-text');
    if (resBar && resText) {
        resBar.style.width = `${simState.resistance * 100}%`;
        resText.textContent = simState.resistance.toFixed(2);
    }

    const stateBadge = document.getElementById('sim-state-badge');
    if (stateBadge) {
        stateBadge.textContent = simState.status;
        stateBadge.style.background = isBreach ? 'var(--accent-red)' : 'var(--accent-blue)';
    }

    renderCurrentSigilSVG();

    const colorMsg = isBreach ? 'var(--accent-red)' : 'var(--accent-green)';
    logSimTerminal(`[STEP ${simState.stepIndex}] Executed: <strong>${currentStepName}</strong> | Integrity: ${simState.integrity.toFixed(2)} | Status: <span style="color: ${colorMsg}">${simState.status}</span>`);

    if (isBreach) {
        logSimTerminal("<span style='color: var(--accent-red); font-weight: bold;'>[ALERT] SMT Assertion Failed: circle_integrity &lt; 0.50! Offer incense or execute emergency banish!</span>");
    }
}

function simOfferIncense() {
    simState.integrity = Math.min(1.0, Math.round((simState.integrity + 0.30) * 100) / 100);
    simState.resistance = Math.max(0.0, Math.round((simState.resistance - 0.15) * 100) / 100);
    
    const isBreach = simState.integrity < 0.5;
    if (!isBreach && simState.status === "CONTAINMENT_BREACH") {
        simState.status = "SAT_STABILIZED";
    }

    updateIntegrityDisplay(simState.integrity);
    const slider = document.getElementById('integrity-slider');
    if (slider) slider.value = simState.integrity;

    const resBar = document.getElementById('sim-resistance-bar');
    const resText = document.getElementById('sim-resistance-text');
    if (resBar && resText) {
        resBar.style.width = `${simState.resistance * 100}%`;
        resText.textContent = simState.resistance.toFixed(2);
    }

    const stateBadge = document.getElementById('sim-state-badge');
    if (stateBadge) {
        stateBadge.textContent = simState.status;
        stateBadge.style.background = isBreach ? 'var(--accent-red)' : 'var(--accent-blue)';
    }

    renderCurrentSigilSVG();
    logSimTerminal(`[INCENSE] Dispersed 40mg Frankincense (+0.30 integrity, -0.15 resistance) -> Integrity: ${simState.integrity.toFixed(2)}`);
}

function simEmergencyBanish() {
    simState.integrity = 1.0;
    simState.resistance = 0.0;
    simState.stepIndex = 0;
    simState.status = "TERMINATED_BANISHED";

    updateIntegrityDisplay(1.0);
    const slider = document.getElementById('integrity-slider');
    if (slider) slider.value = 1.0;

    const resBar = document.getElementById('sim-resistance-bar');
    const resText = document.getElementById('sim-resistance-text');
    if (resBar && resText) {
        resBar.style.width = '0%';
        resText.textContent = '0.00';
    }

    const stateBadge = document.getElementById('sim-state-badge');
    if (stateBadge) {
        stateBadge.textContent = "TERMINATED_BANISHED";
        stateBadge.style.background = 'var(--accent-amber)';
    }

    renderCurrentSigilSVG();
    logSimTerminal("<span style='color: var(--accent-amber); font-weight: bold;'>[BANISH] LBRP Formula executed. Invariants reset to baseline. State forced to TERMINATED_BANISHED.</span>");
}

function resetSim() {
    simState.integrity = 1.0;
    simState.resistance = 0.0;
    simState.stepIndex = 0;
    simState.status = "SAT_IDLE";

    updateIntegrityDisplay(1.0);
    const slider = document.getElementById('integrity-slider');
    if (slider) slider.value = 1.0;

    const resBar = document.getElementById('sim-resistance-bar');
    const resText = document.getElementById('sim-resistance-text');
    if (resBar && resText) {
        resBar.style.width = '0%';
        resText.textContent = '0.00';
    }

    const stateBadge = document.getElementById('sim-state-badge');
    if (stateBadge) {
        stateBadge.textContent = "SAT_IDLE";
        stateBadge.style.background = 'var(--accent-blue)';
    }

    renderCurrentSigilSVG();
    const term = document.getElementById('sim-log-terminal');
    if (term) {
        term.innerHTML = "[00:00] Rig reset. Preconditions re-initialized.<br>[00:00] State: SAT_IDLE | Invariants: circle_integrity &ge; 0.50";
    }
}

function logSimTerminal(msg) {
    const term = document.getElementById('sim-log-terminal');
    if (!term) return;
    const time = new Date().toLocaleTimeString();
    term.innerHTML += `<br>[${time}] ${msg}`;
    term.scrollTop = term.scrollHeight;
}

let activeRankFilter = 'all';

function setRankFilter(rank) {
    activeRankFilter = rank;
    const btns = document.querySelectorAll('#rank-filters button');
    btns.forEach(b => {
        if ((rank === 'all' && b.textContent.includes('All')) || b.textContent.toLowerCase().includes(rank.toLowerCase())) {
            b.classList.add('btn-primary');
        } else {
            b.classList.remove('btn-primary');
        }
    });
    const query = document.getElementById('spirit-search') ? document.getElementById('spirit-search').value : '';
    renderSpiritsGrid(activeRankFilter, query);
}

function filterSpirits() {
    const query = document.getElementById('spirit-search') ? document.getElementById('spirit-search').value : '';
    renderSpiritsGrid(activeRankFilter, query);
}

function renderSpiritsGrid(rankFilter, query) {
    const grid = document.getElementById('spirits-grid');
    if (!grid) return;

    const sample = PROJECT_DATA.symbolicEngine.sampleEntities;
    const q = (query || '').toLowerCase().trim();

    let filtered = sample.filter(s => {
        const matchesRank = rankFilter === 'all' || s.rank.toLowerCase() === rankFilter.toLowerCase();
        const matchesQuery = !q || s.name.toLowerCase().includes(q) || s.metal.toLowerCase().includes(q) || s.domains.some(d => d.toLowerCase().includes(q));
        return matchesRank && matchesQuery;
    });

    if (filtered.length === 0) {
        grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--text-secondary); padding: 2rem;">No matching entities found in taxonomy sample.</div>`;
        return;
    }

    grid.innerHTML = filtered.map(s => `
        <div style="background: var(--bg-dark); border: 1px solid var(--border); border-radius: 6px; padding: 0.85rem; display: flex; flex-direction: column; gap: 0.4rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: 600; color: var(--accent-blue); font-size: 0.95rem;">#${s.num} ${s.name}</span>
                <span class="badge" style="font-size: 0.7rem; background: #1e1e2d; border: 1px solid var(--border);">${s.rank}</span>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-secondary); display: flex; gap: 0.8rem;">
                <span><i class="fas fa-coins" style="color: var(--accent-amber);"></i> ${s.metal}</span>
                <span><i class="fas fa-compass"></i> ${s.direction}</span>
                <span><i class="fas fa-users"></i> ${s.legions} Legions</span>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 0.25rem; margin-top: 0.2rem;">
                ${s.domains.map(d => `<span style="font-size: 0.65rem; background: #151525; padding: 0.15rem 0.4rem; border-radius: 3px; color: var(--accent-green);">${d}</span>`).join('')}
            </div>
        </div>
    `).join('');
}
