document.addEventListener('DOMContentLoaded', function() {
  // Add to cart functionality
  const addToCartButtons = document.querySelectorAll('.add-to-cart');
  addToCartButtons.forEach(button => {
    button.addEventListener('click', function() {
      const itemId = this.getAttribute('data-item-id');
      const itemName = this.getAttribute('data-item-name');
      const itemPrice = parseFloat(this.getAttribute('data-item-price'));
      
      // Get quantity from the input field
      const quantityInput = document.getElementById(`quantity-${itemId}`);
      let quantity = 1;
      
      if (quantityInput) {
        quantity = parseInt(quantityInput.value);
      }
      
      if (quantity < 1) {
        quantity = 1;
      }
      
      // Add to cart via API
      fetch('/api/add-to-cart', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          item_id: itemId,
          quantity: quantity
        })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          // Show success message
          const toast = document.createElement('div');
          toast.className = 'position-fixed bottom-0 end-0 p-3';
          toast.style.zIndex = '11';
          toast.innerHTML = `
            <div class="toast show" role="alert" aria-live="assertive" aria-atomic="true">
              <div class="toast-header">
                <strong class="me-auto">Added to Cart</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
              </div>
              <div class="toast-body">
                ${quantity} × ${itemName} added to your cart.
              </div>
            </div>
          `;
          document.body.appendChild(toast);
          
          // Auto dismiss the toast after 3 seconds
          setTimeout(() => {
            toast.remove();
          }, 3000);
          
          // Update cart badge
          updateCartBadge(data.cart_count);
        } else {
          alert(data.message);
        }
      })
      .catch(error => {
        console.error('Error adding to cart:', error);
        alert('Failed to add item to cart. Please try again.');
      });
    });
  });
  
  // Cart page functionality
  if (document.getElementById('cart-items')) {
    // Increase quantity
    const increaseButtons = document.querySelectorAll('.increase-quantity');
    increaseButtons.forEach(button => {
      button.addEventListener('click', function() {
        const itemId = this.getAttribute('data-item-id');
        const quantityInput = document.querySelector(`.item-quantity[data-item-id="${itemId}"]`);
        let quantity = parseInt(quantityInput.value) + 1;
        updateCartItemQuantity(itemId, quantity);
      });
    });
    
    // Decrease quantity
    const decreaseButtons = document.querySelectorAll('.decrease-quantity');
    decreaseButtons.forEach(button => {
      button.addEventListener('click', function() {
        const itemId = this.getAttribute('data-item-id');
        const quantityInput = document.querySelector(`.item-quantity[data-item-id="${itemId}"]`);
        let quantity = parseInt(quantityInput.value) - 1;
        if (quantity < 1) quantity = 1;
        updateCartItemQuantity(itemId, quantity);
      });
    });
    
    // Remove item
    const removeButtons = document.querySelectorAll('.remove-item');
    removeButtons.forEach(button => {
      button.addEventListener('click', function() {
        const itemId = this.getAttribute('data-item-id');
        updateCartItemQuantity(itemId, 0);
      });
    });
    
    // Clear cart
    const clearCartButton = document.getElementById('clear-cart');
    if (clearCartButton) {
      clearCartButton.addEventListener('click', function() {
        if (confirm('Are you sure you want to clear your cart?')) {
          fetch('/api/clear-cart', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            }
          })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              window.location.reload();
            } else {
              alert(data.message);
            }
          })
          .catch(error => {
            console.error('Error clearing cart:', error);
            alert('Failed to clear cart. Please try again.');
          });
        }
      });
    }
  }
});

// Update cart item quantity
function updateCartItemQuantity(itemId, quantity) {
  fetch('/api/update-cart', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      item_id: itemId,
      quantity: quantity
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      if (quantity <= 0) {
        // Remove item row from table
        const row = document.getElementById(`cart-row-${itemId}`);
        if (row) {
          row.remove();
        }
      } else {
        // Update quantity in input field
        const quantityInput = document.querySelector(`.item-quantity[data-item-id="${itemId}"]`);
        if (quantityInput) {
          quantityInput.value = quantity;
        }
        
        // Update subtotal
        const subtotalElement = document.querySelector(`.item-subtotal[data-item-id="${itemId}"]`);
        if (subtotalElement) {
          const price = parseFloat(subtotalElement.getAttribute('data-price'));
          subtotalElement.textContent = `$${(price * quantity).toFixed(2)}`;
        }
      }
      
      // Update total
      const cartSubtotal = document.getElementById('cart-subtotal');
      const cartTotal = document.getElementById('cart-total');
      if (cartSubtotal && cartTotal) {
        cartSubtotal.textContent = `$${data.total.toFixed(2)}`;
        cartTotal.textContent = `$${data.total.toFixed(2)}`;
      }
      
      // Update cart badge
      updateCartBadge(data.cart_count);
      
      // If cart is empty, reload the page to show empty cart message
      if (data.cart_count === 0) {
        window.location.reload();
      }
    } else {
      alert(data.message);
    }
  })
  .catch(error => {
    console.error('Error updating cart:', error);
    alert('Failed to update cart. Please try again.');
  });
}
