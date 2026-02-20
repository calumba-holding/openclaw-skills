// Visualization Skill Core Logic (Browser-based Rendering)
// Uses OpenClaw's canvas tool for client-side chart generation

async function generateVisualization(context) {
  const { prompt } = context;
  
  // Parse user request into structured parameters
  const params = parseRequest(prompt);
  
  // Generate Chart.js configuration
  let chartConfig;
  switch(params.template) {
    case 'stock':
      chartConfig = generateStockChartConfig(params);
      break;
    case 'portfolio':
      chartConfig = generatePortfolioChartConfig(params);
      break;
    case 'industry':
      chartConfig = generateIndustryChartConfig(params);
      break;
    default:
      throw new Error('Unsupported visualization template');
  }
  
  // Render via OpenClaw's browser-based canvas
  const result = await renderChartInBrowser(chartConfig, params.template);
  return result;
}

// Stock Technical Analysis Config
function generateStockChartConfig(params) {
  const { symbol, indicators = ['price', 'ma50', 'rsi', 'volume'] } = params;
  
  // Mock data (in real implementation, would fetch from API)
  const dates = Array.from({length: 30}, (_, i) => 
    new Date(Date.now() - i*86400000).toISOString().split('T')[0]
  );
  
  const priceData = Array.from({length: 30}, () => 
    150 + Math.random()*20
  );
  
  const ma50Data = Array.from({length: 30}, () => 
    160 + Math.random()*5
  );
  
  const rsiData = Array.from({length: 30}, () => 
    30 + Math.random()*40
  );
  
  const volumeData = Array.from({length: 30}, () => 
    1000000 + Math.random()*500000
  );
  
  return {
    type: 'line',
    data: {
      labels: dates,
      datasets: [
        {
          label: `${symbol} Price`,
          data: priceData,
          borderColor: '#4BC0C0',
          tension: 0.1
        },
        ...(indicators.includes('ma50') ? [{
          label: '50-Day MA',
          data: ma50Data,
          borderColor: '#FF6384',
          borderDash: [5, 5]
        }] : []),
        ...(indicators.includes('rsi') ? [{
          label: 'RSI',
          data: rsiData,
          borderColor: '#FFCE56',
          yAxisID: 'y1'
        }] : []),
        ...(indicators.includes('volume') ? [{
          label: 'Volume',
          data: volumeData,
          type: 'bar',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          yAxisID: 'y2'
        }] : [])
      ]
    },
    options: {
      responsive: true,
      interaction: {
        mode: 'index',
        intersect: false
      },
      scales: {
        y: {
          type: 'linear',
          display: true,
          position: 'left',
        },
        ...(indicators.includes('rsi') ? {
          y1: {
            type: 'linear',
            display: true,
            position: 'right',
            grid: {
              drawOnChartArea: false,
            },
          }
        } : {}),
        ...(indicators.includes('volume') ? {
          y2: {
            type: 'linear',
            display: true,
            position: 'right',
            grid: {
              drawOnChartArea: false,
            },
          }
        } : {})
      }
    }
  };
}

// Portfolio Dashboard Config
function generatePortfolioChartConfig(params) {
  const { assets, riskMetrics } = params;
  
  // Asset allocation pie chart
  const pieConfig = {
    type: 'pie',
    data: {
      labels: Object.keys(assets),
      datasets: [{
        data: Object.values(assets),
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']
      }]
    }
  };
  
  // Performance line chart
  const performanceConfig = {
    type: 'line',
    data: {
      labels: Array.from({length: 90}, (_, i) => 
        new Date(Date.now() - i*86400000).toISOString().split('T')[0]
      ),
      datasets: [{
        label: 'Portfolio Value',
        data: Array.from({length: 90}, (_, i) => 
          100 + Math.random()*20 - i*0.1
        ),
        borderColor: '#FF6384',
        fill: true
      }]
    }
  };
  
  return {
    composite: true,
    charts: [pieConfig, performanceConfig],
    metadata: { riskMetrics }
  };
}

