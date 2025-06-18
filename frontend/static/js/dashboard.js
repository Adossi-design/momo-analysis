// Global variables
let currentPage = 1;
const transactionsPerPage = 10;
let allTransactions = [];
let filteredTransactions = [];

// DOM Elements
const typeFilter = document.getElementById('typeFilter');
const startDate = document.getElementById('startDate');
const endDate = document.getElementById('endDate');
const minAmount = document.getElementById('minAmount');
const maxAmount = document.getElementById('maxAmount');
const applyFiltersBtn = document.getElementById('applyFilters');
const resetFiltersBtn = document.getElementById('resetFilters');
const transactionsBody = document.getElementById('transactionsBody');
const transactionCount = document.getElementById('transactionCount');
const pagination = document.getElementById('pagination');

// Chart instances
let typeChart, monthlyChart;

// Initialize the dashboard
document.addEventListener('DOMContentLoaded', function() {
    // Set default date range (last 30 days)
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    startDate.valueAsDate = thirtyDaysAgo;
    endDate.valueAsDate = today;
    
    // Load initial data
    loadSummaryData();
    loadTransactions();
    
    // Event listeners
    applyFiltersBtn.addEventListener('click', applyFilters);
    resetFiltersBtn.addEventListener('click', resetFilters);
});

// API Functions
async function fetchTransactions(filters = {}) {
    try {
        const params = new URLSearchParams();
        
        if (filters.type) params.append('type', filters.type);
        if (filters.startDate) params.append('start_date', filters.startDate);
        if (filters.endDate) params.append('end_date', filters.endDate);
        if (filters.minAmount) params.append('min_amount', filters.minAmount);
        if (filters.maxAmount) params.append('max_amount', filters.maxAmount);
        
        const response = await fetch(`/api/transactions?${params.toString()}`);
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        if (!data.success) throw new Error(data.error || 'Unknown error');
        
        return data.data;
    } catch (error) {
        console.error('Error fetching transactions:', error);
        showError('Failed to load transactions. Please try again.');
        return [];
    }
}

async function fetchSummaryData() {
    try {
        const response = await fetch('/api/summary');
        if (!response.ok) throw new Error('Network response was not ok');
        
        const data = await response.json();
        if (!data.success) throw new Error(data.error || 'Unknown error');
        
        return data.data;
    } catch (error) {
        console.error('Error fetching summary data:', error);
        showError('Failed to load summary data. Please try again.');
        return null;
    }
}

// Data Loading Functions
async function loadTransactions() {
    const filters = getCurrentFilters();
    allTransactions = await fetchTransactions(filters);
    filteredTransactions = [...allTransactions];
    
    updateTransactionCount();
    renderTransactionsTable();
    renderPagination();
}

async function loadSummaryData() {
    const summary = await fetchSummaryData();
    if (summary) {
        renderTypeChart(summary.by_type);
        renderMonthlyChart(summary.monthly);
    }
}

// Filter Functions
function getCurrentFilters() {
    return {
        type: typeFilter.value,
        startDate: startDate.value,
        endDate: endDate.value,
        minAmount: minAmount.value,
        maxAmount: maxAmount.value
    };
}

function applyFilters() {
    currentPage = 1;
    loadTransactions();
}

function resetFilters() {
    typeFilter.value = '';
    startDate.value = '';
    endDate.value = '';
    minAmount.value = '';
    maxAmount.value = '';
    
    // Reset to default date range
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    startDate.valueAsDate = thirtyDaysAgo;
    endDate.valueAsDate = today;
    
    applyFilters();
}

