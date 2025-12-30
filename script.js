// Glyphs info MCP - Website Scripts

// Copy to clipboard functionality
document.querySelectorAll('.copy-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    const text = btn.dataset.copy;
    try {
      await navigator.clipboard.writeText(text);
      btn.classList.add('copied');

      // Store original SVG element
      const originalSvg = btn.querySelector('svg');
      const originalSvgClone = originalSvg.cloneNode(true);

      // Create checkmark SVG safely using DOM methods
      const checkSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      checkSvg.setAttribute('width', '16');
      checkSvg.setAttribute('height', '16');
      checkSvg.setAttribute('viewBox', '0 0 24 24');
      checkSvg.setAttribute('fill', 'none');
      checkSvg.setAttribute('stroke', 'currentColor');
      checkSvg.setAttribute('stroke-width', '2');

      const polyline = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
      polyline.setAttribute('points', '20 6 9 17 4 12');
      checkSvg.appendChild(polyline);

      // Replace with checkmark
      btn.replaceChild(checkSvg, originalSvg);

      setTimeout(() => {
        btn.classList.remove('copied');
        btn.replaceChild(originalSvgClone, btn.querySelector('svg'));
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  });
});

// Scroll animation with Intersection Observer
const observerOptions = {
  root: null,
  rootMargin: '0px',
  threshold: 0.1
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('animate-in');
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

// Observe elements for scroll animation
document.querySelectorAll('.feature-card, .module-card, .code-block').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});

// Add animation styles when element is in view
const style = document.createElement('style');
style.textContent = `
  .feature-card.animate-in,
  .module-card.animate-in,
  .code-block.animate-in {
    opacity: 1 !important;
    transform: translateY(0) !important;
  }
`;
document.head.appendChild(style);

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// Header background on scroll
const header = document.querySelector('header');
let lastScroll = 0;

window.addEventListener('scroll', () => {
  const currentScroll = window.pageYOffset;

  if (currentScroll > 50) {
    header.style.background = 'rgba(26, 26, 26, 0.95)';
  } else {
    header.style.background = 'rgba(26, 26, 26, 0.9)';
  }

  lastScroll = currentScroll;
});

// Language preference storage
(function() {
  'use strict';

  var LANG_PREF_KEY = 'glyphs-info-mcp-lang';

  // Save language preference when user clicks language switch
  document.querySelectorAll('.lang-switch[data-lang]').forEach(function(link) {
    link.addEventListener('click', function() {
      var targetLang = this.dataset.lang;
      try {
        localStorage.setItem(LANG_PREF_KEY, targetLang);
      } catch (e) {
        // localStorage unavailable
      }
    });
  });
})();
