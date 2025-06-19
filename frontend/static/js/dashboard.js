// Initialize monthly chart
const ctx = document.getElementById('monthlyChart').getContext('2d');
let monthlyChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Transaction Volume (RWF)',
            data: [],
            backgroundColor: '#ff6d00',
            borderColor: '#e65100',
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

// Fetch and update data
function refreshData() {
    document.getElementById('update-time').textContent = new Date().toLocaleString();
    
    // Fetch stats
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update current month total
                const currentMonth = new Date().toISOString().slice(0, 7);
                const monthData = data.data.monthly.find(m => m.month === currentMonth);
                if (monthData) {
                    document.getElementById('current-month-total').textContent = 
                        monthData.total.toLocaleString();
                }

                // Update chart
                monthlyChart.data.labels = data.data.monthly.map(m => m.month);
                monthlyChart.data.datasets[0].data = data.data.monthly.map(m => m.total);
                monthlyChart.update();
            }
        });

    // Fetch recent transactions (AJAX)
    fetch('/api/transactions?limit=10')
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const tableBody = document.querySelector('table tbody');
                // Clear existing rows (except server-rendered ones)
                const serverRows = document.querySelectorAll('table tbody tr[data-server]');
                Array.from(tableBody.children)
                    .filter(row => !row.hasAttribute('data-server'))
                    .forEach(row => row.remove());
                
                // Add new rows
                data.data.forEach(tx => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${new Date(tx.transaction_date).toLocaleDateString()}</td>
                        <td class="${tx.transaction_type}">${tx.transaction_type}</td>
                        <td>${parseFloat(tx.amount).toLocaleString()}</td>
                        <td>${tx.sender || tx.recipient || tx.message_body?.substring(0, 30) || ''}</td>
                    `;
                    tableBody.appendChild(row);
                });
            }
        });
}

// Initial load
document.addEventListener('DOMContentLoaded', refreshData);

// Refresh every 60 seconds
setInterval(refreshData, 60000);
