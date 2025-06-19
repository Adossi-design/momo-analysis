document.addEventListener('DOMContentLoaded', function() {
    // Monthly Volume Chart
    const monthlyCtx = document.getElementById('monthlyChart').getContext('2d');
    new Chart(monthlyCtx, {
        type: 'bar',
        data: {
            labels: {{ monthly_stats|map(attribute='month')|tojson }},
            datasets: [{
                label: 'Transaction Volume (RWF)',
                data: {{ monthly_stats|map(attribute='total')|tojson }},
                backgroundColor: '#4CAF50',
                borderColor: '#2E7D32',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString() + ' RWF';
                        }
                    }
                }
            }
        }
    });

    // Type Distribution Chart
    const typeCtx = document.getElementById('typeChart').getContext('2d');
    new Chart(typeCtx, {
        type: 'pie',
        data: {
            labels: {{ type_stats|map(attribute='type_name')|tojson }},
            datasets: [{
                data: {{ type_stats|map(attribute='total')|tojson }},
                backgroundColor: [
                    '#4CAF50', '#2196F3', '#FFC107', 
                    '#FF5722', '#9C27B0', '#607D8B'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + 
                                context.raw.toLocaleString() + ' RWF';
                        }
                    }
                }
            }
        }
    });
});