// Industry Comparison Config
function generateIndustryChartConfig(params) {
  const { sectors, metrics } = params;
  
  // Bar chart for returns/volatility
  const barConfig = {
    type: 'bar',
    data: {
      labels: sectors,
      datasets: [
        {
          label: 'Annual Return (%)',
          data: metrics.returns || sectors.map(() => 10 + Math.random()*15),
          backgroundColor: 'rgba(54, 162, 235, 0.6)'
        },
        {
          label: 'Volatility (%)',
          data: metrics.volatility || sectors.map(() => 15 + Math.random()*10),
          backgroundColor: 'rgba(255, 99, 132, 0.6)'
        }
      ]
    }
  };
  
  // Scatter plot for risk-return
  const scatterData = sectors.map((sector, i) => ({
    x: metrics.volatility?.[i] || 15 + Math.random()*10,
    y: metrics.returns?.[i] || 10 + Math.random()*15,
    label: sector
  }));
  
  const scatterConfig = {
    type: 'scatter',
    data: {
      datasets: [{
        label: 'Sectors',
        data: scatterData,
        backgroundColor: 'rgba(75, 192, 192, 0.6)'
      }]
    },
    options: {
      scales: {
        x: {
          title: { display: true, text: 'Volatility (%)' }
        },
        y: {
          title: { display: true, text: 'Return (%)' }
        }
      }
    }
  };
  
  return {
    composite: true,
    charts: [barConfig, scatterConfig]
  };
}

// Browser-based rendering using OpenClaw's canvas tool
async function renderChartInBrowser(chartConfig, template) {
  // Generate HTML page with Chart.js
  const htmlContent = `
<!DOCTYPE html>
<html>
<head>
  <title>Visualization</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { margin: 0; padding: 20px; background: white; }
    .chart-container { width: 1200px; height: 800px; margin: 0 auto; }
    .composite { display: flex; flex-wrap: wrap; justify-content: center; }
    .composite > div { margin: 10px; }
  </style>
</head>
<body>
  ${chartConfig.composite 
    ? `<div class="composite">
        ${chartConfig.charts.map((_, i) => 
          `<div class="chart-container" id="chart${i}"></div>`
        ).join('')}
       </div>`
    : '<div class="chart-container"><canvas id="chart"></canvas></div>'
  }
  <script>
    ${chartConfig.composite 
      ? chartConfig.charts.map((config, i) => 
          `new Chart(document.getElementById('chart${i}'), ${JSON.stringify(config)});`
        ).join('\n')
      : `new Chart(document.getElementById('chart'), ${JSON.stringify(chartConfig)});`
    }
    
    // Add risk metrics if available
    ${chartConfig.metadata?.riskMetrics 
      ? `
        const metrics = ${JSON.stringify(chartConfig.metadata.riskMetrics)};
        const info = document.createElement('div');
        info.innerHTML = \`
          <h3>Risk Metrics</h3>
          <p>Volatility: \${metrics.volatility}%</p>
          <p>Max Drawdown: \${metrics.drawdown}%</p>
          <p>Sharpe Ratio: \${metrics.sharpe}</p>
        \`;
        document.body.appendChild(info);
        `
      : ''
    }
  </script>
</body>
</html>`;

  // Save HTML to workspace
  const fs = require('fs');
  const outputPath = `/home/admin/.openclaw/workspace/visualization_${template}_${Date.now()}.html`;
  fs.writeFileSync(outputPath, htmlContent);
  
  // Use OpenClaw's canvas tool to render and capture
  const { canvas } = require('openclaw-tools');
  const snapshot = await canvas.present({
    url: `file://${outputPath}`,
    width: 1600,
    height: 1200,
    delayMs: 2000
  });
  
  return { 
    path: snapshot.path, 
    type: 'image/png',
    htmlPath: outputPath
  };
}

// Helper functions
function parseRequest(prompt) {
  // Extract parameters from natural language prompt
  const template = 
    prompt.includes('股票') || prompt.includes('stock') ? 'stock' :
    prompt.includes('投资组合') || prompt.includes('portfolio') ? 'portfolio' :
    prompt.includes('行业') || prompt.includes('industry') ? 'industry' :
    'stock';
  
  return {
    template,
    symbol: extractSymbol(prompt) || 'AAPL',
    indicators: ['price', 'ma50', 'rsi', 'volume'],
    assets: { 
      '科技股': 60, 
      '金融股': 25, 
      '能源股': 15 
    },
    riskMetrics: {
      volatility: 15,
      drawdown: -8,
      sharpe: 1.2
    },
    sectors: ['科技', '金融', '能源'],
    metrics: {}
  };
}

function extractSymbol(prompt) {
  const match = prompt.match(/([A-Z]{2,5})/);
  return match ? match[1] : null;
}

module.exports = { generateVisualization };