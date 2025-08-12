// Flexor Website - JavaScript Funcionalidades
document.addEventListener('DOMContentLoaded', function() {
    
    // Navegação móvel
    initMobileNavigation();
    
    // Scroll suave e efeitos
    initSmoothScrolling();
    
    // Animações ao scroll
    initScrollAnimations();
    
    // Formulário de contato
    initContactForm();
    
    // Header fixo com efeito de scroll
    initHeaderScrollEffect();
    
    // Dropdown menus
    initDropdownMenus();
});

// Navegação móvel
function initMobileNavigation() {
    const mobileToggle = document.querySelector('.mobile-menu-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (mobileToggle && navMenu) {
        mobileToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            mobileToggle.classList.toggle('active');
            document.body.classList.toggle('menu-open');
        });
        
        // Fechar menu ao clicar em um link
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navMenu.classList.remove('active');
                mobileToggle.classList.remove('active');
                document.body.classList.remove('menu-open');
            });
        });
        
        // Fechar menu ao clicar fora
        document.addEventListener('click', function(e) {
            if (!mobileToggle.contains(e.target) && !navMenu.contains(e.target)) {
                navMenu.classList.remove('active');
                mobileToggle.classList.remove('active');
                document.body.classList.remove('menu-open');
            }
        });
    }
}

// Scroll suave para links internos
function initSmoothScrolling() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                const headerHeight = document.querySelector('.header').offsetHeight;
                const targetPosition = targetElement.offsetTop - headerHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Animações ao fazer scroll
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                
                // Animação especial para estatísticas
                if (entry.target.classList.contains('stat-item')) {
                    animateCounter(entry.target);
                }
            }
        });
    }, observerOptions);
    
    // Observar elementos para animação
    const animateElements = document.querySelectorAll('.product-card, .quality-item, .sustainability-card, .about-text, .about-image, .stat-item, .contact-item');
    
    animateElements.forEach(element => {
        observer.observe(element);
    });
}

// Animação de contador para estatísticas
function animateCounter(element) {
    const counter = element.querySelector('h3');
    if (!counter) return;
    
    const target = parseInt(counter.textContent.replace(/\D/g, ''));
    if (isNaN(target)) return;
    
    const duration = 2000; // 2 segundos
    const increment = target / (duration / 16); // 60fps
    let current = 0;
    
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        
        const suffix = counter.textContent.replace(/[\d]/g, '');
        counter.textContent = Math.floor(current) + suffix;
    }, 16);
}

// Formulário de contato
function initContactForm() {
    const form = document.querySelector('.contact-form');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validação básica
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            
            if (validateForm(data)) {
                submitForm(data);
            }
        });
        
        // Validação em tempo real
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    }
}

// Validação do formulário
function validateForm(data) {
    let isValid = true;
    
    // Validar nome
    if (!data.name || data.name.trim().length < 2) {
        showFieldError('name', 'Nome deve ter pelo menos 2 caracteres');
        isValid = false;
    }
    
    // Validar email
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!data.email || !emailRegex.test(data.email)) {
        showFieldError('email', 'E-mail inválido');
        isValid = false;
    }
    
    // Validar assunto
    if (!data.subject) {
        showFieldError('subject', 'Selecione um assunto');
        isValid = false;
    }
    
    // Validar mensagem
    if (!data.message || data.message.trim().length < 10) {
        showFieldError('message', 'Mensagem deve ter pelo menos 10 caracteres');
        isValid = false;
    }
    
    return isValid;
}

// Validar campo individual
function validateField(field) {
    const value = field.value.trim();
    
    switch (field.name) {
        case 'name':
            if (value.length < 2) {
                showFieldError(field.name, 'Nome deve ter pelo menos 2 caracteres');
                return false;
            }
            break;
            
        case 'email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                showFieldError(field.name, 'E-mail inválido');
                return false;
            }
            break;
            
        case 'message':
            if (value.length < 10) {
                showFieldError(field.name, 'Mensagem deve ter pelo menos 10 caracteres');
                return false;
            }
            break;
    }
    
    clearFieldError(field);
    return true;
}

// Mostrar erro no campo
function showFieldError(fieldName, message) {
    const field = document.querySelector(`[name="${fieldName}"]`);
    const formGroup = field.closest('.form-group');
    
    clearFieldError(field);
    
    const errorElement = document.createElement('span');
    errorElement.className = 'field-error';
    errorElement.textContent = message;
    errorElement.style.color = '#dc3545';
    errorElement.style.fontSize = '0.875rem';
    errorElement.style.marginTop = '0.25rem';
    errorElement.style.display = 'block';
    
    formGroup.appendChild(errorElement);
    field.style.borderColor = '#dc3545';
}

// Limpar erro do campo
function clearFieldError(field) {
    const formGroup = field.closest('.form-group');
    const existingError = formGroup.querySelector('.field-error');
    
    if (existingError) {
        existingError.remove();
    }
    
    field.style.borderColor = '';
}

