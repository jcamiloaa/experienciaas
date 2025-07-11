/* ========================================
   Experienciaas - Enhanced Functionality
   ======================================== */

// Global app object
const ExperienciaasApp = {
  // Initialize all components
  init() {
    this.initLazyLoading();
    this.initSmoothScrolling();
    this.initSearchFilters();
    this.initCardAnimations();
    this.initTooltips();
    this.initImagePreview();
  },

  // Lazy loading for images
  initLazyLoading() {
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.classList.remove('lazy');
            imageObserver.unobserve(img);
          }
        });
      });

      document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
      });
    }
  },

  // Smooth scrolling for anchor links
  initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        
        // Skip if href is just "#" or empty, or if it's a Bootstrap dropdown
        if (!href || href === '#' || href.length <= 1 || this.hasAttribute('data-bs-toggle')) {
          return;
        }
        
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  },

  // Enhanced search and filter functionality
  initSearchFilters() {
    const searchInput = document.querySelector('input[name="search"]');
    const filterForm = document.querySelector('.filter-form');
    
    if (searchInput) {
      // Add search icon animation
      searchInput.addEventListener('focus', () => {
        searchInput.parentElement.classList.add('search-focused');
      });
      
      searchInput.addEventListener('blur', () => {
        searchInput.parentElement.classList.remove('search-focused');
      });
    }

    // Auto-submit filters with debouncing
    if (filterForm) {
      const selects = filterForm.querySelectorAll('select');
      selects.forEach(select => {
        select.addEventListener('change', this.debounce(() => {
          this.showLoadingSpinner();
          filterForm.submit();
        }, 300));
      });
    }
  },

  // Card hover animations and effects
  initCardAnimations() {
    const cards = document.querySelectorAll('.event-card, .card');
    
    cards.forEach(card => {
      // Add entrance animation
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      
      // Intersection observer for entrance animation
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            setTimeout(() => {
              entry.target.style.transition = 'all 0.6s ease-out';
              entry.target.style.opacity = '1';
              entry.target.style.transform = 'translateY(0)';
            }, Math.random() * 200);
            observer.unobserve(entry.target);
          }
        });
      }, { threshold: 0.1 });
      
      observer.observe(card);

      // Enhanced hover effects
      card.addEventListener('mouseenter', () => {
        card.style.transform = 'translateY(-8px) scale(1.02)';
      });
      
      card.addEventListener('mouseleave', () => {
        card.style.transform = 'translateY(0) scale(1)';
      });
    });
  },

  // Initialize Bootstrap tooltips
  initTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(tooltipTriggerEl => {
      new bootstrap.Tooltip(tooltipTriggerEl);
    });
  },

  // Image preview functionality
  initImagePreview() {
    const images = document.querySelectorAll('.event-image, .card-img-top');
    images.forEach(img => {
      // Evitar preview en imágenes con la clase 'no-image-preview'
      if (img.classList.contains('no-image-preview')) {
        img.style.cursor = 'default';
        return;
      }
      img.addEventListener('click', () => {
        this.showImageModal(img.src, img.alt);
      });
      img.style.cursor = 'pointer';
    });
  },

  // Utility functions
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  showLoadingSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'loading-spinner';
    spinner.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cargando...';
    spinner.style.cssText = `
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      background: white;
      padding: 20px;
      border-radius: 10px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.1);
      z-index: 10000;
    `;
    document.body.appendChild(spinner);
    
    setTimeout(() => {
      spinner.remove();
    }, 2000);
  },

  showImageModal(src, alt) {
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.innerHTML = `
      <div class="image-modal-overlay" onclick="this.parentElement.remove()">
        <div class="image-modal-content">
          <img src="${src}" alt="${alt}" style="max-width: 90vw; max-height: 90vh; object-fit: contain;">
          <button class="image-modal-close" onclick="this.closest('.image-modal').remove()">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>
    `;
    
    modal.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.9);
      z-index: 10000;
      display: flex;
      align-items: center;
      justify-content: center;
    `;
    
    document.body.appendChild(modal);
    
    // Close on ESC key
    document.addEventListener('keydown', function escHandler(e) {
      if (e.key === 'Escape') {
        modal.remove();
        document.removeEventListener('keydown', escHandler);
      }
    });
  },

  // Social sharing functions
  shareEvent(platform, url, title) {
    const encodedUrl = encodeURIComponent(url);
    const encodedTitle = encodeURIComponent(title);
    
    const shareUrls = {
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
      twitter: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
      whatsapp: `https://wa.me/?text=${encodedTitle} ${encodedUrl}`,
      linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`
    };
    
    if (shareUrls[platform]) {
      window.open(shareUrls[platform], '_blank', 'width=600,height=400');
    }
  },

  // Copy to clipboard function
  copyToClipboard(text) {
    if (navigator.clipboard) {
      return navigator.clipboard.writeText(text);
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      return Promise.resolve();
    }
  },

  // Show notification
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'exclamation-triangle' : 'info'}-circle"></i>
      <span>${message}</span>
      <button onclick="this.parentElement.remove()">
        <i class="fas fa-times"></i>
      </button>
    `;
    
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: var(--${type === 'success' ? 'success' : type === 'error' ? 'error' : 'primary'}-color);
      color: white;
      padding: 15px 20px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      z-index: 10000;
      animation: slideInRight 0.3s ease-out;
      display: flex;
      align-items: center;
      gap: 10px;
      max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
      notification.style.animation = 'slideOutRight 0.3s ease-in';
      setTimeout(() => notification.remove(), 300);
    }, 5000);
  }
};

// Form validation helpers
const FormValidation = {
  validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  validateRequired(value) {
    return value && value.trim().length > 0;
  },

  showFieldError(field, message) {
    const existing = field.parentElement.querySelector('.field-error');
    if (existing) existing.remove();
    
    const error = document.createElement('div');
    error.className = 'field-error text-danger mt-1';
    error.innerHTML = `<small><i class="fas fa-exclamation-triangle me-1"></i>${message}</small>`;
    field.parentElement.appendChild(error);
    field.classList.add('is-invalid');
  },

  clearFieldError(field) {
    const existing = field.parentElement.querySelector('.field-error');
    if (existing) existing.remove();
    field.classList.remove('is-invalid');
  }
};

// CSS Animations
const style = document.createElement('style');
style.textContent = `
  @keyframes slideInRight {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
  }
  
  @keyframes slideOutRight {
    from { transform: translateX(0); }
    to { transform: translateX(100%); }
  }
  
  .search-focused {
    transform: scale(1.02);
    box-shadow: 0 0 0 0.2rem rgba(59, 130, 246, 0.25) !important;
  }
  
  .event-card {
    transition: all 0.3s ease;
  }
  
  .lazy {
    opacity: 0;
    transition: opacity 0.3s;
  }
  
  .image-modal-close {
    position: absolute;
    top: 20px;
    right: 20px;
    background: rgba(255,255,255,0.9);
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    cursor: pointer;
    font-size: 16px;
  }
`;
document.head.appendChild(style);

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  ExperienciaasApp.init();
});

// Export for global access
window.ExperienciaasApp = ExperienciaasApp;
window.FormValidation = FormValidation;
