// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
  // Enable Bootstrap tooltips
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Enable Bootstrap popovers
  var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
  var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
    return new bootstrap.Popover(popoverTriggerEl);
  });

  // Auto-dismiss alerts after 5 seconds
  setTimeout(function() {
    var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
      var bsAlert = new bootstrap.Alert(alert);
      bsAlert.close();
    });
  }, 5000);
});

// Update cart badge count
function updateCartBadge(count) {
  const cartBadge = document.getElementById('cart-badge');
  if (cartBadge) {
    cartBadge.textContent = count;
    if (count > 0) {
      cartBadge.classList.remove('d-none');
    } else {
      cartBadge.classList.add('d-none');
    }
  }
}
