document.addEventListener('DOMContentLoaded', function () {

    
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const nav = document.querySelector('.nav');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function () {
            nav.classList.toggle('open');
            this.textContent = nav.classList.contains('open') ? '✕' : '☰';
        });
    }

    
    const sliderTrack = document.querySelector('.slider-track');
    const slides = document.querySelectorAll('.slider-slide');
    const prevBtn = document.querySelector('.slider-btn-prev');
    const nextBtn = document.querySelector('.slider-btn-next');
    const dotsContainer = document.querySelector('.slider-dots');
    let currentSlide = 0;
    let slideInterval;

    function updateSlider() {
        if (!sliderTrack || slides.length === 0) return;
        sliderTrack.style.transform = `translateX(-${currentSlide * 100}%)`;

        document.querySelectorAll('.slider-dot').forEach((dot, index) => {
            dot.classList.toggle('active', index === currentSlide);
        });
    }

    function nextSlide() {
        if (slides.length === 0) return;
        currentSlide = (currentSlide + 1) % slides.length;
        updateSlider();
    }

    function prevSlide() {
        if (slides.length === 0) return;
        currentSlide = (currentSlide - 1 + slides.length) % slides.length;
        updateSlider();
    }

    function startAutoSlide() {
        slideInterval = setInterval(nextSlide, 5000);
    }

    function stopAutoSlide() {
        clearInterval(slideInterval);
    }

    if (prevBtn) prevBtn.addEventListener('click', function () {
        prevSlide();
        stopAutoSlide();
        startAutoSlide();
    });

    if (nextBtn) nextBtn.addEventListener('click', function () {
        nextSlide();
        stopAutoSlide();
        startAutoSlide();
    });

    if (dotsContainer && slides.length > 0) {
        slides.forEach((_, index) => {
            const dot = document.createElement('button');
            dot.classList.add('slider-dot');
            if (index === 0) dot.classList.add('active');
            dot.addEventListener('click', function () {
                currentSlide = index;
                updateSlider();
                stopAutoSlide();
                startAutoSlide();
            });
            dotsContainer.appendChild(dot);
        });
    }

    if (slides.length > 1) {
        startAutoSlide();
    }

    
    document.querySelectorAll('.btn-add-cart').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            e.preventDefault();
            e.stopPropagation();

            const productId = this.dataset.productId;
            const csrfToken = getCSRFToken();

            if (!csrfToken) {
                window.location.href = '/login/';
                return;
            }

            const originalText = this.innerHTML;
            this.innerHTML = '<span class="loading-spinner"></span>';
            this.disabled = true;

            fetch('/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: 1,
                }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.innerHTML = '✓ Добавлено';
                        this.classList.add('added');
                        updateCartBadge(data.cart_count);
                        showToast(data.message);

                        setTimeout(() => {
                            this.innerHTML = originalText;
                            this.classList.remove('added');
                            this.disabled = false;
                        }, 2000);
                    } else {
                        this.innerHTML = originalText;
                        this.disabled = false;
                        showToast(data.message || 'Недостаточно товара в наличии', 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.innerHTML = originalText;
                    this.disabled = false;
                    showToast('Ошибка. Войдите в аккаунт.', 'error');
                });
        });
    });

    
    document.querySelectorAll('.cart-qty-btn').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const itemId = this.dataset.itemId;
            const action = this.dataset.action;
            const input = this.parentElement.querySelector('.cart-qty-input');
            let quantity = parseInt(input.value);
            const maxQuantity = parseInt(input.dataset.max) || Infinity;

            if (action === 'increase') {
                if (quantity >= maxQuantity) {
                    showToast(`Максимальное количество: ${maxQuantity} шт.`, 'error');
                    return;
                }
                quantity++;
            } else if (action === 'decrease') {
                quantity--;
            }

            if (quantity <= 0) {
                removeCartItem(itemId);
                return;
            }

            input.value = quantity;

            fetch('/cart/update/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({
                    item_id: itemId,
                    quantity: quantity,
                }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateCartBadge(data.cart_count);
                        const totalEl = document.querySelector(`#item-total-${itemId}`);
                        if (totalEl) {
                            totalEl.textContent = formatPrice(data.item_total);
                        }
                        const cartTotalEl = document.querySelector('#cart-total');
                        if (cartTotalEl) {
                            cartTotalEl.textContent = formatPrice(data.cart_total);
                        }
                    } else {
                        
                        if (action === 'increase') {
                            input.value = quantity - 1;
                        } else {
                            input.value = quantity + 1;
                        }
                        showToast(data.message || 'Недостаточно товара в наличии', 'error');
                    }
                });
        });
    });

    
    document.querySelectorAll('.cart-item-remove').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const itemId = this.dataset.itemId;
            removeCartItem(itemId);
        });
    });

    function removeCartItem(itemId) {
        fetch('/cart/remove/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({item_id: itemId}),
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const itemEl = document.querySelector(`#cart-item-${itemId}`);
                    if (itemEl) {
                        itemEl.style.animation = 'slideOut 0.3s ease';
                        setTimeout(() => {
                            itemEl.remove();
                            updateCartBadge(data.cart_count);
                            const cartTotalEl = document.querySelector('#cart-total');
                            if (cartTotalEl) {
                                cartTotalEl.textContent = formatPrice(data.cart_total);
                            }
                            if (data.cart_count === 0) {
                                location.reload();
                            }
                        }, 300);
                    }
                    showToast(data.message);
                }
            });
    }

    
    const qtyMinus = document.querySelector('.qty-minus');
    const qtyPlus = document.querySelector('.qty-plus');
    const qtyInput = document.querySelector('.qty-input');

    if (qtyMinus) {
        qtyMinus.addEventListener('click', function () {
            let val = parseInt(qtyInput.value);
            if (val > 1) qtyInput.value = val - 1;
        });
    }

    if (qtyPlus) {
        qtyPlus.addEventListener('click', function () {
            let val = parseInt(qtyInput.value);
            const maxVal = parseInt(qtyInput.getAttribute('max')) || Infinity;
            if (val < maxVal) {
                qtyInput.value = val + 1;
            } else {
                showToast(`Максимальное количество: ${maxVal} шт.`, 'error');
            }
        });
    }

    // Запрещаем ручной ввод больше максимума
    if (qtyInput) {
        qtyInput.addEventListener('change', function () {
            const maxVal = parseInt(this.getAttribute('max')) || Infinity;
            const minVal = parseInt(this.getAttribute('min')) || 1;
            let val = parseInt(this.value) || 1;
            if (val > maxVal) {
                this.value = maxVal;
                showToast(`Максимальное количество: ${maxVal} шт.`, 'error');
            } else if (val < minVal) {
                this.value = minVal;
            }
        });
    }

    
    const addToCartDetail = document.querySelector('.btn-add-cart-detail');
    if (addToCartDetail) {
        addToCartDetail.addEventListener('click', function () {
            const productId = this.dataset.productId;
            const quantity = parseInt(document.querySelector('.qty-input').value) || 1;
            const maxStock = parseInt(document.querySelector('.qty-input').getAttribute('max')) || Infinity;
            const csrfToken = getCSRFToken();

            if (quantity > maxStock) {
                showToast(`Максимальное количество: ${maxStock} шт.`, 'error');
                return;
            }

            const originalText = this.innerHTML;
            this.innerHTML = '<span class="loading-spinner"></span> Добавление...';
            this.disabled = true;

            fetch('/cart/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                body: JSON.stringify({
                    product_id: productId,
                    quantity: quantity,
                }),
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        this.innerHTML = '✓ Добавлено в корзину';
                        this.classList.add('added');
                        updateCartBadge(data.cart_count);
                        showToast(data.message);

                        setTimeout(() => {
                            this.innerHTML = originalText;
                            this.classList.remove('added');
                            this.disabled = false;
                        }, 2000);
                    } else {
                        this.innerHTML = originalText;
                        this.disabled = false;
                        showToast(data.message || 'Недостаточно товара в наличии', 'error');
                    }
                })
                .catch(error => {
                    this.innerHTML = originalText;
                    this.disabled = false;
                    showToast('Ошибка. Войдите в аккаунт.', 'error');
                });
        });
    }

    
    document.querySelectorAll('.product-thumbnail').forEach(function (thumb) {
        thumb.addEventListener('click', function () {
            const imgSrc = this.querySelector('img').src;
            const mainImage = document.querySelector('.product-main-image img');
            if (mainImage) {
                mainImage.src = imgSrc;
            }
            document.querySelectorAll('.product-thumbnail').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });

    
    document.querySelectorAll('.profile-tab').forEach(function (tab) {
        tab.addEventListener('click', function () {
            const target = this.dataset.tab;

            document.querySelectorAll('.profile-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.profile-section').forEach(s => s.classList.remove('active'));

            this.classList.add('active');
            const section = document.getElementById(target);
            if (section) section.classList.add('active');
        });
    });

    
    const sortSelect = document.querySelector('.sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function () {
            const url = new URL(window.location);
            url.searchParams.set('sort', this.value);
            window.location.href = url.toString();
        });
    }

    
    const priceFilterBtn = document.querySelector('.price-filter-btn');
    if (priceFilterBtn) {
        priceFilterBtn.addEventListener('click', function () {
            const url = new URL(window.location);
            const minPrice = document.querySelector('#min-price').value;
            const maxPrice = document.querySelector('#max-price').value;

            if (minPrice) url.searchParams.set('min_price', minPrice);
            else url.searchParams.delete('min_price');

            if (maxPrice) url.searchParams.set('max_price', maxPrice);
            else url.searchParams.delete('max_price');

            window.location.href = url.toString();
        });
    }

    
    document.querySelectorAll('.message').forEach(function (msg) {
        setTimeout(() => {
            msg.style.opacity = '0';
            msg.style.transform = 'translateX(100%)';
            setTimeout(() => msg.remove(), 300);
        }, 4000);
    });

    
    function getCSRFToken() {
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : null;
    }

    function updateCartBadge(count) {
        const badges = document.querySelectorAll('.cart-badge');
        badges.forEach(badge => {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'flex' : 'none';
        });
    }

    function formatPrice(price) {
        return new Intl.NumberFormat('ru-RU').format(price) + ' ₽';
    }

    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.textContent = message;
        toast.style.borderColor = type === 'error' ? 'var(--danger)' : 'var(--primary)';
        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
});
