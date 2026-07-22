/* ============================================
   App — Inicialização do visualizador de Stories
   ============================================ */

(function () {
  'use strict';

  const config = window.OfertasConfig || {};

  function init() {
    const container = document.getElementById('story-container');
    if (!container) {
      console.error('Container #story-container não encontrado.');
      return;
    }

    const viewer = new StoryViewer(container, {
      progressDuration: 5000,
      autoPlay: true,
      loop: false,
    });

    // Inicializar gestos
    const gestures = new GestureController(viewer);

    // Botões de navegação
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    if (btnPrev) {
      btnPrev.addEventListener('click', () => viewer.prev());
    }
    if (btnNext) {
      btnNext.addEventListener('click', () => viewer.next());
    }

    // Carregar ofertas
    fetch(config.ofertasUrl || 'ofertas.json')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        viewer.load(data);

        // Mostrar navegação se houver ofertas
        const nav = document.getElementById('story-nav');
        if (nav && data.length > 0) {
          nav.classList.remove('hidden');
        }
      })
      .catch(err => {
        console.error('Erro ao carregar ofertas:', err);
        viewer.load([]);
      });

    // Expor para debug
    window.__viewer = viewer;
  }

  // Aguardar DOM pronto
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
