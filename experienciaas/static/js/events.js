/**
 * Event List JavaScript
 * Funcionalidad para la página de listado de eventos
 */

document.addEventListener('DOMContentLoaded', function() {
  // Featured Events Spotlight Carousel
  initializeSpotlightCarousel();
  
  // Legacy Featured Events Carousel (fallback)
  initializeFeaturedEventsCarousel();
  
  // Event Cards Grid Animation
  initializeEventCardsAnimation();
  
  // Sponsor Carousels
  initializeSponsorCarousels();
});

/**
 * Inicializa el nuevo carrusel spotlight de eventos destacados
 */
function initializeSpotlightCarousel() {
  const spotlightSection = document.querySelector('.featured-spotlight-section');
  const spotlightTrack = document.querySelector('.spotlight-track');
  const spotlightCards = document.querySelectorAll('.spotlight-card');
  const prevBtn = document.querySelector('.spotlight-prev');
  const nextBtn = document.querySelector('.spotlight-next');
  const dots = document.querySelectorAll('.spotlight-dot');
  const galleryThumbs = document.querySelectorAll('.gallery-thumb');
  const progressFill = document.querySelector('.progress-fill');
  
  if (!spotlightSection || !spotlightTrack || spotlightCards.length === 0) {
    return;
  }
  
  let currentSlide = 0;
  let isAutoScrollActive = true;
  let autoScrollTimer;
  const autoScrollInterval = 6000; // 6 segundos entre slides
  
  /**
   * Actualiza el carrusel spotlight
   */
  function updateSpotlightCarousel() {
    // Mover el track
    const translateX = -currentSlide * 100;
    spotlightTrack.style.transform = `translateX(${translateX}%)`;
    
    // Actualizar dots
    dots.forEach((dot, index) => {
      dot.classList.toggle('active', index === currentSlide);
      dot.style.background = index === currentSlide ? 
        'linear-gradient(45deg, #FFD700, #FFA500)' : 
        'rgba(255, 215, 0, 0.3)';
      dot.style.transform = index === currentSlide ? 'scale(1.3)' : 'scale(1)';
    });
    
    // Actualizar galería de miniaturas
    galleryThumbs.forEach((thumb, index) => {
      thumb.classList.toggle('active', index === currentSlide);
      thumb.style.border = index === currentSlide ? 
        '3px solid #FFD700' : 
        '2px solid transparent';
      thumb.style.opacity = index === currentSlide ? '1' : '0.6';
      thumb.style.transform = index === currentSlide ? 'scale(1.1)' : 'scale(1)';
    });
    
    // Actualizar barra de progreso
    const progress = ((currentSlide + 1) / spotlightCards.length) * 100;
    if (progressFill) {
      progressFill.style.width = `${progress}%`;
    }
    
    // Aplicar efectos especiales a la card activa
    spotlightCards.forEach((card, index) => {
      const isActive = index === currentSlide;
      const bgImage = card.querySelector('.spotlight-bg-image img');
      const imageOverlay = card.querySelector('.image-overlay');
      
      if (bgImage) {
        bgImage.style.opacity = isActive ? '0.4' : '0.3';
        bgImage.style.transform = isActive ? 'scale(1.05)' : 'scale(1)';
      }
      
      if (imageOverlay) {
        imageOverlay.style.opacity = isActive ? '0' : '1';
      }
    });
  }
  
  /**
   * Ir al siguiente slide
   */
  function nextSlide() {
    currentSlide = (currentSlide + 1) % spotlightCards.length;
    updateSpotlightCarousel();
    resetAutoScroll();
  }
  
  /**
   * Ir al slide anterior
   */
  function prevSlide() {
    currentSlide = currentSlide === 0 ? spotlightCards.length - 1 : currentSlide - 1;
    updateSpotlightCarousel();
    resetAutoScroll();
  }
  
  /**
   * Ir a un slide específico
   */
  function goToSlide(index) {
    if (index >= 0 && index < spotlightCards.length) {
      currentSlide = index;
      updateSpotlightCarousel();
      resetAutoScroll();
    }
  }
  
  /**
   * Iniciar auto-scroll
   */
  function startAutoScroll() {
    if (spotlightCards.length <= 1 || !isAutoScrollActive) return;
    
    autoScrollTimer = setInterval(() => {
      nextSlide();
    }, autoScrollInterval);
  }
  
  /**
   * Detener auto-scroll
   */
  function stopAutoScroll() {
    clearInterval(autoScrollTimer);
  }
  
  /**
   * Reiniciar auto-scroll
   */
  function resetAutoScroll() {
    stopAutoScroll();
    if (isAutoScrollActive) {
      startAutoScroll();
    }
  }
  
  // Event listeners para navegación
  if (prevBtn) {
    prevBtn.addEventListener('click', prevSlide);
  }
  
  if (nextBtn) {
    nextBtn.addEventListener('click', nextSlide);
  }
  
  // Event listeners para dots
  dots.forEach((dot, index) => {
    dot.addEventListener('click', () => goToSlide(index));
  });
  
  // Event listeners para galería de miniaturas
  galleryThumbs.forEach((thumb, index) => {
    thumb.addEventListener('click', () => goToSlide(index));
  });
  
  // Pausar auto-scroll al hacer hover
  if (spotlightSection) {
    spotlightSection.addEventListener('mouseenter', () => {
      isAutoScrollActive = false;
      stopAutoScroll();
    });
    
    spotlightSection.addEventListener('mouseleave', () => {
      isAutoScrollActive = true;
      startAutoScroll();
    });
  }
  
  // Efectos hover para las cards
  spotlightCards.forEach((card, index) => {
    card.addEventListener('mouseenter', function() {
      const bgImage = this.querySelector('.spotlight-bg-image img');
      const imageSpotlight = this.querySelector('.image-spotlight img');
      const imageOverlay = this.querySelector('.image-overlay');
      
      if (bgImage) {
        bgImage.style.transform = 'scale(1.1)';
        bgImage.style.opacity = '0.5';
      }
      
      if (imageSpotlight) {
        imageSpotlight.style.transform = 'scale(1.1)';
      }
      
      if (imageOverlay) {
        imageOverlay.style.opacity = '1';
      }
      
      // Agregar efecto de iluminación
      this.style.background = 'linear-gradient(145deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.1) 100%)';
    });
    
    card.addEventListener('mouseleave', function() {
      const isActive = index === currentSlide;
      const bgImage = this.querySelector('.spotlight-bg-image img');
      const imageSpotlight = this.querySelector('.image-spotlight img');
      const imageOverlay = this.querySelector('.image-overlay');
      
      if (bgImage) {
        bgImage.style.transform = isActive ? 'scale(1.05)' : 'scale(1)';
        bgImage.style.opacity = isActive ? '0.4' : '0.3';
      }
      
      if (imageSpotlight) {
        imageSpotlight.style.transform = 'scale(1)';
      }
      
      if (imageOverlay) {
        imageOverlay.style.opacity = isActive ? '0' : '1';
      }
      
      // Restaurar fondo normal
      this.style.background = 'linear-gradient(145deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%)';
    });
  });
  
  // Navegación con teclado
  document.addEventListener('keydown', (e) => {
    if (!spotlightSection.matches(':hover')) return;
    
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      prevSlide();
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      nextSlide();
    } else if (e.key >= '1' && e.key <= '9') {
      const slideIndex = parseInt(e.key) - 1;
      if (slideIndex < spotlightCards.length) {
        e.preventDefault();
        goToSlide(slideIndex);
      }
    }
  });
  
  // Soporte para gestos táctiles (swipe)
  let touchStartX = 0;
  let touchEndX = 0;
  
  spotlightSection.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  });
  
  spotlightSection.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
  });
  
  function handleSwipe() {
    const swipeThreshold = 50;
    const diff = touchStartX - touchEndX;
    
    if (Math.abs(diff) > swipeThreshold) {
      if (diff > 0) {
        // Swipe left - next slide
        nextSlide();
      } else {
        // Swipe right - previous slide
        prevSlide();
      }
    }
  }
  
  // Inicialización
  updateSpotlightCarousel();
  
  // Iniciar auto-scroll si hay más de una card
  if (spotlightCards.length > 1) {
    startAutoScroll();
  }
  
  // Animación de entrada para las estrellas flotantes
  const floatingStars = document.querySelectorAll('.floating-star');
  floatingStars.forEach((star, index) => {
    star.style.animationDelay = `${index * 0.5}s`;
  });
}

