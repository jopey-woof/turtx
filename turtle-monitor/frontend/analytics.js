// analytics.js - Turtle Analytics Dashboard Logic
document.addEventListener('DOMContentLoaded', () => {
    // Chart configurations
    const tempTrendChart = new Chart(document.getElementById('temperatureTrend'), {
        type: 'line',
        data: { datasets: [] },
        options: { responsive: true, scales: { x: { type: 'time' } } }
    });

    const humidityTrendChart = new Chart(document.getElementById('humidityTrend'), {
        type: 'line',
        data: { datasets: [] },
        options: { responsive: true, scales: { x: { type: 'time' } } }
    });

    const tempDistributionChart = new Chart(document.getElementById('tempDistribution'), {
        type: 'bar',
        data: { datasets: [] },
        options: { responsive: true }
    });

    const dailyPatternsChart = new Chart(document.getElementById('dailyPatterns'), {
        type: 'line',
        data: { datasets: [] },
        options: { responsive: true }
    });

    // Load initial data
    loadData('24h');

    // Event listeners for time period buttons
    document.querySelectorAll('.time-controls button').forEach(button => {
        button.addEventListener('click', () => loadData(button.dataset.period));
    });
});

async function loadData(period) {
    const zones = ['sensor1', 'sensor2'];
    const metrics = ['temperature', 'humidity'];

    const data = {};
    for (const zone of zones) {
        data[zone] = {};
        for (const metric of metrics) {
            data[zone][metric] = await fetchData(metric, zone, period);
        }
    }

    updateCharts(data, period);
    updateKPIs(data, period);
}

async function fetchData(metric, zone, period) {
    const response = await fetch(`/api/analytics/${metric}/${zone}?period=${period}`);
    if (!response.ok) throw new Error('Failed to fetch data');
    return await response.json();
}

function updateCharts(data, period) {
    // Update temperature trend
    tempTrendChart.data.datasets = [
        { label: 'Basking Temp', data: data.sensor1.temperature.data, borderColor: 'red' },
        { label: 'Cooling Temp', data: data.sensor2.temperature.data, borderColor: 'blue' }
    ];
    tempTrendChart.update();

    // Update humidity trend
    humidityTrendChart.data.datasets = [
        { label: 'Basking Humidity', data: data.sensor1.humidity.data, borderColor: 'green' },
        { label: 'Cooling Humidity', data: data.sensor2.humidity.data, borderColor: 'purple' }
    ];
    humidityTrendChart.update();

    // Update other charts similarly (distribution, patterns)
}

function updateKPIs(data, period) {
    document.getElementById('avg-basking-temp').textContent = calculateAverage(data.sensor1.temperature.data);
    document.getElementById('avg-cooling-temp').textContent = calculateAverage(data.sensor2.temperature.data);
    document.getElementById('avg-basking-humidity').textContent = calculateAverage(data.sensor1.humidity.data);
    document.getElementById('avg-cooling-humidity').textContent = calculateAverage(data.sensor2.humidity.data);
    document.getElementById('optimal-conditions').textContent = calculateOptimalPercentage(data);
    document.getElementById('alert-count').textContent = calculateAlertCount(data);
}

function calculateAverage(data) {
    const sum = data.reduce((acc, val) => acc + val.value, 0);
    return (sum / data.length).toFixed(2);
}

function calculateOptimalPercentage(data) {
    // Implement logic for optimal conditions percentage
    return '85%'; // Placeholder
}

function calculateAlertCount(data) {
    // Implement logic for alert count
    return '2'; // Placeholder
}