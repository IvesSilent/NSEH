// ════════════════════════════════════════
// NSEH UX Enhancements — Micro-interaction Layer
// ════════════════════════════════════════

(function() {
  'use strict';

  // ── Modal Animation Helper ─────────────────────
  const _origStyles = new WeakMap();

  function animateModalOpen(overlay) {
    if (!overlay) return;
    overlay.style.opacity = '0';
    overlay.style.display = 'flex';
    // Force reflow
    void overlay.offsetHeight;
    overlay.style.transition = 'opacity 0.25s ease, backdrop-filter 0.25s ease';
    overlay.style.opacity = '1';

    const card = overlay.querySelector('.modal-card');
    if (card) {
      card.style.transform = 'scale(0.95) translateY(10px)';
      card.style.opacity = '0';
      card.style.transition = 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.25s ease';
      void card.offsetHeight;
      requestAnimationFrame(() => {
        card.style.transform = 'scale(1) translateY(0)';
        card.style.opacity = '1';
      });
    }
  }

  function animateModalClose(overlay, callback) {
    if (!overlay) return;
    const card = overlay.querySelector('.modal-card');
    if (card) {
      card.style.transition = 'transform 0.2s ease, opacity 0.2s ease';
      card.style.transform = 'scale(0.96)';
      card.style.opacity = '0';
    }
    overlay.style.opacity = '0';
    overlay.style.backdropFilter = 'blur(0)';

    setTimeout(() => {
      overlay.style.display = 'none';
      overlay.style.transition = '';
      overlay.style.opacity = '';
      overlay.style.backdropFilter = '';
      if (card) {
        card.style.transition = '';
        card.style.transform = '';
        card.style.opacity = '';
      }
      if (callback) callback();
    }, 220);
  }

  // ── Monkey-patch modal openers ────────────────
  function patchModal() {
    // Intercept display = 'flex' assignments on modal-overlay
    const observer = new MutationObserver((mutations) => {
      for (const m of mutations) {
        if (m.type !== 'attributes' || m.attributeName !== 'style') continue;
        const el = m.target;
        if (!el.classList.contains('modal-overlay')) continue;
        const style = el.getAttribute('style') || '';
        if (style.includes('display: flex') || style.includes('display:flex')) {
          // Prevent the default immediate show
          requestAnimationFrame(() => animateModalOpen(el));
        }
      }
    });

    document.querySelectorAll('.modal-overlay').forEach(el => {
      observer.observe(el, { attributes: true, attributeFilter: ['style'] });
    });
  }

  // ── Tab Switch Animation ──────────────────────
  function patchTabAnimation() {
    // Override the original tab click to add animation
    const tabs = document.querySelectorAll('.tab');
    const pages = document.querySelectorAll('.page');
    if (!tabs.length) return;

    tabs.forEach((tab, i) => {
      // Preserve original listener logic; just add animation wrapper
      const origClick = tab._listeners?.[0] || null;
      // We can't easily unwrap event listeners, so add a transition per-page
    });

    // Instead, animate page on classList change
    const pageObserver = new MutationObserver((mutations) => {
      for (const m of mutations) {
        if (m.type !== 'attributes' || m.attributeName !== 'class') continue;
        const page = m.target;
        if (!page.classList.contains('page')) continue;
        if (page.classList.contains('active')) {
          page.style.animation = 'none';
          void page.offsetHeight;
          page.style.animation = 'fadeSlideUp 0.35s ease both';
        }
      }
    });

    pages.forEach(p => {
      pageObserver.observe(p, { attributes: true, attributeFilter: ['class'] });
    });
  }

  // ── Form Auto-Save ────────────────────────────
  let _saveTimer = null;

  function initAutoSave() {
    const fields = [
      'population_capacity', 'num_generations', 'num_mutation',
      'num_hybridization', 'num_reflection', 'base_url',
      'problem', 'fun_name', 'fun_notes', 'problem_path',
      'train_data', 'train_solution', 'ascend'
    ];
    const container = document.getElementById('setting-page');
    if (!container) return;

    function debounceSave() {
      clearTimeout(_saveTimer);
      _saveTimer = setTimeout(() => {
        const config = {};
        fields.forEach(id => {
          const el = document.getElementById(id);
          if (el) config[id] = el.value;
        });
        config.population_capacity = parseInt(document.getElementById('population_capacity')?.value) || 10;
        config.num_generations = parseInt(document.getElementById('num_generations')?.value) || 10;
        config.num_mutation = parseInt(document.getElementById('num_mutation')?.value) || 2;
        config.num_hybridization = parseInt(document.getElementById('num_hybridization')?.value) || 2;
        config.num_reflection = parseInt(document.getElementById('num_reflection')?.value) || 2;
        config.ascend = document.getElementById('ascend')?.value === 'true';
        config.fun_args = [...document.querySelectorAll('#fun_args_container .arg-item')].map(el => el.textContent.trim());
        config.fun_return = [...document.querySelectorAll('#fun_return_container .arg-item')].map(el => el.textContent.trim());
        config.llm_model = getCurrentModelName ? getCurrentModelName() : '';

        try { localStorage.setItem('nseh_autosave', JSON.stringify(config)); } catch(e) {}
      }, 800);
    }

    // Listen to all form fields in setting page
    container.querySelectorAll('input, select, textarea, .arg-item').forEach(el => {
      el.addEventListener('change', debounceSave);
      el.addEventListener('input', debounceSave);
      el.addEventListener('blur', debounceSave);
    });
  }

  // ── Restore Auto-Save ─────────────────────────
  function restoreAutoSave() {
    try {
      const saved = localStorage.getItem('nseh_autosave');
      if (!saved) return;
      const config = JSON.parse(saved);
      const fields = [
        'population_capacity', 'num_generations', 'num_mutation',
        'num_hybridization', 'num_reflection', 'base_url',
        'problem', 'fun_name', 'fun_notes', 'problem_path',
        'train_data', 'train_solution'
      ];
      fields.forEach(id => {
        const el = document.getElementById(id);
        if (el && config[id] !== undefined) el.value = config[id];
      });
      const asc = document.getElementById('ascend');
      if (asc && config.ascend !== undefined) asc.value = config.ascend ? 'true' : 'false';
      // Don't auto-restore if cached config already loaded
    } catch(e) {}
  }

  // ── Keyboard Focus Management for Modals ─────
  let _lastFocused = null;

  function initModalFocusTrap() {
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Tab') return;
      const activeModal = document.querySelector('.modal-overlay[style*="display: flex"], .modal-overlay[style*="display:flex"]');
      if (!activeModal) return;

      const focusable = activeModal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      if (!focusable.length) { e.preventDefault(); return; }

      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    });

    // Track last focused before modal opens
    document.querySelectorAll('.modal-overlay').forEach(modal => {
      const openBtn = document.querySelector(`[onclick*="${modal.id}"]`) ||
                       document.querySelectorAll('button, a');
      // Fallback: watch for style change
      const obs = new MutationObserver(() => {
        const visible = modal.style.display === 'flex';
        if (visible) {
          _lastFocused = document.activeElement;
          // Focus first focusable in modal after animation
          setTimeout(() => {
            const first = modal.querySelector('input, select, textarea, button');
            if (first && !document.activeElement?.closest('.modal-overlay')) first.focus();
          }, 350);
        } else if (_lastFocused) {
          setTimeout(() => _lastFocused?.focus(), 50);
          _lastFocused = null;
        }
      });
      obs.observe(modal, { attributes: true, attributeFilter: ['style'] });
    });
  }

  // ── Smooth anchor scrolling ──────────────────
  function initSmoothScroll() {
    document.addEventListener('click', (e) => {
      const a = e.target.closest('a[href^="#"]');
      if (!a) return;
      e.preventDefault();
      const target = document.querySelector(a.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  }

  // ── Page entrance animation ──────────────────
  function initPageEntrance() {
    const content = document.querySelector('.page.active');
    if (content) {
      content.style.opacity = '0';
      content.style.transform = 'translateY(12px)';
      content.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
      void content.offsetHeight;
      requestAnimationFrame(() => {
        content.style.opacity = '1';
        content.style.transform = 'translateY(0)';
        setTimeout(() => {
          content.style.transition = '';
          content.style.opacity = '';
          content.style.transform = '';
        }, 500);
      });
    }
  }

  // ── Init ──────────────────────────────────────
  function init() {
    // Wait for DOM content
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => {
        setTimeout(initNow, 50);
      });
    } else {
      setTimeout(initNow, 50);
    }
  }

  function initNow() {
    patchModal();
    patchTabAnimation();
    initAutoSave();
    initModalFocusTrap();
    initSmoothScroll();
    initPageEntrance();
    // Restore after existing restoreCachedConfig runs
    setTimeout(restoreAutoSave, 200);
  }

  init();

})();