/**
 * Inicializa el carrusel de eventos destacados
 */
function initializeFeaturedEventsCarousel() {
  const featuredSection = document.querySelector('.featured-events-section');
  const track = document.querySelector('.featured-events-track');
  const prevBtn = document.querySelector('.featured-prev');
  const nextBtn = document.querySelector('.featured-next');
  const dots = document.querySelectorAll('.featured-dot');
  
  if (!track || !featuredSection) return;
  
  const cards = track.querySelectorAll('.featured-event-card');
  
  // Hide section if no featured events
  if (cards.length === 0) {
    featuredSection.style.display = 'none';
    return;
  }
  
  let currentSlide = 0;
  let isDesktop = window.innerWidth >= 768;
  let slidesToShow = getSlidesToShow();
  
  function getSlidesToShow() {
    if (window.innerWidth >= 1200) return 3; // Desktop large
    if (window.innerWidth >= 768) return 2;  // Desktop small/tablet
    return 1; // Mobile
  }
  
  function getMaxSlides() {
    return Math.max(0, cards.length - slidesToShow);
  }
  
  function updateCarousel() {
    slidesToShow = getSlidesToShow();
    const maxSlides = getMaxSlides();
    currentSlide = Math.min(currentSlide, maxSlides);
    
    // Calculate card width based on container and number of visible cards
    const containerWidth = track.parentElement.offsetWidth;
    const gap = 20;
    const cardWidth = (containerWidth - (gap * (slidesToShow - 1))) / slidesToShow;
    const slideWidth = cardWidth + gap;
    
    // Set card widths dynamically
    cards.forEach(card => {
      card.style.flex = `0 0 ${cardWidth}px`;
      card.style.minWidth = `${Math.min(cardWidth, 280)}px`; // Maintain minimum width
    });
    
    const translateX = -(currentSlide * slideWidth);
    track.style.transform = `translateX(${translateX}px)`;
    
    // Update navigation buttons
    if (prevBtn && nextBtn) {
      const shouldShowNavigation = cards.length > slidesToShow;
      
      prevBtn.style.display = shouldShowNavigation ? 'inline-flex' : 'none';
      nextBtn.style.display = shouldShowNavigation ? 'inline-flex' : 'none';
      
      if (shouldShowNavigation) {
        prevBtn.disabled = currentSlide === 0;
        nextBtn.disabled = currentSlide >= maxSlides;
        
        prevBtn.style.opacity = currentSlide === 0 ? '0.5' : '1';
        nextBtn.style.opacity = currentSlide >= maxSlides ? '0.5' : '1';
      }
    }
    
    // Update dots for mobile
    dots.forEach((dot, index) => {
      // Only show dots if we have more cards than can be displayed
      const shouldShowDots = cards.length > slidesToShow && !isDesktop;
      dot.style.display = shouldShowDots ? 'block' : 'none';
      
      if (shouldShowDots) {
        dot.classList.toggle('active', index === currentSlide);
        dot.style.background = index === currentSlide ? '#667eea' : '#cbd5e0';
      }
    });
    
    // Hide dots container if not needed
    const dotsContainer = document.querySelector('.featured-dots');
    if (dotsContainer) {
      const shouldShowDotsContainer = cards.length > slidesToShow && !isDesktop;
      dotsContainer.style.display = shouldShowDotsContainer ? 'flex' : 'none';
    }
  }
  
  function nextSlide() {
    const maxSlides = getMaxSlides();
    if (currentSlide < maxSlides) {
      currentSlide++;
      updateCarousel();
    } else if (cards.length > slidesToShow) {
      // Loop back to beginning for auto-scroll
      currentSlide = 0;
      updateCarousel();
    }
  }
  
  function prevSlide() {
    if (currentSlide > 0) {
      currentSlide--;
      updateCarousel();
    } else if (cards.length > slidesToShow) {
      // Loop to end
      currentSlide = getMaxSlides();
      updateCarousel();
    }
  }
  
  // Event listeners
  if (nextBtn) nextBtn.addEventListener('click', nextSlide);
  if (prevBtn) prevBtn.addEventListener('click', prevSlide);
  
  // Dots navigation
  dots.forEach((dot, index) => {
    dot.addEventListener('click', () => {
      const maxSlides = getMaxSlides();
      currentSlide = Math.min(index, maxSlides);
      updateCarousel();
    });
  });
  
  // Auto-scroll for featured events
  let autoScrollTimer;
  function startAutoScroll() {
    // Only auto-scroll if we have more cards than can be displayed
    if (cards.length <= slidesToShow) return;
    
    autoScrollTimer = setInterval(() => {
      nextSlide(); // This will automatically loop back to start
    }, 5000); // Change slide every 5 seconds
  }
  
  function stopAutoScroll() {
    clearInterval(autoScrollTimer);
  }
  
  // Start auto-scroll only if more cards than visible
  if (cards.length > slidesToShow) {
    startAutoScroll();
  }
  
  // Pause auto-scroll on hover
  const carousel = document.querySelector('.featured-events-carousel');
  if (carousel) {
    carousel.addEventListener('mouseenter', stopAutoScroll);
    carousel.addEventListener('mouseleave', () => {
      if (cards.length > slidesToShow) startAutoScroll();
    });
  }
  
  // Handle window resize
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      isDesktop = window.innerWidth >= 768;
      updateCarousel();
      
      // Restart auto-scroll if needed
      stopAutoScroll();
      if (cards.length > getSlidesToShow()) {
        startAutoScroll();
      }
    }, 250);
  });
  
  // Initial setup
  updateCarousel();
  
  // Add hover effects to featured cards
  cards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.transform = 'translateY(-10px) scale(1.02)';
      this.style.boxShadow = '0 20px 40px rgba(0,0,0,0.15)';
      this.style.zIndex = '10';
      
      const img = this.querySelector('img');
      if (img) {
        img.style.transform = 'scale(1.1)';
      }
    });
    
    card.addEventListener('mouseleave', function() {
      this.style.transform = 'translateY(0) scale(1)';
      this.style.boxShadow = '0 10px 30px rgba(0,0,0,0.12)';
      this.style.zIndex = '1';
      
      const img = this.querySelector('img');
      if (img) {
        img.style.transform = 'scale(1)';
      }
    });
  });
  
  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (!featuredSection.matches(':hover')) return;
    
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      prevSlide();
      stopAutoScroll();
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      nextSlide();
      stopAutoScroll();
    }
  });
}

