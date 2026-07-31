// React 18 Component — Public Gift E-Commerce Storefront
const { useState, useMemo } = React;

function ShopFrontApp({ initialProducts = [], initialCategories = [], shopDetails = {} }) {
  const [products] = useState(initialProducts);
  const [categories] = useState(initialCategories);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [maxPrice, setMaxPrice] = useState(5000);
  const [cart, setCart] = useState([]);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [previewProduct, setPreviewProduct] = useState(null);

  // Filter Products
  const filteredProducts = useMemo(() => {
    return products.filter((p) => {
      const matchesCat = !selectedCategory || String(p.category_id) === String(selectedCategory);
      const matchesQuery =
        !searchQuery ||
        p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        p.sku.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesPrice = parseFloat(p.selling_price || 0) <= maxPrice;
      return matchesCat && matchesQuery && matchesPrice;
    });
  }, [products, selectedCategory, searchQuery, maxPrice]);

  // Cart operations
  const addToCart = (product) => {
    setCart((prev) => {
      const existing = prev.find((item) => item.id === product.id);
      if (existing) {
        return prev.map((item) =>
          item.id === product.id ? { ...item, qty: item.qty + 1 } : item
        );
      }
      return [...prev, { ...product, qty: 1 }];
    });
    setIsCartOpen(true);
  };

  const updateCartQty = (id, newQty) => {
    if (newQty <= 0) {
      setCart((prev) => prev.filter((i) => i.id !== id));
    } else {
      setCart((prev) => prev.map((i) => (i.id === id ? { ...i, qty: newQty } : i)));
    }
  };

  const totalCartPrice = useMemo(() => {
    return cart.reduce((sum, item) => sum + parseFloat(item.selling_price || 0) * item.qty, 0);
  }, [cart]);

  // WhatsApp Order payload
  const getWhatsAppOrderUrl = () => {
    if (cart.length === 0) return '#';
    let text = `*NEW GIFT ORDER — SHAMBHU GIFT HOUSE* 🎁\n\n*Items Ordered:*\n`;
    cart.forEach((item, idx) => {
      text += `${idx + 1}. ${item.name} (${item.sku}) x ${item.qty} = ₹${(
        parseFloat(item.selling_price) * item.qty
      ).toFixed(2)}\n`;
    });
    text += `\n*Total Amount:* ₹${totalCartPrice.toFixed(2)}\n\nPlease confirm availability and payment details. Thank you!`;
    return `https://wa.me/918975027902?text=${encodeURIComponent(text)}`;
  };

  return (
    <div className="react-shop-app">
      {/* Category Pills & Filters Header */}
      <div className="card border-0 shadow-sm rounded-4 p-3 mb-4 bg-white">
        <div className="row g-3 align-items-center">
          {/* Search Input */}
          <div className="col-md-5">
            <div className="input-group input-group-md">
              <span className="input-group-text bg-light border-end-0 text-muted">
                <i className="fa-solid fa-magnifying-glass"></i>
              </span>
              <input
                type="text"
                className="form-control bg-light border-start-0 fs-6"
                placeholder="Search soft toys, photo frames, Parker pens..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>

          {/* Price Range Slider */}
          <div className="col-md-4">
            <div className="d-flex justify-content-between small text-muted fw-bold mb-1">
              <span>Max Price:</span>
              <span className="text-dark">₹{maxPrice}</span>
            </div>
            <input
              type="range"
              className="form-range"
              min="50"
              max="5000"
              step="50"
              value={maxPrice}
              onChange={(e) => setMaxPrice(parseInt(e.target.value))}
            />
          </div>

          {/* Cart Counter Trigger Button */}
          <div className="col-md-3 text-md-end">
            <button
              className="btn btn-dark rounded-pill px-4 py-2 fw-bold d-inline-flex align-items-center gap-2 shadow-sm position-relative"
              onClick={() => setIsCartOpen(true)}
            >
              <i className="fa-solid fa-gift text-warning fs-5"></i>
              <span>View Cart</span>
              {cart.length > 0 && (
                <span className="badge bg-danger rounded-circle font-monospace">
                  {cart.reduce((s, i) => s + i.qty, 0)}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Category Pills */}
        <div className="d-flex gap-2 overflow-auto pt-3 border-top mt-3 no-scrollbar">
          <button
            className={`btn btn-sm rounded-pill px-3.5 fw-bold ${
              selectedCategory === '' ? 'btn-danger shadow-sm' : 'btn-outline-secondary'
            }`}
            onClick={() => setSelectedCategory('')}
          >
            All Categories ({products.length})
          </button>
          {categories.map((c) => (
            <button
              key={c.id}
              className={`btn btn-sm rounded-pill px-3.5 fw-bold ${
                String(selectedCategory) === String(c.id) ? 'btn-danger shadow-sm' : 'btn-outline-secondary'
              }`}
              onClick={() => setSelectedCategory(c.id)}
            >
              {c.name}
            </button>
          ))}
        </div>
      </div>

      {/* Product Cards Showcase Grid */}
      <div className="row g-4 mb-5">
        {filteredProducts.map((p) => (
          <div key={p.id} className="col-lg-3 col-md-4 col-sm-6">
            <div className="card h-100 border-0 shadow-sm rounded-4 overflow-hidden shop-product-card transition-all position-relative bg-white">
              {/* Product Image / Icon Showcase */}
              <div
                className="product-img-box position-relative bg-light d-flex align-items-center justify-content-center p-3"
                style={{ height: '200px', cursor: 'pointer' }}
                onClick={() => setPreviewProduct(p)}
              >
                {p.image ? (
                  <img src={p.image} alt={p.name} className="img-fluid max-h-100 object-fit-contain" style={{ maxHeight: '170px' }} />
                ) : (
                  <div className="text-center text-muted">
                    <i className="fa-solid fa-gift fs-1 text-danger opacity-50 mb-2"></i>
                    <span className="d-block small font-monospace">{p.sku}</span>
                  </div>
                )}
                <span className="badge bg-dark text-warning position-absolute top-0 start-0 m-3 px-2.5 py-1.5 font-monospace small rounded-pill">
                  {p.sku}
                </span>
                <span className="badge bg-success position-absolute top-0 end-0 m-3 px-2.5 py-1.5 fw-extrabold rounded-pill fs-7 shadow-xs">
                  ₹{p.selling_price}
                </span>
              </div>

              {/* Product Card Body */}
              <div className="card-body p-3.5 d-flex flex-column justify-content-between">
                <div>
                  <h6 className="fw-bold text-dark mb-1 text-truncate font-heading" title={p.name}>
                    {p.name}
                  </h6>
                  <p className="text-muted small mb-2 line-clamp-2" style={{ fontSize: '0.82rem', height: '2.5em' }}>
                    {p.description || 'Premium gift item available at Shambhu Gift House counter.'}
                  </p>
                </div>

                <div className="d-flex gap-2 mt-3 pt-2 stroke-top">
                  <button
                    className="btn btn-outline-dark btn-sm rounded-pill flex-grow-1 fw-bold"
                    onClick={() => setPreviewProduct(p)}
                  >
                    Quick View
                  </button>
                  <button
                    className="btn btn-danger btn-sm rounded-pill px-3 fw-bold d-flex align-items-center gap-1 shadow-sm"
                    onClick={() => addToCart(p)}
                    style={{ background: 'linear-gradient(135deg, #E11D48 0%, #BE123C 100%)', border: 'none' }}
                  >
                    <i className="fa-solid fa-cart-plus"></i> Add
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}

        {filteredProducts.length === 0 && (
          <div className="col-12 text-center py-5 bg-white rounded-4 shadow-sm">
            <i className="fa-solid fa-gift fs-1 text-muted d-block mb-3"></i>
            <h5 className="fw-bold">No gift items match your search</h5>
            <p className="text-muted small">Try clearing filters or adjusting your price slider.</p>
            <button className="btn btn-outline-danger rounded-pill px-4" onClick={() => { setSearchQuery(''); setSelectedCategory(''); setMaxPrice(5000); }}>
              Reset Filters
            </button>
          </div>
        )}
      </div>

      {/* Slide-over WhatsApp Cart Drawer */}
      {isCartOpen && (
        <div className="cart-drawer-overlay position-fixed top-0 start-0 w-100 h-100 bg-dark bg-opacity-50 d-flex justify-content-end" style={{ zIndex: 1060 }}>
          <div className="cart-drawer bg-white h-100 p-4 shadow-lg d-flex flex-column" style={{ width: '420px', maxWidth: '100vw' }}>
            {/* Drawer Header */}
            <div className="d-flex justify-content-between align-items-center border-bottom pb-3 mb-3">
              <div className="d-flex align-items-center gap-2">
                <i className="fa-solid fa-bag-shopping fs-4 text-danger"></i>
                <h5 className="fw-bold mb-0 font-heading">Your Gift Cart</h5>
              </div>
              <button className="btn-close" onClick={() => setIsCartOpen(false)}></button>
            </div>

            {/* Cart Items List */}
            <div className="cart-drawer-items flex-grow-1 overflow-auto pe-1 mb-3">
              {cart.length === 0 ? (
                <div className="text-center py-5 text-muted">
                  <i className="fa-solid fa-gift fs-1 text-secondary opacity-50 mb-2"></i>
                  <p className="fw-bold mb-0">Your gift cart is empty</p>
                </div>
              ) : (
                cart.map((item) => (
                  <div key={item.id} className="card border-0 bg-light rounded-3 p-3 mb-2.5">
                    <div className="d-flex justify-content-between align-items-start mb-1">
                      <h6 className="fw-bold text-dark mb-0 me-2">{item.name}</h6>
                      <span className="fw-extrabold text-success">₹{(parseFloat(item.selling_price) * item.qty).toFixed(2)}</span>
                    </div>
                    <div className="d-flex justify-content-between align-items-center mt-2">
                      <small className="text-muted font-monospace">{item.sku}</small>
                      <div className="input-group input-group-sm" style={{ width: '90px' }}>
                        <button className="btn btn-outline-secondary border px-2" onClick={() => updateCartQty(item.id, item.qty - 1)}>-</button>
                        <span className="form-control text-center bg-white border-0 fw-bold px-1">{item.qty}</span>
                        <button className="btn btn-outline-secondary border px-2" onClick={() => updateCartQty(item.id, item.qty + 1)}>+</button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Drawer Footer & Checkout Button */}
            <div className="border-top pt-3">
              <div className="d-flex justify-content-between align-items-center mb-3">
                <span className="fw-bold text-secondary">Total Gift Amount:</span>
                <span className="fs-4 fw-extrabold text-dark">₹{totalCartPrice.toFixed(2)}</span>
              </div>
              <a
                href={getWhatsAppOrderUrl()}
                target="_blank"
                rel="noreferrer"
                className={`btn btn-success w-100 py-3 fw-bold rounded-pill shadow-sm d-flex align-items-center justify-content-center gap-2 ${
                  cart.length === 0 ? 'disabled' : ''
                }`}
                style={{ background: 'linear-gradient(135deg, #25D366 0%, #128C7E 100%)', border: 'none' }}
              >
                <i className="fa-brands fa-whatsapp fs-5"></i> Order Directly via WhatsApp
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Product Quick Preview Modal */}
      {previewProduct && (
        <div className="modal show d-block bg-dark bg-opacity-50" tabIndex="-1">
          <div className="modal-dialog modal-dialog-centered">
            <div className="modal-content rounded-4 border-0 shadow-lg">
              <div className="modal-header border-0 pb-0">
                <h5 className="modal-title fw-bold font-heading">{previewProduct.name}</h5>
                <button className="btn-close" onClick={() => setPreviewProduct(null)}></button>
              </div>
              <div className="modal-body p-4">
                <div className="text-center mb-3 bg-light rounded-3 p-4">
                  {previewProduct.image ? (
                    <img src={previewProduct.image} alt={previewProduct.name} className="img-fluid max-h-200" style={{ maxHeight: '200px' }} />
                  ) : (
                    <i className="fa-solid fa-gift fs-1 text-danger"></i>
                  )}
                </div>
                <div className="d-flex justify-content-between align-items-center mb-3">
                  <span className="badge bg-dark text-warning px-3 py-2 font-monospace">{previewProduct.sku}</span>
                  <span className="fs-4 fw-extrabold text-success">₹{previewProduct.selling_price}</span>
                </div>
                <p className="text-muted small">{previewProduct.description || 'Exclusive gift item from Shambhu Gift House.'}</p>
                <button
                  className="btn btn-danger w-100 py-2.5 rounded-pill fw-bold"
                  onClick={() => { addToCart(previewProduct); setPreviewProduct(null); }}
                >
                  <i className="fa-solid fa-cart-plus me-1"></i> Add to Gift Cart
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

window.ShopFrontApp = ShopFrontApp;
