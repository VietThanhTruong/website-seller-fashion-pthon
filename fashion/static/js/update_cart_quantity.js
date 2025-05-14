document.querySelectorAll('.cart-update-form').forEach(form => {
  const buttons = form.querySelectorAll('button[name="action"]');
  const csrfToken = form.querySelector('input[name="csrfmiddlewaretoken"]').value;
  const itemId = form.dataset.id;

  buttons.forEach(button => {
    button.addEventListener('click', function (e) {
      e.preventDefault();
      const actionType = this.value;
      const actionUrl = form.getAttribute('action');

      fetch(actionUrl, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Accept': 'application/json',
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ action: actionType })
      })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            document.getElementById(`quantity-${itemId}`).textContent = data.quantity;

            const itemTotalElement = document.getElementById(`item-total-${itemId}`);
            if (itemTotalElement) {
              itemTotalElement.textContent = formatCurrency(data.item_total) + 'đ';
            }

            const cartTotalElement = document.getElementById('cart-total');
            if (cartTotalElement) {
              cartTotalElement.textContent = formatCurrency(data.cart_total) + ' đ';
            }
          } else {
            alert(data.error || 'Cập nhật thất bại');
          }
        })
        .catch(error => {
          console.error('Lỗi:', error);
          alert('Đã xảy ra lỗi.');
        });
    });
  });
});

function formatCurrency(number) {
  return number.toLocaleString('vi-VN');
}