// Submeter formulário
function submitForm(data) {
    const submitButton = document.querySelector('.contact-form button[type="submit"]');
    const originalText = submitButton.textContent;
    
    // Estado de loading
    submitButton.textContent = 'Enviando...';
    submitButton.disabled = true;
    submitButton.classList.add('loading');
    
    // Simular envio (substituir por integração real)
    setTimeout(() => {
        // Sucesso
        showNotification('Mensagem enviada com sucesso! Entraremos em contato em breve.', 'success');
        
        // Reset do formulário
        document.querySelector('.contact-form').reset();
        
        // Restaurar botão
        submitButton.textContent = originalText;
        submitButton.disabled = false;
        submitButton.classList.remove('loading');
    }, 2000);
}

// Mostrar notificação
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Estilos da notificação
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#007bff'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        max-width: 400px;
    `;
    
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Fechar ao clicar no X
    const closeButton = notification.querySelector('.notification-close');
    closeButton.addEventListener('click', () => {
        closeNotification(notification);
    });
    
    // Auto-fechar após 5 segundos
    setTimeout(() => {
        closeNotification(notification);
    }, 5000);
}

// Fechar notificação
function closeNotification(notification) {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 300);
}

// Efeito no header durante scroll
function initHeaderScrollEffect() {
    const header = document.querySelector('.header');
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', () => {
        const currentScrollY = window.scrollY;
        
        if (currentScrollY > 100) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        // Esconder/mostrar header baseado na direção do scroll
        if (currentScrollY > lastScrollY && currentScrollY > 200) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }
        
        lastScrollY = currentScrollY;
    });
}

// Dropdown menus
function initDropdownMenus() {
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const menu = dropdown.querySelector('.dropdown-menu');
        
        // Mostrar/esconder no hover (desktop)
        dropdown.addEventListener('mouseenter', () => {
            if (window.innerWidth >= 768) {
                menu.style.display = 'block';
                setTimeout(() => {
                    menu.style.opacity = '1';
                    menu.style.visibility = 'visible';
                    menu.style.transform = 'translateY(0)';
                }, 10);
            }
        });
        
        dropdown.addEventListener('mouseleave', () => {
            if (window.innerWidth >= 768) {
                menu.style.opacity = '0';
                menu.style.visibility = 'hidden';
                menu.style.transform = 'translateY(-10px)';
                setTimeout(() => {
                    menu.style.display = 'none';
                }, 300);
            }
        });
        
        // Toggle no clique (mobile)
        const dropdownLink = dropdown.querySelector('.nav-link');
        dropdownLink.addEventListener('click', (e) => {
            if (window.innerWidth < 768) {
                e.preventDefault();
                dropdown.classList.toggle('active');
            }
        });
    });
}

// Lazy loading para imagens
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                imageObserver.unobserve(img);
                
                img.addEventListener('load', () => {
                    img.classList.add('loaded');
                });
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Utilitário para debounce
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Otimização de performance para scroll
const optimizedScrollHandler = debounce(() => {
    // Handlers de scroll otimizados aqui
}, 16);

window.addEventListener('scroll', optimizedScrollHandler);

// Adicionar estilos CSS dinâmicos para mobile menu
const style = document.createElement('style');
style.textContent = `
    @media (max-width: 767px) {
        .nav-menu {
            position: fixed;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            flex-direction: column;
            padding: 2rem 1rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            transform: translateY(-100%);
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 999;
        }
        
        .nav-menu.active {
            display: flex;
            transform: translateY(0);
            opacity: 1;
            visibility: visible;
        }
        
        .nav-menu li {
            margin: 0.5rem 0;
        }
        
        .dropdown-menu {
            position: static;
            box-shadow: none;
            background: #f8f9fa;
            margin-left: 1rem;
            display: none;
        }
        
        .dropdown.active .dropdown-menu {
            display: block;
            opacity: 1;
            visibility: visible;
            transform: none;
        }
        
        .mobile-menu-toggle.active span:nth-child(1) {
            transform: rotate(45deg) translate(5px, 5px);
        }
        
        .mobile-menu-toggle.active span:nth-child(2) {
            opacity: 0;
        }
        
        .mobile-menu-toggle.active span:nth-child(3) {
            transform: rotate(-45deg) translate(7px, -6px);
        }
        
        body.menu-open {
            overflow: hidden;
        }
    }
    
    .header.scrolled {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    
    .header {
        transition: all 0.3s ease;
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }
    
    .notification-close {
        background: none;
        border: none;
        color: white;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
        line-height: 1;
    }
    
    .notification-close:hover {
        opacity: 0.8;
    }
`;

document.head.appendChild(style);

// Performance monitoring
if ('performance' in window) {
    window.addEventListener('load', () => {
        setTimeout(() => {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Site loaded in:', perfData.loadEventEnd - perfData.loadEventStart, 'ms');
        }, 0);
    });
}