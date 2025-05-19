function formatCurrency(number) {
  return number.toLocaleString("vi-VN");
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".delete-cart-item").forEach((form) => {
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      const itemId = this.dataset.itemId;
      const url = this.getAttribute("action");
      const csrfToken = this.querySelector(
        'input[name="csrfmiddlewaretoken"]'
      ).value;

      if (!confirm("Bạn có chắc muốn xóa sản phẩm này khỏi giỏ hàng?")) {
        return;
      }

      fetch(url, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrfToken,
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        credentials: "same-origin",
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            const itemRow = document.querySelector(`#cart-item-${itemId}`);
            if (itemRow) {
              itemRow.remove();
            }

            const cartTotalElement = document.getElementById("cart-total");
            if (cartTotalElement && data.cart_total !== undefined) {
              cartTotalElement.textContent =
                formatCurrency(data.cart_total) + " VNĐ";
            }

            alert(data.message);
          } else {
            alert(data.error || "Lỗi khi xóa sản phẩm.");
          }
        })
        .catch(() => alert("Có lỗi xảy ra, vui lòng thử lại."));
    });
  });

  document.querySelectorAll(".cart-update-form").forEach((form) => {
    const buttons = form.querySelectorAll('button[name="action"]');
    const csrfToken = form.querySelector(
      'input[name="csrfmiddlewaretoken"]'
    ).value;
    const itemId = form.dataset.id;

    buttons.forEach((button) => {
      button.addEventListener("click", function (e) {
        e.preventDefault();
        const actionType = this.value;
        const actionUrl = form.getAttribute("action");

        fetch(actionUrl, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrfToken,
            Accept: "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
          },
          body: new URLSearchParams({ action: actionType }),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.success) {
              document.getElementById(`quantity-${itemId}`).textContent =
                data.quantity;

              const itemTotalElement = document.getElementById(
                `item-total-${itemId}`
              );
              if (itemTotalElement) {
                itemTotalElement.textContent =
                  formatCurrency(data.item_total) + " VNĐ";
              }

              const cartTotalElement = document.getElementById("cart-total");
              if (cartTotalElement) {
                cartTotalElement.textContent =
                  formatCurrency(data.cart_total) + " VNĐ";
              }
            } else {
              alert(data.error || "Cập nhật thất bại");
            }
          })
          .catch((error) => {
            console.error("Lỗi:", error);
            alert("Đã xảy ra lỗi.");
          });
      });
    });
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const checkboxes = document.querySelectorAll(".cart-checkbox");
  const totalDisplay = document.getElementById("cart-total");

  const formatCurrency = (number) => {
    return new Intl.NumberFormat("vi-VN").format(number) + " VNĐ";
  };

  const updateTotal = () => {
    let total = 0;
    checkboxes.forEach((checkbox) => {
      if (checkbox.checked) {
        total += parseInt(checkbox.dataset.price);
      }
    });
    totalDisplay.textContent = formatCurrency(total);
  };

  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", updateTotal);
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const checkboxes = document.querySelectorAll(".cart-checkbox");
  const totalDisplay = document.getElementById("cart-total");
  const checkoutForm = document.getElementById("checkout-form");
  const selectedItemsInput = document.getElementById("selected-items-input");

  const formatCurrency = (number) => {
    return new Intl.NumberFormat("vi-VN").format(number) + " VNĐ";
  };

  const updateTotal = () => {
    let total = 0;
    checkboxes.forEach((checkbox) => {
      if (checkbox.checked) {
        total += parseInt(checkbox.dataset.price);
      }
    });
    totalDisplay.textContent = formatCurrency(total);
  };

  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", updateTotal);
  });

  checkoutForm.addEventListener("submit", function (e) {
    const selectedIds = [];
    checkboxes.forEach((checkbox) => {
      if (checkbox.checked) {
        selectedIds.push(checkbox.dataset.id);
      }
    });

    if (selectedIds.length === 0) {
      e.preventDefault();
      alert("Vui lòng chọn ít nhất một sản phẩm để thanh toán.");
    } else {
      selectedItemsInput.value = selectedIds.join(",");
    }
  });
});
