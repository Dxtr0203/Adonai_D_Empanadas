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

  // top navbar cart button (may have href to checkout) -> open modal
  const topBtn = document.getElementById('top-cart-btn');
  if(topBtn){
    topBtn.addEventListener('click', function(e){
      // if the element has data-bs-toggle assigned elsewhere, let it handle. Otherwise open modal
      if(this.getAttribute('href') && this.getAttribute('href').indexOf('#') !== 0){
        e.preventDefault();
      } else {
        e.preventDefault();
      }
      const modalEl = document.getElementById('cart-modal');
      if(modalEl){
        showCart();
        const m = new bootstrap.Modal(modalEl);
        m.show();
      }
    });
  }

  // catalog's cart-icon also should populate before modal shown
  const modalEl = document.getElementById('cart-modal');
  if(modalEl){
    modalEl.addEventListener('shown.bs.modal', function(){ showCart(); });
  }

  // protect add-to-cart quantity inputs from typing 'e' or signs
  document.querySelectorAll('.quantity-input').forEach(function(inp){
    inp.addEventListener('keydown', function(e){ if(e.key==='e'||e.key==='E'||e.key==='+'||e.key==='-'||e.key==='.') e.preventDefault(); });
  });

  // go-to-checkout button behavior
  const go = document.getElementById('go-to-checkout');
  if(go){
    go.addEventListener('click', function(evt){
      if(!cart || cart.length === 0){ evt.preventDefault(); alert('Tu carrito está vacío. Añade productos antes de ir a pagar.'); return false; }
      return true;
    });
  }
});