/**
 * Inicializa la animación de las tarjetas de eventos
 */
function initializeEventCardsAnimation() {
  const eventCards = document.querySelectorAll('.event-card');
  
  eventCards.forEach((card, index) => {
    card.style.transition = `transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), opacity 0.4s ease`;
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    
    // Trigger animation on load
    setTimeout(() => {
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }, index * 100); // Staggered animation
  });
}

/**
 * Inicializa los carruseles de sponsors
 */
function initializeSponsorCarousels() {
  const sponsorCarousels = document.querySelectorAll('.sponsor-carousel');
  
  sponsorCarousels.forEach(carousel => {
    const sliderTrack = carousel.querySelector('.sponsor-slider-track');
    
    if (!sliderTrack) return;
    
    // Método 1: Usar CSS Animation (más suave)
    const sponsorItems = sliderTrack.querySelectorAll('.sponsor-item');
    
    if (sponsorItems.length > 0) {
      // Verificar que el ancho total permita la animación infinita
      let totalWidth = 0;
      sponsorItems.forEach(item => {
        totalWidth += item.offsetWidth;
      });
      
      // Establecer el ancho del track para la animación infinita
      if (totalWidth > 0) {
        sliderTrack.style.width = `${totalWidth * 2}px`;
      }
      
      // Agregar eventos de hover para pausar/reanudar
      carousel.addEventListener('mouseenter', () => {
        sliderTrack.style.animationPlayState = 'paused';
      });
      
      carousel.addEventListener('mouseleave', () => {
        sliderTrack.style.animationPlayState = 'running';
      });
    }
  });

  // Método 2: JavaScript Animation (alternativo para casos específicos)
  initializeJavaScriptSponsorCarousels();
}

