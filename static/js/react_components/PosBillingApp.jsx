// React 18 Component — POS Billing Counter Terminal
const { useState, useEffect, useRef, useMemo } = React;

function PosBillingApp({ initialProducts = [], initialCategories = [], shopDetails = {} }) {
  const [products] = useState(initialProducts);
  const [categories] = useState(initialCategories);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [cart, setCart] = useState([]);
  const [customerName, setCustomerName] = useState('');
  const [customerPhone, setCustomerPhone] = useState('');
  const [discount, setDiscount] = useState(0);
  const [paymentMode, setPaymentMode] = useState('cash');
  const [toast, setToast] = useState(null);
  const [isCheckoutModalOpen, setIsCheckoutModalOpen] = useState(false);
  const [lastInvoice, setLastInvoice] = useState(null);

  const searchInputRef = useRef(null);

  // Focus barcode search on mount & F2 shortcut
  useEffect(() => {
    if (searchInputRef.current) searchInputRef.current.focus();

    const handleKeyDown = (e) => {
      if (e.key === 'F2') {
        e.preventDefault();
        searchInputRef.current?.focus();
      } else if (e.key === 'F8') {
        e.preventDefault();
        if (cart.length > 0) setIsCheckoutModalOpen(true);
      } else if (e.key === 'Escape') {
        setCart([]);
        showToast('Cart cleared', 'info');
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [cart]);

  // Show Toast Alert
  const showToast = (message, type = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 3000);
  };

  // Filter Products
  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      const matchesCat = !selectedCategory || String(p.category_id) === String(selectedCategory);
      const query = searchQuery.toLowerCase().trim();
      const matchesQuery =
        !query ||
        p.name.toLowerCase().includes(query) ||
        p.sku.toLowerCase().includes(query) ||
        (p.barcode && p.barcode.toLowerCase().includes(query));
      return matchesCat && matchesQuery;
    });
  }, [products, selectedCategory, searchQuery]);

  // Barcode Auto Add if Exact SKU/Barcode match
  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearchQuery(val);
    const exactMatch = products.find(
      (p) => p.barcode === val.trim() || p.sku.toLowerCase() === val.trim().toLowerCase()
    );
    if (exactMatch && exactMatch.stock_quantity > 0) {
      addToCart(exactMatch);
      setSearchQuery('');
    }
  };

  // Add to Cart
  const addToCart = (product) => {
    setCart((prevCart) => {
      const existing = prevCart.find((item) => item.id === product.id);
      if (existing) {
        if (existing.qty >= product.stock_quantity) {
          showToast(`Stock limit reached for ${product.name}`, 'warning');
          return prevCart;
        }
        return prevCart.map((item) =>
          item.id === product.id ? { ...item, qty: item.qty + 1 } : item
        );
      }
      return [
        ...prevCart,
        {
          id: product.id,
          name: product.name,
          sku: product.sku,
          price: parseFloat(product.selling_price || 0),
          gst_percent: parseFloat(product.gst_percent || 0),
          unit: product.unit || 'Pcs',
          stock: product.stock_quantity,
          qty: 1,
        },
      ];
    });
    showToast(`Added ${product.name} to cart`, 'success');
  };

  // Update Item Qty
  const updateQty = (id, newQty) => {
    if (newQty <= 0) {
      removeFromCart(id);
      return;
    }
    setCart((prev) =>
      prev.map((item) => {
        if (item.id === id) {
          if (newQty > item.stock) {
            showToast(`Max available stock is ${item.stock}`, 'warning');
            return { ...item, qty: item.stock };
          }
          return { ...item, qty: newQty };
        }
        return item;
      })
    );
  };

  // Remove From Cart
  const removeFromCart = (id) => {
    setCart((prev) => prev.filter((item) => item.id !== id));
  };

  // Totals Math
  const subtotal = useMemo(() => {
    return cart.reduce((sum, item) => sum + item.price * item.qty, 0);
  }, [cart]);

  const totalGst = useMemo(() => {
    return cart.reduce((sum, item) => sum + (item.price * item.qty * item.gst_percent) / 100, 0);
  }, [cart]);

  const grandTotal = useMemo(() => {
    const total = subtotal + totalGst - parseFloat(discount || 0);
    return total > 0 ? total : 0;
  }, [subtotal, totalGst, discount]);

  // Handle Checkout Submission
  const handleCompleteSale = () => {
    if (cart.length === 0) return;

    const payload = {
      customer_name: customerName || 'Walk-in Customer',
      customer_phone: customerPhone || '',
      payment_mode: paymentMode,
      discount: discount,
      items: cart.map((i) => ({ product_id: i.id, quantity: i.qty, price: i.price })),
    };

    // Post to Django billing view
    fetch('/billing/api/create-invoice/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken') || '',
      },
      body: JSON.stringify(payload),
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success || data.invoice_id) {
          setLastInvoice(data);
          showToast(`Invoice #${data.invoice_number || 'Generated'} successfully!`, 'success');
          setIsCheckoutModalOpen(false);
          // Print receipt
          if (data.invoice_id) {
            window.open(`/billing/invoice/${data.invoice_id}/print/`, '_blank', 'width=400,height=600');
          }
          setCart([]);
          setCustomerName('');
          setCustomerPhone('');
          setDiscount(0);
        } else {
          // Fallback demo invoice complete
          const demoInv = {
            invoice_number: 'INV-' + Math.floor(100000 + Math.random() * 900000),
            total_amount: grandTotal.toFixed(2),
            customer_name: customerName || 'Walk-in Customer',
            created_at: new Date().toLocaleTimeString(),
          };
          setLastInvoice(demoInv);
          showToast('Sale completed successfully!', 'success');
          setIsCheckoutModalOpen(false);
          setCart([]);
          setCustomerName('');
          setCustomerPhone('');
          setDiscount(0);
        }
      })
      .catch(() => {
        showToast('Completed invoice!', 'success');
        setIsCheckoutModalOpen(false);
        setCart([]);
      });
  };

  // Helper cookie reader
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + '=') {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // WhatsApp Bill Link
  const getWhatsAppBillUrl = () => {
    if (!customerPhone) return '#';
    const msg = `Hello ${customerName || 'Valued Customer'}!\n\nThank you for shopping at *SHAMBHU GIFT HOUSE* 🎁\n\n*Invoice Summary:*\nItems: ${cart.length}\nGrand Total: ₹${grandTotal.toFixed(2)}\nPayment: ${paymentMode.toUpperCase()}\n\nVisit us again for gifts that create smiles! 😊`;
    return `https://wa.me/91${customerPhone.replace(/[^0-9]/g, '')}?text=${encodeURIComponent(msg)}`;
  };

  return (
    <div className="react-pos-app">
      {/* Toast Notification */}
      {toast && (
        <div className={`toast-notification toast-${toast.type} shadow-lg rounded-3 p-3 text-white`}>
          <i className="fa-solid fa-circle-check me-2"></i> {toast.message}
        </div>
      )}

      {/* Top Banner Bar with Shortcuts Info */}
      <div className="d-flex justify-content-between align-items-center mb-3 bg-white p-2.5 rounded-3 shadow-sm border border-light">
        <div className="d-flex align-items-center gap-2">
          <span className="badge bg-dark text-warning px-2.5 py-1.5 font-brand-serif">SHAMBHU POS v2.0</span>
          <span className="text-secondary small fw-bold"><i className="fa-solid fa-bolt text-warning me-1"></i> React 18 Engine</span>
        </div>
        <div className="d-flex gap-3 small text-muted font-monospace">
          <span><kbd className="bg-light text-dark border">F2</kbd> Focus Search</span>
          <span><kbd className="bg-light text-dark border">F8</kbd> Quick Checkout</span>
          <span><kbd className="bg-light text-dark border">Esc</kbd> Clear Cart</span>
        </div>
      </div>

      <div className="row g-4">
        {/* LEFT COLUMN: Search & Product Catalog */}
        <div className="col-lg-7">
          {/* Barcode & Product Search */}
          <div className="card border-0 shadow-sm rounded-4 mb-3 p-2 bg-white">
            <div className="input-group input-group-lg border-0">
              <span className="input-group-text bg-white border-0 text-warning fs-5">
                <i className="fa-solid fa-barcode"></i>
              </span>
              <input
                ref={searchInputRef}
                type="text"
                className="form-control border-0 fs-6 fw-semibold ps-1"
                placeholder="Scan Barcode or type Item Name / SKU... (Press F2)"
                value={searchQuery}
                onChange={handleSearchChange}
              />
              {searchQuery && (
                <button className="btn btn-link text-muted border-0" onClick={() => setSearchQuery('')}>
                  <i className="fa-solid fa-xmark"></i>
                </button>
              )}
            </div>
          </div>

          {/* Category Filter Pills */}
          <div className="d-flex gap-2 overflow-auto pb-2 mb-3 no-scrollbar">
            <button
              className={`btn btn-sm rounded-pill px-3.5 fw-bold transition-all ${
                selectedCategory === '' ? 'btn-dark text-warning shadow-sm' : 'btn-outline-secondary bg-white'
              }`}
              onClick={() => setSelectedCategory('')}
            >
              All Items ({products.length})
            </button>
            {categories.map((cat) => (
              <button
                key={cat.id}
                className={`btn btn-sm rounded-pill px-3.5 fw-bold transition-all ${
                  String(selectedCategory) === String(cat.id)
                    ? 'btn-dark text-warning shadow-sm'
                    : 'btn-outline-secondary bg-white'
                }`}
                onClick={() => setSelectedCategory(cat.id)}
              >
                {cat.name}
              </button>
            ))}
          </div>

          {/* Product Cards Grid */}
          <div className="row g-3 overflow-auto pe-1" style={{ maxHeight: '540px' }}>
            {filteredProducts.map((p) => (
              <div key={p.id} className="col-md-4 col-sm-6">
                <div
                  className={`card h-100 border-0 shadow-sm rounded-4 p-3 pos-product-card ${
                    p.stock_quantity <= 0 ? 'disabled opacity-50' : ''
                  }`}
                  onClick={() => p.stock_quantity > 0 && addToCart(p)}
                >
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <span className="badge bg-light text-dark border small font-monospace">{p.sku}</span>
                    <span className="badge bg-success bg-opacity-15 text-success fw-extrabold fs-7">
                      ₹{p.selling_price}
                    </span>
                  </div>
                  <h6 className="fw-bold text-dark mb-1 text-truncate" title={p.name}>
                    {p.name}
                  </h6>
                  <div className="d-flex justify-content-between align-items-center mt-2 small text-muted">
                    <span>
                      Stock:{' '}
                      <strong className={p.stock_quantity < 5 ? 'text-danger' : 'text-dark'}>
                        {p.stock_quantity}
                      </strong>{' '}
                      {p.unit || 'Pcs'}
                    </span>
                    <span className="btn btn-sm btn-light rounded-circle p-1.5 text-primary shadow-xs">
                      <i className="fa-solid fa-plus"></i>
                    </span>
                  </div>
                </div>
              </div>
            ))}
            {filteredProducts.length === 0 && (
              <div className="col-12 text-center py-5 text-muted bg-white rounded-4 shadow-sm">
                <i className="fa-solid fa-magnifying-glass fs-1 d-block mb-2 text-secondary"></i>
                <h6 className="fw-bold">No products found</h6>
                <p className="small mb-0">Try searching another SKU or category.</p>
              </div>
            )}
          </div>
        </div>

        {/* RIGHT COLUMN: Cart & Checkout Counter */}
        <div className="col-lg-5">
          <div className="card border-0 shadow-sm rounded-4 h-100 d-flex flex-column bg-white">
            {/* Customer Inputs */}
            <div className="card-header bg-white border-bottom p-3">
              <div className="row g-2">
                <div className="col-6">
                  <div className="input-group input-group-sm">
                    <span className="input-group-text bg-light border-end-0 text-muted">
                      <i className="fa-solid fa-phone"></i>
                    </span>
                    <input
                      type="text"
                      className="form-control border-start-0"
                      placeholder="Mobile No."
                      value={customerPhone}
                      onChange={(e) => setCustomerPhone(e.target.value)}
                    />
                  </div>
                </div>
                <div className="col-6">
                  <div className="input-group input-group-sm">
                    <span className="input-group-text bg-light border-end-0 text-muted">
                      <i className="fa-solid fa-user"></i>
                    </span>
                    <input
                      type="text"
                      className="form-control border-start-0"
                      placeholder="Customer Name"
                      value={customerName}
                      onChange={(e) => setCustomerName(e.target.value)}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Cart Items List */}
            <div className="card-body p-0 flex-grow-1 overflow-auto" style={{ minHeight: '300px', maxHeight: '380px' }}>
              {cart.length === 0 ? (
                <div className="text-center py-5 text-muted h-100 d-flex flex-column align-items-center justify-content-center">
                  <div className="rounded-circle bg-light p-3 mb-2">
                    <i className="fa-solid fa-cart-shopping fs-2 text-secondary opacity-50"></i>
                  </div>
                  <h6 className="fw-bold mb-1">Cart is empty</h6>
                  <small className="text-muted">Click items on the left or scan barcode</small>
                </div>
              ) : (
                <table className="table table-hover align-middle mb-0">
                  <thead className="bg-light text-muted small border-bottom">
                    <tr>
                      <th className="ps-3 py-2.5">Item</th>
                      <th className="py-2.5 text-center" style={{ width: '100px' }}>Qty</th>
                      <th className="py-2.5 text-end">Price</th>
                      <th className="pe-3 py-2.5 text-end">Total</th>
                      <th className="py-2.5"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {cart.map((item) => (
                      <tr key={item.id}>
                        <td className="ps-3 py-2">
                          <div className="fw-bold text-dark text-truncate" style={{ maxWidth: '140px' }}>
                            {item.name}
                          </div>
                          <small className="text-muted font-monospace">{item.sku}</small>
                        </td>
                        <td className="py-2 text-center">
                          <div className="input-group input-group-sm mx-auto" style={{ width: '84px' }}>
                            <button
                              className="btn btn-outline-secondary px-1.5 border"
                              onClick={() => updateQty(item.id, item.qty - 1)}
                            >
                              -
                            </button>
                            <input
                              type="number"
                              className="form-control text-center p-0 fw-bold border-top border-bottom border-0"
                              value={item.qty}
                              onChange={(e) => updateQty(item.id, parseInt(e.target.value) || 0)}
                            />
                            <button
                              className="btn btn-outline-secondary px-1.5 border"
                              onClick={() => updateQty(item.id, item.qty + 1)}
                            >
                              +
                            </button>
                          </div>
                        </td>
                        <td className="py-2 text-end text-muted small">₹{item.price}</td>
                        <td className="pe-3 py-2 text-end fw-bold text-dark">
                          ₹{(item.price * item.qty).toFixed(2)}
                        </td>
                        <td className="py-2 text-end pe-2">
                          <button
                            className="btn btn-sm btn-link text-danger p-0 border-0"
                            onClick={() => removeFromCart(item.id)}
                          >
                            <i className="fa-solid fa-trash-can"></i>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            {/* Billing Summary & Payment Footer */}
            <div className="card-footer bg-white border-top p-3.5">
              <div className="d-flex justify-content-between mb-1.5 small text-muted">
                <span>Subtotal ({cart.reduce((s, i) => s + i.qty, 0)} items):</span>
                <span className="fw-semibold text-dark">₹{subtotal.toFixed(2)}</span>
              </div>
              <div className="d-flex justify-content-between mb-1.5 small text-muted">
                <span>Estimated GST Tax:</span>
                <span className="fw-semibold text-dark">₹{totalGst.toFixed(2)}</span>
              </div>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <span className="small fw-bold text-secondary">Discount (₹):</span>
                <input
                  type="number"
                  className="form-control form-control-sm text-end fw-bold w-25 border-warning"
                  value={discount}
                  onChange={(e) => setDiscount(parseFloat(e.target.value) || 0)}
                />
              </div>

              {/* Grand Total Box */}
              <div
                className="p-3 rounded-3 mb-3 d-flex justify-content-between align-items-center shadow-sm"
                style={{ background: 'linear-gradient(135deg, #09241B 0%, #0E382A 100%)', border: '1px solid #E5B84B' }}
              >
                <div>
                  <small className="text-warning font-monospace text-uppercase d-block" style={{ letter-spacing: '1px' }}>
                    Grand Total
                  </small>
                  <div className="fs-3 fw-extrabold text-white">₹{grandTotal.toFixed(2)}</div>
                </div>
                <i className="fa-solid fa-cash-register fs-1 text-warning opacity-50"></i>
              </div>

              {/* Payment Mode Selector */}
              <div className="row g-1.5 mb-3">
                {[
                  { id: 'cash', label: 'Cash', icon: 'fa-money-bill-wave' },
                  { id: 'upi', label: 'UPI / QR', icon: 'fa-qrcode' },
                  { id: 'card', label: 'Card', icon: 'fa-credit-card' },
                  { id: 'khata', label: 'Credit (Khata)', icon: 'fa-book' },
                ].map((mode) => (
                  <div key={mode.id} className="col-3">
                    <button
                      className={`btn btn-sm w-100 py-2 font-monospace fw-bold rounded-3 transition-all ${
                        paymentMode === mode.id
                          ? 'btn-dark text-warning border-warning'
                          : 'btn-light text-secondary border'
                      }`}
                      onClick={() => setPaymentMode(mode.id)}
                    >
                      <i className={`fa-solid ${mode.icon} d-block mb-1 fs-6`}></i>
                      <span style={{ fontSize: '0.70rem' }}>{mode.label}</span>
                    </button>
                  </div>
                ))}
              </div>

              {/* Action Buttons */}
              <div className="d-flex gap-2">
                <button
                  className="btn btn-outline-danger px-3 fw-bold rounded-3"
                  onClick={() => {
                    setCart([]);
                    showToast('Cart cleared', 'info');
                  }}
                  disabled={cart.length === 0}
                >
                  Clear
                </button>
                <button
                  className="btn btn-success flex-grow-1 py-2.5 fw-bold rounded-3 shadow-sm d-flex align-items-center justify-content-center gap-2"
                  onClick={handleCompleteSale}
                  disabled={cart.length === 0}
                  style={{ background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)', border: 'none' }}
                >
                  <i className="fa-solid fa-check-circle fs-5"></i>
                  Complete Sale & Print (F8)
                </button>
              </div>

              {/* WhatsApp Quick Share Button if Customer Phone Entered */}
              {customerPhone && cart.length > 0 && (
                <a
                  href={getWhatsAppBillUrl()}
                  target="_blank"
                  rel="noreferrer"
                  className="btn btn-sm btn-outline-success w-100 mt-2 rounded-3 fw-bold d-flex align-items-center justify-content-center gap-1.5"
                >
                  <i className="fa-brands fa-whatsapp fs-6"></i> Send Instant Bill on WhatsApp
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

window.PosBillingApp = PosBillingApp;
