/* ============================================
   StoryViewer — Núcleo do visualizador de Stories
   ============================================ */

class StoryViewer {
  constructor(container, options = {}) {
    this.container = container;
    this.options = Object.assign({
      progressDuration: 5000,
      autoPlay: true,
      loop: false,
    }, options);

    this.slides = [];
    this.currentIndex = 0;
    this.isAnimating = false;
    this.progressTimer = null;
    this.isPaused = false;

    this._init();
  }

  _init() {
    this.container.innerHTML = '';
    this.progressBar = document.createElement('div');
    this.progressBar.className = 'story-progress';
    this.container.appendChild(this.progressBar);

    this.slideContainer = document.createElement('div');
    this.slideContainer.className = 'story-slides';
    this.container.appendChild(this.slideContainer);
  }

  load(ofertas) {
    this.ofertas = ofertas || [];
    this.slides = [];
    this.currentIndex = 0;
    this.container.innerHTML = '';
    this.progressBar = document.createElement('div');
    this.progressBar.className = 'story-progress';
    this.container.appendChild(this.progressBar);

    if (this.ofertas.length === 0) {
      this._showEmpty();
      return;
    }

    this.ofertas.forEach((oferta, index) => {
      const slide = this._createSlide(oferta, index);
      this.slides.push(slide);
      this.container.appendChild(slide);

      // Barra de progresso
      const bar = document.createElement('div');
      bar.className = 'progress-bar';
      bar.innerHTML = '<div class="fill"></div>';
      this.progressBar.appendChild(bar);
    });

    this._showSlide(0);
    this._preloadNext(0);

    if (this.options.autoPlay) {
      this._startProgress();
    }
  }

  _createSlide(oferta, index) {
    const slide = document.createElement('div');
    slide.className = 'story-slide';
    slide.dataset.index = index;

    const imgContainer = document.createElement('div');
    imgContainer.className = 'story-image';

    const img = document.createElement('img');
    img.className = 'loading';
    img.alt = oferta.titulo || 'Oferta';
    img.dataset.src = oferta.imagem;
    img.loading = 'lazy';

    imgContainer.appendChild(img);

    const overlay = document.createElement('div');
    overlay.className = 'story-overlay';

    const info = document.createElement('div');
    info.className = 'story-info';

    const titulo = document.createElement('h2');
    titulo.className = 'story-titulo';
    titulo.textContent = oferta.titulo;

    const contador = document.createElement('span');
    contador.className = 'story-contador';
    contador.textContent = `${index + 1} de ${this.ofertas.length}`;

    info.appendChild(titulo);
    info.appendChild(contador);

    slide.appendChild(imgContainer);
    slide.appendChild(overlay);
    slide.appendChild(info);

    return slide;
  }

  _showSlide(index) {
    if (index < 0 || index >= this.slides.length) return;

    this.slides.forEach((slide, i) => {
      slide.classList.remove('active', 'prev', 'next');
      if (i === index) {
        slide.classList.add('active');
      } else if (i < index) {
        slide.classList.add('prev');
      } else {
        slide.classList.add('next');
      }
    });

    this.currentIndex = index;
    this._loadImage(index);
    this._updateProgress(index);

    // Atualizar contadores
    const contadores = this.container.querySelectorAll('.story-contador');
    contadores.forEach((el, i) => {
      el.textContent = `${i + 1} de ${this.slides.length}`;
    });
  }

  _loadImage(index) {
    const slide = this.slides[index];
    if (!slide) return;
    const img = slide.querySelector('img');
    if (!img || img.classList.contains('loaded')) return;

    const src = img.dataset.src;
    if (!src) return;

    const tempImg = new Image();
    tempImg.onload = () => {
      img.src = src;
      img.classList.remove('loading');
      img.classList.add('loaded');
    };
    tempImg.onerror = () => {
      img.classList.remove('loading');
      img.alt = 'Imagem indisponível';
    };
    tempImg.src = src;
  }

  _preloadNext(index) {
    const nextIndex = index + 1;
    if (nextIndex < this.ofertas.length) {
      // Preload com link rel=preload
      const oferta = this.ofertas[nextIndex];
      if (oferta.imagem) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.as = 'image';
        link.href = oferta.imagem;
        document.head.appendChild(link);
      }
    }
  }

  _updateProgress(activeIndex) {
    const bars = this.progressBar.querySelectorAll('.progress-bar');
    bars.forEach((bar, i) => {
      bar.classList.remove('active', 'done');
      const fill = bar.querySelector('.fill');
      if (fill) fill.style.width = '0%';

      if (i < activeIndex) {
        bar.classList.add('done');
        if (fill) fill.style.width = '100%';
      } else if (i === activeIndex) {
        bar.classList.add('active');
      }
    });
  }

  _startProgress() {
    this._stopProgress();
    if (this.slides.length === 0) return;

    const currentBar = this.progressBar.querySelectorAll('.progress-bar')[this.currentIndex];
    if (!currentBar) return;

    const fill = currentBar.querySelector('.fill');
    if (!fill) return;

    fill.style.width = '0%';
    // Força reflow
    void fill.offsetWidth;

    this.progressTimer = setTimeout(() => {
      fill.style.width = '100%';
      fill.style.transition = `width ${this.options.progressDuration}ms linear`;

      this.progressTimeout = setTimeout(() => {
        this.next();
      }, this.options.progressDuration);
    }, 50);
  }

  _stopProgress() {
    if (this.progressTimer) {
      clearTimeout(this.progressTimer);
      this.progressTimer = null;
    }
    if (this.progressTimeout) {
      clearTimeout(this.progressTimeout);
      this.progressTimeout = null;
    }
  }

  _showEmpty() {
    const emptyState = document.getElementById('empty-state');
    if (emptyState) {
      emptyState.classList.remove('hidden');
      emptyState.removeAttribute('aria-hidden');
    }
    const nav = document.getElementById('story-nav');
    if (nav) nav.classList.add('hidden');
  }

  // --- Navegação Pública ---

  next() {
    if (this.isAnimating) return;
    const nextIndex = this.currentIndex + 1;

    if (nextIndex >= this.slides.length) {
      if (this.options.loop) {
        this.goTo(0);
      } else {
        this._stopProgress();
      }
      return;
    }

    this._stopProgress();
    this._showSlide(nextIndex);
    this._preloadNext(nextIndex);

    if (this.options.autoPlay && !this.isPaused) {
      this._startProgress();
    }
  }

  prev() {
    if (this.isAnimating) return;
    const prevIndex = this.currentIndex - 1;
    if (prevIndex < 0) return;

    this._stopProgress();
    this._showSlide(prevIndex);

    if (this.options.autoPlay && !this.isPaused) {
      this._startProgress();
    }
  }

  goTo(index) {
    if (index < 0 || index >= this.slides.length || this.isAnimating) return;
    this._stopProgress();
    this._showSlide(index);
    this._preloadNext(index);

    if (this.options.autoPlay && !this.isPaused) {
      this._startProgress();
    }
  }

  pause() {
    this.isPaused = true;
    this._stopProgress();
  }

  resume() {
    this.isPaused = false;
    if (this.options.autoPlay) {
      this._startProgress();
    }
  }

  destroy() {
    this._stopProgress();
    this.container.innerHTML = '';
    this.slides = [];
    this.ofertas = [];
  }
}
