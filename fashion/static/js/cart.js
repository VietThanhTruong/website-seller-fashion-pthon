function formatCurrency(number) {
  return new Intl.NumberFormat("en-US").format(number);
}

function parseCurrency(currencyStr) {
  return Number(currencyStr.replace(/,/g, ""));
}

document.addEventListener("DOMContentLoaded", () => {
  const checkboxes = document.querySelectorAll(".cart-checkbox");
  const totalDisplay = document.getElementById("cart-total");
  const checkoutForm = document.getElementById("checkout-form");
  const selectedItemsInput = document.getElementById("selected-items-input");
  const selectAll = document.getElementById("select-all-checkbox");

  const updateTotal = () => {
    let total = 0;
    checkboxes.forEach((checkbox) => {
      if (checkbox.checked) {
        total += parseInt(checkbox.dataset.price);
      }
    });
    totalDisplay.textContent = formatCurrency(total) + " VNĐ";
  };

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
            document.querySelector(
                `.cart-checkbox[data-id="${itemId}"]`
              ).checked = false;
              
            const itemRow = document.querySelector(`#cart-item-${itemId}`);
            if (itemRow) {
              itemRow.remove();
            }
            updateTotal();

            alert(data.message);
          } else {
            alert(data.error || "Lỗi khi xóa sản phẩm.");
          }
        })
        .catch(() => alert("Có lỗi xảy ra, vui lòng thử lại."));
    });
  });

  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", () => {
      updateTotal();

      const allChecked = Array.from(checkboxes).every((cb) => cb.checked);
      selectAll.checked = allChecked;
    });
  });

  if (selectAll) {
    selectAll.addEventListener("change", () => {
      checkboxes.forEach((checkbox) => {
        checkbox.checked = selectAll.checked;
      });
      updateTotal();
    });
  }

  if (checkoutForm) {
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
  }

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

              const itemCheckbox = document.querySelector(
                `.cart-checkbox[data-id="${itemId}"]`
              );
              if (itemCheckbox) {
                itemCheckbox.dataset.price = parseCurrency(data.item_total);
              }

              const itemTotalElement = document.getElementById(
                `item-total-${itemId}`
              );
              if (itemTotalElement) {
                itemTotalElement.textContent = data.item_total + "đ";
              }

              if (itemCheckbox && itemCheckbox.checked) {
                updateTotal();
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
