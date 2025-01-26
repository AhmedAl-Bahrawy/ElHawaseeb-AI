document.addEventListener("DOMContentLoaded", function() {
    function adjustNavbar() {
        const navbar = document.querySelector('.navbar');
        if (window.innerWidth <= 768) {
            navbar.classList.add('mobile');
        } else {
            navbar.classList.remove('mobile');
        }
    }

    adjustNavbar();

    window.addEventListener('resize', function() {
        adjustNavbar();
    });
});

document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        document.querySelector(".loading-spinner").style.display = 'none';
    }, 3000); // Hide spinner after 3 seconds
});

window.addEventListener("load", function() {
    document.querySelector(".overlay").style.display = 'none'; // Hide overlay and spinner
    const buttons = document.querySelectorAll(".disable-button");
    buttons.forEach(button => button.disabled = false); // Enable all buttons
});

// Disable buttons while loading
document.addEventListener("DOMContentLoaded", function() {
    const buttons = document.querySelectorAll(".disable-button");
    buttons.forEach(button => button.disabled = true); // Disable all buttons
});

document.querySelector('.file-upload-input').addEventListener('change', function(e) {
    var fileName = e.target.files[0].name;
    var nextSibling = e.target.nextElementSibling;
    nextSibling.innerText = fileName;
});
document.querySelector('.file-upload-input2').addEventListener('change', function(e) {
    var fileName = e.target.files[0].name;
    var nextSibling = e.target.nextElementSibling;
    nextSibling.innerText = fileName;
});

document.addEventListener('DOMContentLoaded', function() {
    const scrollAmount = 300; // مقدار التمرير في كل مرة
    const carousels = document.querySelectorAll('.product-carousel');

    carousels.forEach(carousel => {
        const prevButton = carousel.querySelector('.prev');
        const nextButton = carousel.querySelector('.next');
        const productList = carousel.querySelector('.product-list');
        const productCards = Array.from(productList.children);
        const productCardWidth = productCards[0].offsetWidth;
        const visibleCount = Math.floor(productList.offsetWidth / productCardWidth);
        let currentIndex = 0;

        function updateCarousel() {
            const newTransformX = -currentIndex * productCardWidth;
            productList.style.transform = `translateX(${newTransformX}px)`;
        }

        prevButton.addEventListener('click', function() {
            if (currentIndex > 0) {
                currentIndex--;
                updateCarousel();
            }
        });

        nextButton.addEventListener('click', function() {
            if (currentIndex < productCards.length - visibleCount) {
                currentIndex++;
                updateCarousel();
            }
        });

        // Initialize carousel
        updateCarousel();
    });
});

// التعامل مع إظهار وإخفاء حقول التخفيض والسعر النهائي
var discountField = document.getElementById("discount_field");
var finalPriceField = document.getElementById("final_price_field");
var isDiscountCheckbox = document.getElementById("is_discount_checkbox");
var discountInput = document.getElementById("discount_input");
var finalPriceInput = document.getElementById("final_price_input");
var finalPriceHidden = document.getElementById("final_price_hidden"); 
var priceInput = document.getElementById("price_input");

// دالة لحساب السعر النهائي
function calculateFinalPrice() {
    var originalPrice = parseFloat(priceInput.value) || 0; // الحصول على السعر الأصلي
    var discount = parseFloat(discountInput.value) || 0; // الحصول على قيمة الخصم
    if (discount < 0) discount = 0; // ضمان أن الخصم لا يكون أقل من 0%
    if (discount > 100) discount = 100; // ضمان أن الخصم لا يتجاوز 100%
    var finalPrice = originalPrice - (originalPrice * (discount / 100)); // حساب السعر النهائي بعد الخصم
    finalPriceInput.value = finalPrice.toFixed(2); // عرض السعر النهائي في الحقل المرئي
    finalPriceHidden.value = finalPrice.toFixed(2); // تخزين السعر النهائي في الحقل المخفي لإرساله إلى Flask
}

// التحقق من حالة is_discount عند التغيير
isDiscountCheckbox.addEventListener("change", function() {
    if (this.checked) {
        discountField.style.display = "block"; // عرض حقل الخصم إذا كانت is_discount محددة
        finalPriceField.style.display = "block"; // عرض حقل السعر النهائي إذا كانت is_discount محددة
        calculateFinalPrice(); // حساب السعر النهائي عند تفعيل التخفيض
    } else {
        discountField.style.display = "none"; // إخفاء حقل الخصم إذا لم تكن is_discount محددة
        finalPriceField.style.display = "none"; // إخفاء حقل السعر النهائي إذا لم تكن is_discount محددة
        finalPriceInput.value = "0"; // تعيين القيمة إلى 0 بدلاً من سلسلة فارغة
        finalPriceHidden.value = "0"; // تعيين القيمة المخفية إلى 0
    }
});

// تحديث السعر النهائي عند إدخال قيم في حقل الخصم
discountInput.addEventListener("input", function() {
    calculateFinalPrice(); // حساب السعر النهائي عند تغيير قيمة الخصم
});

// تحديث السعر النهائي عند إدخال قيم في حقل السعر
priceInput.addEventListener("input", function() {
    calculateFinalPrice(); // حساب السعر النهائي عند تغيير قيمة السعر
});

// التحقق عند تحميل الصفحة إذا كان الحقل محدد بالفعل
window.onload = function() {
    if (isDiscountCheckbox.checked) {
        discountField.style.display = "block"; // عرض حقل الخصم إذا كانت is_discount محددة
        finalPriceField.style.display = "block"; // عرض حقل السعر النهائي إذا كانت is_discount محددة
        calculateFinalPrice(); // حساب السعر النهائي عند تحميل الصفحة
    }
};