// Rendering Functions
function renderTransactionsTable() {
    const startIdx = (currentPage - 1) * transactionsPerPage;
    const endIdx = startIdx + transactionsPerPage;
    const pageTransactions = filteredTransactions.slice(startIdx, endIdx);
    
    transactionsBody.innerHTML = '';
    
    if (pageTransactions.length === 0) {
        transactionsBody.innerHTML = `
            <tr>
                <td colspan="5" class="no-results">No transactions found matching your criteria</td>
            </tr>
        `;
        return;
    }
    
    pageTransactions.forEach(transaction => {
        const row = document.createElement('tr');
        
        // Date cell
        const dateCell = document.createElement('td');
        dateCell.textContent = formatDate(transaction.transaction_date);
        row.appendChild(dateCell);
        
        // Type cell
        const typeCell = document.createElement('td');
        typeCell.textContent = formatTransactionType(transaction.transaction_type);
        row.appendChild(typeCell);
        
        // Amount cell
        const amountCell = document.createElement('td');
        amountCell.textContent = transaction.amount ? 
            formatCurrency(transaction.amount) : 'N/A';
        amountCell.classList.add('amount');
        row.appendChild(amountCell);
        
        // Party cell (recipient or sender)
        const partyCell = document.createElement('td');
        partyCell.textContent = transaction.recipient || transaction.sender || 'N/A';
        row.appendChild(partyCell);
        
        // Details cell
        const detailsCell = document.createElement('td');
        detailsCell.textContent = truncateText(transaction.message_body, 50);
        detailsCell.title = transaction.message_body;
        row.appendChild(detailsCell);
        
        transactionsBody.appendChild(row);
    });
}

function renderTypeChart(data) {
    const ctx = document.getElementById('typeChart').getContext('2d');
    
    if (typeChart) typeChart.destroy();
    
    typeChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(item => formatTransactionType(item.transaction_type)),
            datasets: [{
                data: data.map(item => item.total || 0),
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0',
                    '#9966FF', '#FF9F40', '#8AC24A', '#607D8B'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.raw || 0;
                            return `${label}: ${formatCurrency(value)}`;
                        }
                    }
                }
            }
        }
    });
}

function renderMonthlyChart(data) {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    
    if (monthlyChart) monthlyChart.destroy();
    
    monthlyChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.month),
            datasets: [{
                label: 'Total Amount (RWF)',
                data: data.map(item => item.total || 0),
                backgroundColor: '#FFCC00',
                borderColor: '#FFCC00',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${formatCurrency(context.raw)}`;
                        }
                    }
                }
            }
        }
    });
}

function renderPagination() {
    const totalPages = Math.ceil(filteredTransactions.length / transactionsPerPage);
    
    pagination.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = 'Previous';
    prevBtn.classList.add('page-btn');
    prevBtn.disabled = currentPage === 1;
    prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            renderTransactionsTable();
            renderPagination();
        }
    });
    pagination.appendChild(prevBtn);
    
    // Page buttons
    for (let i = 1; i <= totalPages; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.classList.add('page-btn');
        if (i === currentPage) pageBtn.classList.add('active');
        
        pageBtn.addEventListener('click', () => {
            currentPage = i;
            renderTransactionsTable();
            renderPagination();
        });
        
        pagination.appendChild(pageBtn);
    }
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next';
    nextBtn.classList.add('page-btn');
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            renderTransactionsTable();
            renderPagination();
        }
    });
    pagination.appendChild(nextBtn);
}

// Helper Functions
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

function formatTransactionType(type) {
    const typeMap = {
        'incoming': 'Incoming',
        'payment': 'Payment',
        'transfer': 'Transfer',
        'deposit': 'Deposit',
        'airtime': 'Airtime',
        'cash_power': 'Cash Power',
        'withdrawal': 'Withdrawal',
        'bundle': 'Bundle',
        'other': 'Other'
    };
    
    return typeMap[type] || type;
}

function formatCurrency(amount) {
    if (amount === null || amount === undefined) return 'N/A';
    return new Intl.NumberFormat('en-RW', {
        style: 'currency',
        currency: 'RWF',
        minimumFractionDigits: 0
    }).format(amount);
}

function truncateText(text, maxLength) {
    if (!text) return '';
    return text.length > maxLength ? 
        text.substring(0, maxLength) + '...' : text;
}

function updateTransactionCount() {
    transactionCount.textContent = filteredTransactions.length;
}

function showError(message) {
    // In a real app, you'd show this in a nice error message area
    console.error(message);
    alert(message);
}
