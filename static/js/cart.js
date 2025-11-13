// Global cart utilities - used by templates (addToCart called from product cards)
let cart = JSON.parse(localStorage.getItem('cart')) || [];

function saveCart() {
  localStorage.setItem('cart', JSON.stringify(cart));
  updateCartCount();
}

function updateCartCount() {
  const el = document.getElementById('cart-count');
  if (!el) return;
  try { el.textContent = String(cart.length); } catch (e) {}
}

function validateQuantity(value){
  if(value === undefined || value === null) return { valid:false, message: 'Cantidad inválida' };
  const s = String(value).trim();
  if(s.length === 0) return { valid:false, message: 'Ingrese una cantidad' };
  if(!/^\d+$/.test(s)) return { valid:false, message: 'La cantidad debe ser un número entero sin signos ni letras' };
  const n = parseInt(s, 10);
  if(isNaN(n)) return { valid:false, message: 'Cantidad inválida' };
  if(n <= 0) return { valid:false, message: 'La cantidad debe ser mayor que cero' };
  return { valid:true, value:n };
}

function showQtyError(inputId, message){
  if(!inputId) return;
  try{
    let base = inputId.replace(/^quantity-/, '');
    let errId = 'qty-error-' + base;
    const err = document.getElementById(errId);
    if(err){ err.textContent = message; err.classList.remove('d-none'); }
  }catch(e){}
}

function clearQtyError(inputId){
  if(!inputId) return;
  try{
    let base = inputId.replace(/^quantity-/, '');
    let errId = 'qty-error-' + base;
    const err = document.getElementById(errId);
    if(err){ err.textContent = ''; err.classList.add('d-none'); }
  }catch(e){}
}

