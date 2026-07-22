/* ============================================
   Gestures — Suporte a gestos touch e teclado
   ============================================ */

class GestureController {
  constructor(viewer, options = {}) {
    this.viewer = viewer;
    this.options = Object.assign({
      swipeThreshold: 50,
      swipeAngleThreshold: 30,
    }, options);

    this.startY = 0;
    this.startX = 0;
    this.startTime = 0;
    this.isDragging = false;

    this._bindEvents();
  }

  _bindEvents() {
    const container = this.viewer.container;

    // Touch events
    container.addEventListener('touchstart', this._onTouchStart.bind(this), { passive: true });
    container.addEventListener('touchmove', this._onTouchMove.bind(this), { passive: true });
    container.addEventListener('touchend', this._onTouchEnd.bind(this), { passive: true });

    // Mouse events (para desktop)
    container.addEventListener('mousedown', this._onMouseDown.bind(this));
    document.addEventListener('mousemove', this._onMouseMove.bind(this));
    document.addEventListener('mouseup', this._onMouseUp.bind(this));

    // Keyboard events
    document.addEventListener('keydown', this._onKeyDown.bind(this));

    // Wheel events
    container.addEventListener('wheel', this._onWheel.bind(this), { passive: true });

    // Visibility change (pausa quando a aba perde foco)
    document.addEventListener('visibilitychange', this._onVisibilityChange.bind(this));
  }

  // --- Touch ---

  _onTouchStart(e) {
    const touch = e.touches[0];
    this.startY = touch.clientY;
    this.startX = touch.clientX;
    this.startTime = Date.now();
    this.isDragging = false;
  }

  _onTouchMove(e) {
    if (!this.startY) return;
    const touch = e.touches[0];
    const deltaY = Math.abs(touch.clientY - this.startY);
    const deltaX = Math.abs(touch.clientX - this.startX);

    // Só considera como drag se for predominantemente vertical
    if (deltaY > 10 && deltaY > deltaX) {
      this.isDragging = true;
    }
  }

  _onTouchEnd(e) {
    if (!this.startY) return;

    const touch = e.changedTouches[0];
    const deltaY = touch.clientY - this.startY;
    const deltaX = touch.clientX - this.startX;
    const absDeltaY = Math.abs(deltaY);
    const elapsed = Date.now() - this.startTime;

    this.startY = 0;
    this.startX = 0;

    // Ignorar se foi um toque curto sem movimento (tap)
    if (absDeltaY < 10 && elapsed < 300) return;

    if (absDeltaY > this.options.swipeThreshold) {
      if (deltaY < 0) {
        this.viewer.next();
      } else {
        this.viewer.prev();
      }
    }
  }

  // --- Mouse ---

  _onMouseDown(e) {
    this.startY = e.clientY;
    this.startX = e.clientX;
    this.isDragging = false;
  }

  _onMouseMove(e) {
    if (this.startY === 0) return;
    const deltaY = Math.abs(e.clientY - this.startY);
    if (deltaY > 10) {
      this.isDragging = true;
    }
  }

  _onMouseUp(e) {
    if (this.startY === 0) return;
    const deltaY = e.clientY - this.startY;
    const absDeltaY = Math.abs(deltaY);

    // Clique (sem arrasto) nas laterais
    if (!this.isDragging && absDeltaY < 10) {
      const rect = this.viewer.container.getBoundingClientRect();
      const clickX = e.clientX - rect.left;
      const midX = rect.width / 2;

      if (clickX > midX) {
        this.viewer.next();
      } else {
        this.viewer.prev();
      }
    } else if (absDeltaY > this.options.swipeThreshold) {
      // Arrasto vertical
      if (deltaY < 0) {
        this.viewer.next();
      } else {
        this.viewer.prev();
      }
    }

    this.startY = 0;
    this.startX = 0;
    this.isDragging = false;
  }

  // --- Teclado ---

  _onKeyDown(e) {
    switch (e.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        e.preventDefault();
        this.viewer.next();
        break;
      case 'ArrowUp':
      case 'ArrowLeft':
        e.preventDefault();
        this.viewer.prev();
        break;
      case ' ':
        e.preventDefault();
        if (this.viewer.isPaused) {
          this.viewer.resume();
        } else {
          this.viewer.pause();
        }
        break;
      case 'Home':
        e.preventDefault();
        this.viewer.goTo(0);
        break;
      case 'End':
        e.preventDefault();
        this.viewer.goTo(this.viewer.slides.length - 1);
        break;
    }
  }

  // --- Scroll (roda do mouse) ---

  _onWheel(e) {
    if (e.deltaY > 0) {
      this.viewer.next();
    } else if (e.deltaY < 0) {
      this.viewer.prev();
    }
  }

  // --- Visibilidade ---

  _onVisibilityChange() {
    if (document.hidden) {
      this.viewer.pause();
    } else {
      this.viewer.resume();
    }
  }

  destroy() {
    // Event listeners seriam limpos em uma implementação mais robusta
    this.viewer = null;
  }
}
