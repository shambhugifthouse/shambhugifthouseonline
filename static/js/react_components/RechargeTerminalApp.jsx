// React 18 Component — Mobile & DTH Recharge Terminal
const { useState } = React;

function RechargeTerminalApp() {
  const [serviceType, setServiceType] = useState('mobile'); // 'mobile' or 'dth'
  const [operator, setOperator] = useState('jio');
  const [number, setNumber] = useState('');
  const [amount, setAmount] = useState('');
  const [paymentMode, setPaymentMode] = useState('CASH'); // 'CASH' or 'ONLINE'
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [activePlanCategory, setActivePlanCategory] = useState('Unlimited');
  const [isConfirming, setIsConfirming] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [toast, setToast] = useState(null);

  const mobileOperators = [
    { id: 'jio', name: 'Jio 5G', color: '#0F288A', badge: 'JIO' },
    { id: 'airtel', name: 'Airtel 5G', color: '#E40000', badge: 'AIRTEL 5G' },
    { id: 'vi', name: 'Vi (Vodafone Idea)', color: '#D32F2F', badge: 'VI' },
    { id: 'bsnl', name: 'BSNL TopUp', color: '#007A3D', badge: 'BSNL' },
  ];

  const dthOperators = [
    { id: 'tataplay', name: 'Tata Play (Sky)', color: '#6A1B9A', badge: 'TATA' },
    { id: 'airteldth', name: 'Airtel Digital TV', color: '#E40000', badge: 'AIRTEL DTH' },
    { id: 'sundirect', name: 'Sun Direct', color: '#E65100', badge: 'SUN' },
    { id: 'dishtv', name: 'Dish TV', color: '#C2185B', badge: 'DISH' },
  ];

  const samplePlans = [
    { id: 1, category: 'Unlimited', price: 299, validity: '28 Days', data: '1.5 GB/Day', desc: 'Unlimited Calls + 100 SMS/Day' },
    { id: 2, category: 'Unlimited', price: 349, validity: '28 Days', data: '2.0 GB/Day', desc: '5G Unlimited Data + Calls' },
    { id: 3, category: 'Unlimited', price: 719, validity: '84 Days', data: '1.5 GB/Day', desc: 'Long Validity Value Pack' },
    { id: 4, category: 'Data', price: 19, validity: 'Active Plan', data: '1 GB', desc: 'Data Booster Pack' },
    { id: 5, category: 'Data', price: 61, validity: 'Active Plan', data: '6 GB', desc: 'High-speed Data Top-up' },
    { id: 6, category: 'Talktime', price: 100, validity: 'Unlimited', data: 'N/A', desc: 'Full Talktime Value: ₹81.75' },
  ];

  const filteredPlans = samplePlans.filter((p) => p.category === activePlanCategory);

  const handleSelectPlan = (plan) => {
    setSelectedPlan(plan);
    setAmount(plan.price.toString());
  };

  const handleRechargeSubmit = () => {
    if (!number || number.length < 10) {
      showToast('Please enter a valid 10-digit number / VC ID', 'warning');
      return;
    }
    if (!amount || parseFloat(amount) <= 0) {
      showToast('Please select or enter a valid amount', 'warning');
      return;
    }
    setIsConfirming(true);
  };

  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const processRecharge = () => {
    if (isSubmitting) return; // Anti-duplicate protection
    setIsSubmitting(true);
    setIsConfirming(false);

    showToast(`Recharge of ₹${amount} (${paymentMode}) for ${number} completed successfully!`, 'success');
    
    setTimeout(() => {
      setIsSubmitting(false);
      setNumber('');
      setAmount('');
      setSelectedPlan(null);
    }, 1500);
  };

  const currentOps = serviceType === 'mobile' ? mobileOperators : dthOperators;

  return (
    <div className="react-recharge-app">
      {/* Toast Alert */}
      {toast && (
        <div className={`toast-notification toast-${toast.type} shadow-lg rounded-3 p-3 text-white`}>
          <i className="fa-solid fa-circle-check me-2"></i> {toast.message}
        </div>
      )}

      {/* Service Type Switcher */}
      <div className="d-flex justify-content-center mb-4">
        <div className="btn-group btn-group-lg rounded-pill p-1.5 bg-white shadow-sm border" style={{ maxWidth: '420px', width: '100%' }}>
          <button
            className={`btn rounded-pill fw-bold border-0 py-2.5 ${serviceType === 'mobile' ? 'btn-dark text-warning shadow-sm' : 'btn-light text-muted'}`}
            onClick={() => { setServiceType('mobile'); setOperator('jio'); }}
          >
            <i className="fa-solid fa-mobile-screen-button me-2"></i> Mobile Recharge
          </button>
          <button
            className={`btn rounded-pill fw-bold border-0 py-2.5 ${serviceType === 'dth' ? 'btn-dark text-warning shadow-sm' : 'btn-light text-muted'}`}
            onClick={() => { setServiceType('dth'); setOperator('tataplay'); }}
          >
            <i className="fa-solid fa-tv me-2"></i> DTH Satellite TV
          </button>
        </div>
      </div>

      <div className="row g-4">
        {/* LEFT COLUMN: Operator, Payment Mode & Number Input */}
        <div className="col-lg-5">
          <div className="card border-0 shadow-sm rounded-4 p-4 bg-white">
            <h5 className="fw-bold text-dark mb-3 font-heading">
              Select Operator & Payment Details
            </h5>

            {/* Operator Grid */}
            <div className="row g-2 mb-3">
              {currentOps.map((op) => (
                <div key={op.id} className="col-6">
                  <div
                    className={`p-3 rounded-3 border text-center transition-all ${
                      operator === op.id ? 'border-warning bg-light shadow-xs' : 'border-light bg-white'
                    }`}
                    style={{ cursor: 'pointer' }}
                    onClick={() => setOperator(op.id)}
                  >
                    <span className="badge rounded-pill text-white px-3 py-1.5 mb-1.5 font-monospace fw-bold" style={{ background: op.color }}>
                      {op.badge}
                    </span>
                    <small className="d-block fw-bold text-dark">{op.name}</small>
                  </div>
                </div>
              ))}
            </div>

            {/* Payment Mode Choice: Cash vs Online */}
            <div className="mb-3">
              <label className="form-label fw-bold small text-secondary">Payment Received Mode</label>
              <div className="btn-group w-100 p-1 rounded-3 bg-light border" role="group">
                <button
                  type="button"
                  className={`btn btn-sm py-2 fw-bold rounded-2 ${paymentMode === 'CASH' ? 'btn-success text-white shadow-xs' : 'btn-light text-secondary'}`}
                  onClick={() => setPaymentMode('CASH')}
                >
                  💵 Cash Payment
                </button>
                <button
                  type="button"
                  className={`btn btn-sm py-2 fw-bold rounded-2 ${paymentMode === 'ONLINE' ? 'btn-primary text-white shadow-xs' : 'btn-light text-secondary'}`}
                  onClick={() => setPaymentMode('ONLINE')}
                >
                  📱 Online / UPI
                </button>
              </div>
            </div>

            {/* Input Form */}
            <div className="mb-3">
              <label className="form-label fw-bold small text-secondary">
                {serviceType === 'mobile' ? '10-Digit Mobile Number' : 'DTH Customer ID / VC Number'}
              </label>

              <div className="input-group input-group-lg">
                <span className="input-group-text bg-light text-muted border-end-0">
                  <i className={`fa-solid ${serviceType === 'mobile' ? 'fa-phone' : 'fa-tv'}`}></i>
                </span>
                <input
                  type="text"
                  className="form-control border-start-0 fs-6 fw-bold"
                  placeholder={serviceType === 'mobile' ? 'Enter 10 digit number' : 'Enter VC / Subscriber ID'}
                  value={number}
                  onChange={(e) => setNumber(e.target.value)}
                />
              </div>
            </div>

            <div className="mb-4">
              <label className="form-label fw-bold small text-secondary">Recharge Amount (₹)</label>
              <div className="input-group input-group-lg">
                <span className="input-group-text bg-light text-muted border-end-0">₹</span>
                <input
                  type="number"
                  className="form-control border-start-0 fs-5 fw-extrabold text-success"
                  placeholder="Enter amount or pick plan"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                />
              </div>
            </div>

            {/* Action Buttons: Instant Recharge & Quick Recharge Side-by-Side */}
            <div className="d-flex gap-2">
              <button
                className="btn btn-warning flex-grow-1 py-3 fw-extrabold rounded-3 shadow-sm font-brand-serif fs-6"
                onClick={handleRechargeSubmit}
                disabled={isSubmitting}
                style={{ background: 'linear-gradient(135deg, #F5DA8A 0%, #E5B84B 100%)', border: 'none', color: '#09241B' }}
              >
                <i className="fa-solid fa-bolt me-1.5"></i> Instant Recharge
              </button>
              
              <button
                className="btn btn-dark py-3 px-3 fw-bold rounded-3 shadow-sm fs-6"
                data-bs-toggle="modal"
                data-bs-target="#quickRechargeModal"
                type="button"
                title="Quick Operator Entry"
              >
                <i className="fa-solid fa-square-plus me-1 text-warning"></i> Quick
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: Plan Browser Tabs */}
        <div className="col-lg-7">
          <div className="card border-0 shadow-sm rounded-4 p-4 bg-white h-100">
            <div className="d-flex justify-content-between align-items-center mb-3">
              <h5 className="fw-bold text-dark mb-0 font-heading">Recommended Plans</h5>
              <span className="badge bg-light text-dark border font-monospace text-uppercase">{operator}</span>
            </div>

            {/* Plan Category Tabs */}
            <div className="d-flex gap-2 border-bottom pb-2 mb-3">
              {['Unlimited', 'Data', 'Talktime'].map((cat) => (
                <button
                  key={cat}
                  className={`btn btn-sm rounded-pill px-3.5 fw-bold ${
                    activePlanCategory === cat ? 'btn-dark text-warning' : 'btn-outline-secondary'
                  }`}
                  onClick={() => setActivePlanCategory(cat)}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* Plans List */}
            <div className="overflow-auto pe-1" style={{ maxHeight: '360px' }}>
              {filteredPlans.map((plan) => (
                <div
                  key={plan.id}
                  className={`card border rounded-3 p-3 mb-2.5 transition-all ${
                    selectedPlan?.id === plan.id ? 'border-warning bg-light shadow-xs' : 'border-light bg-white'
                  }`}
                  style={{ cursor: 'pointer' }}
                  onClick={() => handleSelectPlan(plan)}
                >
                  <div className="d-flex justify-content-between align-items-center">
                    <div>
                      <span className="fs-4 fw-extrabold text-success me-3">₹{plan.price}</span>
                      <span className="badge bg-secondary bg-opacity-10 text-secondary me-2">Validity: {plan.validity}</span>
                      <span className="badge bg-primary bg-opacity-10 text-primary">Data: {plan.data}</span>
                    </div>
                    <button className="btn btn-sm btn-outline-warning fw-bold px-3">Select</button>
                  </div>
                  <p className="text-muted small mb-0 mt-2">{plan.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {isConfirming && (
        <div className="modal show d-block bg-dark bg-opacity-50" tabIndex="-1">
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content rounded-4 border-0 shadow-lg p-3">
              <div className="modal-header border-0 pb-0">
                <h5 className="modal-title fw-bold font-heading">Confirm Transaction</h5>
                <button className="btn-close" onClick={() => setIsConfirming(false)}></button>
              </div>
              <div className="modal-body p-4 text-center">
                <div className="p-3 rounded-4 mb-3" style={{ background: '#09241B', color: '#E5B84B' }}>
                  <small className="text-uppercase font-monospace d-block text-warning opacity-75">Target Number</small>
                  <h3 className="fw-extrabold mb-0">{number}</h3>
                  <small className="text-white-50">{operator.toUpperCase()} Operator • Mode: {paymentMode}</small>
                </div>
                <div className="fs-2 fw-extrabold text-success mb-3">₹{amount}</div>
                <p className="text-muted small">Please confirm payment ({paymentMode}) before processing.</p>
                <div className="d-flex gap-2">
                  <button className="btn btn-light w-50 py-2.5 fw-bold" onClick={() => setIsConfirming(false)} disabled={isSubmitting}>Cancel</button>
                  <button className="btn btn-success w-50 py-2.5 fw-bold" onClick={processRecharge} disabled={isSubmitting}>
                    {isSubmitting ? 'Processing...' : 'Confirm & Pay'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

window.RechargeTerminalApp = RechargeTerminalApp;
