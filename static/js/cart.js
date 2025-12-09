// Global cart utilities - used by templates (addToCart called from product cards)
let cart = JSON.parse(localStorage.getItem('cart')) || [];

function saveCart() {
  localStorage.setItem('cart', JSON.stringify(cart));
  updateCartCount();
}

function updateCartCount() {
  // Actualizar contador del header
  const el1 = document.getElementById('cart-count');
  if (el1) el1.textContent = String(cart.length);
  
  // Actualizar contador del catálogo
  const el2 = document.getElementById('cart-count-catalogo');
  if (el2) el2.textContent = String(cart.length);
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

function addToCart(productId, productName, productPrice, quantity, cuponOrInputId, inputId){
  // Permitir llamadas antiguas: addToCart(id, name, price, qty, inputId)
  // y nuevas: addToCart(id, name, price, qty, cupon, inputId)
  let cupon = null;
  let actualInputId = null;
  
  // Si el 5º parámetro es un string, es inputId (llamada antigua)
  // Si es un objeto, es cupon (llamada nueva)
  if (typeof cuponOrInputId === 'string') {
    actualInputId = cuponOrInputId;
  } else if (typeof cuponOrInputId === 'object') {
    cupon = cuponOrInputId;
    actualInputId = inputId || null;
  }
  
  const v = validateQuantity(quantity);
  if(!v.valid){
    if(actualInputId) { showQtyError(actualInputId, v.message); try{ document.getElementById(actualInputId).focus(); }catch(e){} }
    else alert(v.message);
    return;
  }
  if(actualInputId) clearQtyError(actualInputId);
  const qty = v.value;

  // Obtener stock del input si existe
  let stock = null;
  if(actualInputId){
    try{
      const inp = document.getElementById(actualInputId);
      if(inp){
        const stockAttr = inp.getAttribute('data-stock');
        if(stockAttr !== null){
          stock = parseInt(stockAttr, 10);
        }
      }
    }catch(e){}
  }

  // check stock if input has data-stock
  if(actualInputId){
    try{
      const inp = document.getElementById(actualInputId);
      if(inp){
        const stockAttr = inp.getAttribute('data-stock');
        if(stockAttr !== null){
          const stock = parseInt(stockAttr, 10);
          if(!isNaN(stock) && qty > stock){
            showQtyError(actualInputId, 'Cantidad supera el stock disponible (' + stock + ')');
            try{ inp.focus(); } catch(e){}
            return;
          }
        }
      }
    }catch(e){}
  }

  const pid = Number(productId);
  
  // Si tiene cupón, siempre crear un nuevo item (no agregar al existente)
  // Si NO tiene cupón, buscar si ya existe y agregar cantidad
  if (cupon) {
    // Con cupón: crear nuevo item siempre
    const newItem = { id: pid, nombre: productName, precio: productPrice, cantidad: qty, cupon: cupon };
    cart.push(newItem);
  } else {
    // Sin cupón: buscar existente (que tampoco tenga cupón)
    const existing = cart.find(it => Number(it.id) === pid && !it.cupon);
    if(existing) { 
      existing.cantidad = Number(existing.cantidad) + qty;
    } else { 
      // Crear nuevo item SIN propiedad cupon, pero WITH stock info
      const newItem = { id: pid, nombre: productName, precio: productPrice, cantidad: qty };
      if (stock !== null) newItem.stock = stock;
      cart.push(newItem); 
    }
  }

  saveCart();

  // feedback
  if(window.bootstrap && typeof bootstrap.Toast === 'function'){
    const toastEl = document.createElement('div');
    toastEl.className = 'toast align-items-center text-bg-success border-0 position-fixed';
    toastEl.style.right = '16px';
    toastEl.style.bottom = '16px';
    toastEl.setAttribute('role','status');
    const toastMsg = cupon ? 'Cupón canjeado y producto añadido al carrito' : 'Producto añadido al carrito';
    toastEl.innerHTML = `<div class="d-flex"><div class="toast-body">${toastMsg}</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button></div>`;
    document.body.appendChild(toastEl);
    const t = new bootstrap.Toast(toastEl, { delay: 1600 });
    t.show();
    setTimeout(()=> toastEl.remove(), 2000);
  } else {
    console.log('Producto añadido al carrito');
  }

  // Actualizar la vista del carrito si está visible
  showCart();
}

function showCart(){
  const cartItems = document.getElementById('cart-items');
  if(!cartItems) return;
  cartItems.innerHTML = '';
  if(cart.length === 0){ cartItems.innerHTML = '<p>No hay productos en el carrito.</p>'; return; }
  cart.forEach((item, index) => {
    const row = document.createElement('div');
    row.className = 'd-flex align-items-center justify-content-between gap-2 mb-2';
    // compute subtotal for this line
    const unit = parseFloat(String(item.precio).replace(',', '.')) || 0;
    const subtotal = (unit * Number(item.cantidad)) || 0;
    
    // Indicador de cupón aplicado - solo si existe y tiene datos
    let cuponIndicador = '';
    if (item.cupon && item.cupon.codigo && item.cupon.porcentaje) {
      cuponIndicador = `<div class="badge bg-success mt-1"><i class="bi bi-ticket-perforated"></i> Cupón ${item.cupon.codigo} aplicado (${item.cupon.porcentaje}% desc.)</div>`;
    }
    
    // Si tiene cupón, bloquear cantidad en 1 y usar índice
    let quantityInput = '';
    let removeBtn = '';
    if (item.cupon) {
      // Con cupón: cantidad bloqueada en 1, usar índice como identificador
      quantityInput = `<input type="number" min="1" max="1" class="form-control form-control-sm" value="1" disabled>`;
      removeBtn = `<button class="btn btn-sm btn-outline-danger" onclick="removeFromCart(${index})">Eliminar</button>`;
    } else {
      // Sin cupón: cantidad editable normal, usar índice también para evitar conflictos
      quantityInput = `<input type="number" min="1" class="form-control form-control-sm" value="${item.cantidad}" onchange="updateQuantity(${index}, this.value)">`;
      removeBtn = `<button class="btn btn-sm btn-outline-danger" onclick="removeFromCart(${index})">Eliminar</button>`;
    }
    
    row.innerHTML = `
      <div class="flex-grow-1">
        <div class="fw-bold">${item.nombre}</div>
        <div class="small text-muted">Bs. ${Number(unit).toFixed(2)} • <small class="text-muted">Subtotal: Bs. ${Number(subtotal).toFixed(2)}</small></div>
        ${cuponIndicador}
      </div>
      <div style="width:110px">
        ${quantityInput}
      </div>
      <div>
        ${removeBtn}
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

function updateQuantity(index, newQuantity){
  const v = validateQuantity(newQuantity);
  if(!v.valid){ alert(v.message); showCart(); return; }
  
  const it = cart[index];
  if(!it) return;
  
  // Validar stock desde el item del carrito
  let stock = it.stock; 
  
  // Validar contra el stock
  if(stock && !isNaN(stock) && v.value > stock){ 
    alert('La cantidad solicitada supera el stock disponible (' + stock + ')'); 
    showCart(); 
    return; 
  }
  
  it.cantidad = v.value; 
  saveCart(); 
  showCart();
}

function removeFromCart(index){
  // Usar índice para todos los items
  const item = cart[index];
  if (!item) return;
  
  // Si el producto tiene cupón aplicado, mostrar confirmación especial
  if (item.cupon) {
    showRemoveWithCouponModal(index, item);
  } else {
    // Eliminación normal sin cupón
    cart.splice(index, 1);
    saveCart();
    showCart();
  }
}

function showRemoveWithCouponModal(index, item, isCoupon) {
  // Crear modal dinámicamente
  const modalId = 'remove-cupon-modal-' + index;
  let modal = document.getElementById(modalId);
  
  if (!modal) {
    modal = document.createElement('div');
    modal.id = modalId;
    modal.className = 'modal fade';
    modal.setAttribute('tabindex', '-1');
    modal.setAttribute('aria-hidden', 'true');
    modal.innerHTML = `
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-warning">
            <h5 class="modal-title text-dark">
              <i class="bi bi-exclamation-triangle"></i> ¡Atención!
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
          </div>
          <div class="modal-body">
            <p class="mb-3">
              <strong>¿Estás seguro de que deseas eliminar este producto del carrito?</strong>
            </p>
            <div class="alert alert-danger" role="alert">
              <i class="bi bi-info-circle"></i>
              <strong>Este producto tiene un cupón de descuento aplicado.</strong><br>
              Si lo eliminas del carrito, <strong>perderás el cupón utilizado</strong> y no podrás recuperarlo.
            </div>
            <p class="text-muted small mb-0">
              Producto: <strong>${item.nombre}</strong><br>
              Precio con descuento: <strong>Bs. ${Number(item.precio).toFixed(2)}</strong>
            </p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              <i class="bi bi-x-lg"></i> Cancelar
            </button>
            <button type="button" class="btn btn-danger" id="confirm-remove-${index}">
              <i class="bi bi-trash"></i> Sí, estoy seguro
            </button>
          </div>
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }

  // Agregar listener al botón de confirmación
  const confirmBtn = document.getElementById('confirm-remove-' + index);
  confirmBtn.onclick = function() {
    // Usar índice para remover
    cart.splice(index, 1);
    saveCart();
    showCart();
    
    // Cerrar modal
    const bsModal = bootstrap.Modal.getInstance(modal);
    if (bsModal) bsModal.hide();
    modal.remove();
  };

  // Mostrar modal
  const bsModal = new bootstrap.Modal(modal);
  bsModal.show();
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

