// Obtiene el carrito de localStorage (si existe)
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Función para agregar productos al carrito
function addToCart(productId) {
  // Simulación de obtener el producto por su ID
  const product = {
    id: productId,
    nombre: "Producto " + productId, // Aquí deberías obtener el nombre real del producto
    precio: "15.00", // Igual con el precio
    cantidad: 1
  };

  // Verifica si el producto ya está en el carrito
  const existingProduct = cart.find(item => item.id === productId);
  if (existingProduct) {
    existingProduct.cantidad += 1; // Si ya está, incrementa la cantidad
  } else {
    cart.push(product); // Si no está, lo agrega
  }

  // Guarda el carrito en localStorage
  localStorage.setItem('cart', JSON.stringify(cart));

  // Alerta de que el producto fue agregado
  alert("Producto añadido al carrito");
  console.log(cart);  // Esto solo para depuración, muestra el contenido del carrito
}

// Función para mostrar el carrito
function showCart() {
  const cartItems = document.getElementById("cart-items");
  cartItems.innerHTML = ''; // Limpiar el contenido actual del carrito

  if (cart.length === 0) {
    cartItems.innerHTML = '<p>No hay productos en el carrito.</p>';
  } else {
    cart.forEach(item => {
      const productDiv = document.createElement('div');
      productDiv.classList.add('cart-item');
      productDiv.innerHTML = `
        <p>${item.nombre} - Bs. ${item.precio} x ${item.cantidad}</p>
        <button onclick="removeFromCart(${item.id})">Eliminar</button>
      `;
      cartItems.appendChild(productDiv);
    });
  }
}

// Función para eliminar productos del carrito
function removeFromCart(productId) {
  cart = cart.filter(item => item.id !== productId); // Elimina el producto por ID
  localStorage.setItem('cart', JSON.stringify(cart)); // Guarda los cambios
  showCart(); // Actualiza el carrito
}

// Mostrar carrito cuando se hace clic en el icono del carrito
document.getElementById('cart-icon').addEventListener('click', function() {
  showCart(); // Mostrar el contenido del carrito
  document.getElementById('cart-modal').style.display = 'block'; // Abre el modal del carrito
});

// Función para cerrar el carrito
document.getElementById('close-cart').addEventListener('click', function() {
  document.getElementById('cart-modal').style.display = 'none'; // Cierra el modal
});
