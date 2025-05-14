
document.getElementById("add-to-cart-form").addEventListener("submit", function(e) {
    e.preventDefault(); 

    const form = e.target;
    const formData = new FormData(form);
    const csrfToken = form.querySelector('[name=csrfmiddlewaretoken]').value;
    const actionUrl = form.action;

    fetch(actionUrl, {
        method: "POST",
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const msgBox = document.getElementById("cart-message");
        if (data.success) {
            msgBox.textContent = "✅ Sản phẩm đã được thêm vào giỏ hàng!";
            msgBox.classList.remove("text-danger");
            msgBox.classList.add("text-success");
        } else {
            msgBox.textContent = "❌ Thêm vào giỏ hàng thất bại.";
            msgBox.classList.remove("text-success");
            msgBox.classList.add("text-danger");
        }
    })
    .catch(error => {
        console.error("Lỗi khi gửi yêu cầu:", error);
        const msgBox = document.getElementById("cart-message");
        msgBox.textContent = "⚠️ Đã xảy ra lỗi.";
        msgBox.classList.remove("text-success");
        msgBox.classList.add("text-danger");
    });
});
