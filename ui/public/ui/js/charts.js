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

// Export to window
window.drawBasinChart = drawBasinChart;
window.drawCorpusChart = drawCorpusChart;