/**
 * Inicializa carruseles de sponsors usando JavaScript (método alternativo)
 */
function initializeJavaScriptSponsorCarousels() {
  const sponsorTracks = document.querySelectorAll('.sponsor-slider-track');
  
  sponsorTracks.forEach(track => {
    const wrapper = track.parentElement;
    const wrapperWidth = wrapper?.offsetWidth || 0;
    const trackWidth = track.scrollWidth / 2; // Dividido por 2 porque tenemos contenido duplicado
    
    if (trackWidth > wrapperWidth && trackWidth > 0) {
      // Solo animar si el contenido es más ancho que el contenedor
      let scrollPosition = 0;
      const speed = 0.5; // Pixels por frame
      let animationFrame;
      
      function animate() {
        scrollPosition += speed;
        
        // Cuando hemos desplazado el ancho de un set completo, reiniciar sin que se note
        if (scrollPosition >= trackWidth) {
          scrollPosition = 0;
        }
        
        track.style.transform = `translateX(-${scrollPosition}px)`;
        animationFrame = requestAnimationFrame(animate);
      }
      
      // Solo usar JavaScript animation si CSS no está funcionando
      const computedStyle = getComputedStyle(track);
      if (!computedStyle.animationName || computedStyle.animationName === 'none') {
        animate();
      }
      
      // Pausar animación JavaScript en hover
      const carousel = track.closest('.sponsor-carousel');
      if (carousel) {
        carousel.addEventListener('mouseenter', () => {
          if (animationFrame) {
            cancelAnimationFrame(animationFrame);
          }
        });
        
        carousel.addEventListener('mouseleave', () => {
          if (!computedStyle.animationName || computedStyle.animationName === 'none') {
            animate();
          }
        });
      }
    }
  });
}
