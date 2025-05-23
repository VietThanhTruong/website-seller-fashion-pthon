const signUp = document.querySelector("#signUp");
const signIn = document.querySelector("#signIn");
const passwordIcon = document.querySelectorAll(".password__icon");
const authPassword = document.querySelectorAll(".auth__password");

signUp.addEventListener("click", () => {
  document.querySelector(".login__form").classList.remove("active");
  document.querySelector(".register__form").classList.add("active");
  document.querySelector(".ball").classList.add("register");
  document.querySelector(".ball").classList.remove("login");
});

signIn.addEventListener("click", () => {
  document.querySelector(".login__form").classList.add("active");
  document.querySelector(".register__form").classList.remove("active");
  document.querySelector(".ball").classList.add("login");
  document.querySelector(".ball").classList.remove("register");
});

for (var i = 0; i < passwordIcon.length; ++i) {
  passwordIcon[i].addEventListener("click", (i) => {
    const lastArray = i.target.classList.length - 1;
    if (i.target.classList[lastArray] == "bi-eye-slash") {
      i.target.classList.remove("bi-eye-slash");
      i.target.classList.add("bi-eye");
      i.currentTarget.parentNode.querySelector("input").type = "text";
    } else {
      i.target.classList.add("bi-eye-slash");
      i.target.classList.remove("bi-eye");
      i.currentTarget.parentNode.querySelector("input").type = "password";
    }
  });
}

$(document).ready(function () {
  $("#loginForm").on("submit", function (e) {
    e.preventDefault();

    
    var $form = $(this);
    var csrf_token = $form.find('input[name="csrfmiddlewaretoken"]').val();
    $.ajax({
      url: '/vi/api/login/',
      type: "POST",
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrf_token
    },
      data: $form.serialize(),
      success: function (response) {
        if (response.success) {
          alert("Đăng nhập thành công!");
          setTimeout(function () {
            window.location.href = response.redirect_url || "/";
          }, 1000);
        } else {
          alert("Lỗi: " + response.error);
        }
      },
      error: function (xhr) {
        alert("Đã xảy ra lỗi. Vui lòng thử lại.");
      },
    });
  });
});

$(document).ready(function () {
  $("#registerForm").on("submit", function (e) {
    e.preventDefault();

    var $form = $(this);
    var csrf_token = $form.find('input[name="csrfmiddlewaretoken"]').val();

    $.ajax({
      url: '/vi/api/register/',
      type: "POST",
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrf_token
      },
      data: $form.serialize(),
      success: function (response) {
        if (response.success) {
          alert("Đăng ký thành công!");
          window.location.href = response.redirect_url || "/login/";
        } else {
          alert("Lỗi: " + response.error);
        }
      },
      error: function (xhr) {
        alert("Đã xảy ra lỗi. Vui lòng thử lại.");
      },
    });
  });
});
