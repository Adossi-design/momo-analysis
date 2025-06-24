let transactions = [];

function fetchAllTransactions() {
    fetch('http://localhost:5000/api/transactions')
        .then(res => res.json())
        .then(data => {
            transactions = data;
            populateTable(data);
        });
}

function handleSearch(query) {
    fetch(http://localhost:5000/api/search?query=${encodeURIComponent(query)})
        .then(res => res.json())
        .then(data => {
            document.getElementById('noResultMsg').classList.toggle('hidden', data.length > 0);
            populateTable(data);
        });
}

function filterData() {
    const value = document.getElementById('searchBox').value;
    handleSearch(value);
}

function populateTable(data) {
    const tbody = document.querySelector('#transactionTable tbody');
    tbody.innerHTML = '';
    data.forEach(txn => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${txn.type}</td>
            <td>${txn.amount}</td>
            <td>${txn.party}</td>
            <td>${txn.tx_id || 'N/A'}</td>
            <td>${txn.date || 'N/A'}</td>
        `;
        tbody.appendChild(tr);
    });
}

function drawCharts() {
    fetch('http://localhost:5000/api/summary')
        .then(res => res.json())
        .then(summary => {
            const typeData = summary.type_summary;
            const monthData = summary.monthly_summary;

            new Chart(document.getElementById('typeChart'), {
                type: 'bar',
                data: {
                    labels: Object.keys(typeData),
                    datasets: [{
                        label: 'Total Amount by Type',
                        data: Object.values(typeData),
                        backgroundColor: 'green'
                    }]
                }
            });

            new Chart(document.getElementById('monthlyChart'), {
                type: 'line',
                data: {
                    labels: Object.keys(monthData),
                    datasets: [{
                        label: 'Monthly Summary',
                        data: Object.values(monthData),
                        borderColor: 'green',
                        fill: false
                    }]
                }
            });
        });
}

window.onload = function () {
    fetchAllTransactions();
    drawCharts();
};
