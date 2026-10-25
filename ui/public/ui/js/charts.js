// Will Breaker Dashboard Charts (Canvas-based, no external dependencies)

function drawBasinChart(canvasId, basins) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    ctx.clearRect(0, 0, width, height);
    
    const barWidth = (width - 100) / basins.length;
    const maxPhi = Math.max(...basins.map(b => b.phi));
    
    basins.forEach((b, i) => {
        const barHeight = (b.phi / maxPhi) * (height - 60);
        const x = 50 + i * barWidth;
        const y = height - 30 - barHeight;
        
        // Draw bar
        const gradient = ctx.createLinearGradient(x, y, x, height - 30);
        gradient.addColorStop(0, '#4f8ef7');
        gradient.addColorStop(1, '#a78bfa');
        
        ctx.fillStyle = gradient;
        ctx.fillRect(x + 5, y, barWidth - 10, barHeight);
        
        // Draw label
        ctx.fillStyle = '#888';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`Depth ${b.depth}`, x + barWidth/2, height - 10);
        
        // Draw phi value
        ctx.fillStyle = '#e0e0e0';
        ctx.fillText(`φ=${b.phi}`, x + barWidth/2, y - 5);
    });
}

function drawCorpusChart(canvasId, sources) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    ctx.clearRect(0, 0, width, height);
    
    const total = sources.reduce((sum, s) => sum + s.lines, 0);
    let angle = -Math.PI / 2;
    const radius = Math.min(width, height) / 2 - 40;
    const centerX = width / 2;
    const centerY = height / 2;
    
    const colors = ['#4f8ef7', '#4ade80', '#f59e0b', '#ef4444', '#a78bfa', '#888'];
    
    sources.forEach((s, i) => {
        const sliceAngle = (s.lines / total) * 2 * Math.PI;
        
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, angle, angle + sliceAngle);
        ctx.closePath();
        ctx.fillStyle = colors[i % colors.length];
        ctx.fill();
        
        // Label
        const midAngle = angle + sliceAngle / 2;
        const labelX = centerX + (radius * 0.7) * Math.cos(midAngle);
        const labelY = centerY + (radius * 0.7) * Math.sin(midAngle);
        
        ctx.fillStyle = '#fff';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(s.name.split(' ')[0], labelX, labelY);
        
        angle += sliceAngle;
    });
}

// Initialize charts when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Basin chart
    const basinCanvas = document.getElementById('basin-chart');
    if (basinCanvas && typeof PROJECT_DATA !== 'undefined') {
        drawBasinChart('basin-chart', PROJECT_DATA.basins);
    }
    
    // Corpus chart
    const corpusCanvas = document.getElementById('corpus-chart');
    if (corpusCanvas && typeof PROJECT_DATA !== 'undefined') {
        drawCorpusChart('corpus-chart', PROJECT_DATA.corpus.sources);
    }
});

function drawMechanisticChart(canvasId, arms) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !arms) return;
    
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    ctx.clearRect(0, 0, width, height);
    
    const paddingLeft = 50;
    const paddingRight = 30;
    const paddingTop = 40;
    const paddingBottom = 40;
    
    const plotWidth = width - paddingLeft - paddingRight;
    const plotHeight = height - paddingTop - paddingBottom;
    
    // Axes & grid lines
    ctx.strokeStyle = '#333';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(paddingLeft, paddingTop);
    ctx.lineTo(paddingLeft, height - paddingBottom);
    ctx.lineTo(width - paddingRight, height - paddingBottom);
    ctx.stroke();
    
    const maxH = 1.4;
    const minH = 0.0;
    
    // Y-axis ticks
    ctx.fillStyle = '#888';
    ctx.font = '11px sans-serif';
    ctx.textAlign = 'right';
    for (let h = 0.0; h <= maxH; h += 0.35) {
        const y = height - paddingBottom - (h / maxH) * plotHeight;
        ctx.fillText(h.toFixed(2), paddingLeft - 8, y + 4);
        ctx.strokeStyle = '#262626';
        ctx.beginPath();
        ctx.moveTo(paddingLeft, y);
        ctx.lineTo(width - paddingRight, y);
        ctx.stroke();
    }
    
    // X-axis ticks (Depths 1 to 5)
    ctx.textAlign = 'center';
    const depths = [1, 2, 3, 4, 5];
    const xPositions = depths.map((d, i) => paddingLeft + (i / (depths.length - 1)) * plotWidth);
    depths.forEach((d, i) => {
        ctx.fillText(`Depth ${d}`, xPositions[i], height - paddingBottom + 20);
    });
    
    const armColors = {
        'arm_a': '#38bdf8', // Cyan
        'arm_b': '#a78bfa', // Purple
        'arm_c': '#f59e0b', // Amber
        'arm_d': '#34d399'  // Emerald
    };
    
    // Plot lines
    arms.forEach(arm => {
        const color = armColors[arm.id] || '#fff';
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.beginPath();
        
        arm.entropy.forEach((val, i) => {
            const x = xPositions[i];
            const y = height - paddingBottom - (val / maxH) * plotHeight;
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        });
        ctx.stroke();
        
        // Data points
        arm.entropy.forEach((val, i) => {
            const x = xPositions[i];
            const y = height - paddingBottom - (val / maxH) * plotHeight;
            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(x, y, 4, 0, Math.PI * 2);
            ctx.fill();
        });
    });
}

// Export to window
window.drawBasinChart = drawBasinChart;
window.drawCorpusChart = drawCorpusChart;
window.drawMechanisticChart = drawMechanisticChart;