function addToCart(productId, productName, productPrice, quantity, inputId){
  const v = validateQuantity(quantity);
  if(!v.valid){
    if(inputId) { showQtyError(inputId, v.message); try{ document.getElementById(inputId).focus(); }catch(e){} }
    else alert(v.message);
    return;
  }
  if(inputId) clearQtyError(inputId);
  const qty = v.value;

  // check stock if input has data-stock
  if(inputId){
    try{
      const inp = document.getElementById(inputId);
      if(inp){
        const stockAttr = inp.getAttribute('data-stock');
        if(stockAttr !== null){
          const stock = parseInt(stockAttr, 10);
          if(!isNaN(stock) && qty > stock){
            showQtyError(inputId, 'Cantidad supera el stock disponible (' + stock + ')');
            try{ inp.focus(); } catch(e){}
            return;
          }
        }
      }
    }catch(e){}
  }

  const pid = Number(productId);
  const existing = cart.find(it => Number(it.id) === pid);
  if(existing){ existing.cantidad = Number(existing.cantidad) + qty; }
  else { cart.push({ id: pid, nombre: productName, precio: productPrice, cantidad: qty }); }

  saveCart();

  // feedback
  if(window.bootstrap && typeof bootstrap.Toast === 'function'){
    const toastEl = document.createElement('div');
    toastEl.className = 'toast align-items-center text-bg-success border-0 position-fixed';
    toastEl.style.right = '16px';
    toastEl.style.bottom = '16px';
    toastEl.setAttribute('role','status');
    toastEl.innerHTML = `<div class="d-flex"><div class="toast-body">Producto añadido al carrito</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
    document.body.appendChild(toastEl);
    const t = new bootstrap.Toast(toastEl, { delay: 1600 });
    t.show();
    setTimeout(()=> toastEl.remove(), 2000);
  } else {
    console.log('Producto añadido al carrito');
  }
}

function showCart(){
  const cartItems = document.getElementById('cart-items');
  if(!cartItems) return;
  cartItems.innerHTML = '';
  if(cart.length === 0){ cartItems.innerHTML = '<p>No hay productos en el carrito.</p>'; return; }
  cart.forEach(item => {
    const row = document.createElement('div');
    row.className = 'd-flex align-items-center justify-content-between gap-2 mb-2';
    // compute subtotal for this line
    const unit = parseFloat(String(item.precio).replace(',', '.')) || 0;
    const subtotal = (unit * Number(item.cantidad)) || 0;
    row.innerHTML = `
      <div class="flex-grow-1">
        <div class="fw-bold">${item.nombre}</div>
        <div class="small text-muted">Bs. ${Number(unit).toFixed(2)} • <small class="text-muted">Subtotal: Bs. ${Number(subtotal).toFixed(2)}</small></div>
      </div>
      <div style="width:110px">
        <input type="number" min="1" class="form-control form-control-sm" value="${item.cantidad}" onchange="updateQuantity(${item.id}, this.value)">
      </div>
      <div>
        <button class="btn btn-sm btn-outline-danger" onclick="removeFromCart(${item.id})">Eliminar</button>
      </div>
    `;
    cartItems.appendChild(row);
  });
  // compute grand total
  try{
    const total = cart.reduce((acc, it) => acc + ((parseFloat(String(it.precio).replace(',', '.'))||0) * Number(it.cantidad)), 0);
    const totalEl = document.getElementById('cart-total');
    if(totalEl) totalEl.textContent = 'Bs. ' + Number(total).toFixed(2);
  }catch(e){ console.error('Error computing cart total', e); }
}

function updateQuantity(productId, newQuantity){
  const v = validateQuantity(newQuantity);
  if(!v.valid){ alert(v.message); showCart(); return; }
  // check stock if original product input exists
  try{
    const prodInput = document.getElementById('quantity-' + productId);
    if(prodInput){
      const stockAttr = prodInput.getAttribute('data-stock');
      if(stockAttr !== null){
        const stock = parseInt(stockAttr, 10);
        if(!isNaN(stock) && v.value > stock){ alert('La cantidad solicitada supera el stock disponible (' + stock + ')'); showCart(); return; }
      }
    }
  }catch(e){}

  const it = cart.find(i => Number(i.id) === Number(productId));
  if(it){ it.cantidad = v.value; saveCart(); showCart(); }
}

function removeFromCart(productId){
  cart = cart.filter(i => Number(i.id) !== Number(productId)); saveCart(); showCart();
}

// wire UI events on DOM ready
document.addEventListener('DOMContentLoaded', function(){
  updateCartCount();

  // When cart modal is shown, populate the items
  const modalEl = document.getElementById('cart-modal');
  if(modalEl){
    modalEl.addEventListener('shown.bs.modal', function(){ showCart(); });
    // Also populate when hidden to ensure clean state
    modalEl.addEventListener('hidden.bs.modal', function(){ 
      // Optional: clear any lingering state here if needed
    });
  }

  // protect add-to-cart quantity inputs from typing 'e' or signs
  document.querySelectorAll('.quantity-input').forEach(function(inp){
    inp.addEventListener('keydown', function(e){ if(e.key==='e'||e.key==='E'||e.key==='+'||e.key==='-'||e.key==='.') e.preventDefault(); });
  });

  // go-to-checkout button behavior
  const go = document.getElementById('go-to-checkout');
  if(go){
    go.addEventListener('click', function(evt){
      if(!cart || cart.length === 0){ 
        evt.preventDefault(); 
        alert('Tu carrito está vacío. Añade productos antes de ir a pagar.'); 
        return false; 
      }
      // Close the modal before navigating
      const modalEl = document.getElementById('cart-modal');
      if(modalEl){
        const m = bootstrap.Modal.getInstance(modalEl);
        if(m) m.hide();
      }
      return true;
    });
  }

  // Instant search and category filter for catalog
  function setupCatalogFilters() {
    const categorySelect = document.getElementById('category-select');
    const searchInput = document.getElementById('search-input');

    function updateCatalog() {
      const category = categorySelect ? categorySelect.value : '';
      const searchTerm = searchInput ? searchInput.value.trim().toLowerCase() : '';

      const items = document.querySelectorAll('.catalog-item');
      items.forEach(item => {
        const itemCategory = item.getAttribute('data-category').toLowerCase();
        const itemName = item.getAttribute('data-name').toLowerCase();

        const matchesCategory = category === 'Todas' || itemCategory === category.toLowerCase();
        const matchesSearch = !searchTerm || itemName.includes(searchTerm);

        if (matchesCategory && matchesSearch) {
          item.style.display = '';
        } else {
          item.style.display = 'none';
        }
      });
    }

    if (categorySelect) {
      categorySelect.addEventListener('change', updateCatalog);
    }

    if (searchInput) {
      searchInput.addEventListener('input', updateCatalog);
    }
  }

  setupCatalogFilters();
});

