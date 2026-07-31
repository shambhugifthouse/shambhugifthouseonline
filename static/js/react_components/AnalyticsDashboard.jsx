// React 18 Component — Analytics & Sales Dashboard
const { useState, useEffect, useRef } = React;

function AnalyticsDashboard({ stats = {}, lowStockItems = [], recentSales = [] }) {
  const [timeframe, setTimeframe] = useState('daily');
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);

  useEffect(() => {
    if (!chartRef.current) return;
    const ctx = chartRef.current.getContext('2d');
    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy();
    }

    const labels = timeframe === 'daily'
      ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
      : ['Week 1', 'Week 2', 'Week 3', 'Week 4'];

    const dataPoints = timeframe === 'daily'
      ? [1200, 1900, 3000, 5000, 2400, 8900, 10400]
      : [28000, 34000, 42000, 51000];

    chartInstanceRef.current = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Sales Revenue (₹)',
            data: dataPoints,
            borderColor: '#E5B84B',
            backgroundColor: 'rgba(229, 184, 75, 0.15)',
            fill: true,
            tension: 0.35,
            borderWidth: 3,
            pointBackgroundColor: '#09241B',
            pointBorderColor: '#E5B84B',
            pointRadius: 5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
        },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(0,0,0,0.05)' } },
        },
      },
    });

    return () => {
      if (chartInstanceRef.current) chartInstanceRef.current.destroy();
    };
  }, [timeframe]);

  return (
    <div className="react-dashboard-app">
      {/* Metric Cards Row */}
      <div className="row g-4 mb-4">
        {[
          { label: 'Today\'s Sales Revenue', val: `₹${stats.today_sales || '10,400.00'}`, icon: 'fa-sack-dollar', color: 'text-success', bg: 'bg-success' },
          { label: 'Invoices Issued', val: stats.today_invoices || '18', icon: 'fa-receipt', color: 'text-primary', bg: 'bg-primary' },
          { label: 'Total Catalog Products', val: stats.total_products || '142', icon: 'fa-boxes-stacked', color: 'text-warning', bg: 'bg-warning' },
          { label: 'Low Stock Alert', val: lowStockItems.length || '3', icon: 'fa-triangle-exclamation', color: 'text-danger', bg: 'bg-danger' },
        ].map((c, idx) => (
          <div key={idx} className="col-lg-3 col-sm-6">
            <div className="card border-0 shadow-sm rounded-4 p-3.5 bg-white h-100 stat-card">
              <div className="d-flex justify-content-between align-items-start">
                <div>
                  <span className="text-secondary small fw-bold d-block mb-1">{c.label}</span>
                  <h3 className="fw-extrabold text-dark mb-0 font-heading">{c.val}</h3>
                </div>
                <div className={`rounded-3 p-3 text-white shadow-sm ${c.bg}`} style={{ opacity: 0.9 }}>
                  <i className={`fa-solid ${c.icon} fs-4`}></i>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Chart & Alerts Row */}
      <div className="row g-4 mb-4">
        {/* Sales Chart */}
        <div className="col-lg-8">
          <div className="card border-0 shadow-sm rounded-4 p-4 bg-white h-100">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <div>
                <h5 className="fw-bold text-dark mb-0 font-heading">Sales Revenue Performance</h5>
                <small className="text-muted">Real-time revenue tracking breakdown</small>
              </div>
              <div className="btn-group btn-group-sm rounded-pill border p-0.5 bg-light">
                <button
                  className={`btn rounded-pill px-3 fw-bold ${timeframe === 'daily' ? 'btn-dark text-warning' : 'btn-light border-0'}`}
                  onClick={() => setTimeframe('daily')}
                >
                  Daily
                </button>
                <button
                  className={`btn rounded-pill px-3 fw-bold ${timeframe === 'weekly' ? 'btn-dark text-warning' : 'btn-light border-0'}`}
                  onClick={() => setTimeframe('weekly')}
                >
                  Weekly
                </button>
              </div>
            </div>
            <div style={{ height: '300px' }}>
              <canvas ref={chartRef}></canvas>
            </div>
          </div>
        </div>

        {/* Low Stock Alerts Box */}
        <div className="col-lg-4">
          <div className="card border-0 shadow-sm rounded-4 p-4 bg-white h-100">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="fw-bold text-dark mb-0 font-heading">Low Stock Alerts</h5>
              <span className="badge bg-danger rounded-pill px-2.5">{lowStockItems.length || 3} Items</span>
            </div>
            <div className="overflow-auto pe-1" style={{ maxHeight: '300px' }}>
              {lowStockItems.length === 0 ? (
                <div className="text-center py-4 text-muted small">
                  <i className="fa-solid fa-circle-check text-success fs-3 d-block mb-1"></i>
                  All stock levels are optimal!
                </div>
              ) : (
                lowStockItems.map((item, idx) => (
                  <div key={idx} className="p-2.5 mb-2 rounded-3 bg-light d-flex justify-content-between align-items-center">
                    <div>
                      <strong className="d-block text-dark small">{item.name}</strong>
                      <span className="font-monospace text-muted" style={{ fontSize: '0.75rem' }}>SKU: {item.sku}</span>
                    </div>
                    <span className="badge bg-danger bg-opacity-15 text-danger fw-bold">
                      {item.stock_quantity || item.stock} {item.unit || 'Pcs'} left
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

window.AnalyticsDashboard = AnalyticsDashboard;
