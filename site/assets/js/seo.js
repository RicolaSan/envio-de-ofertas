/* ============================================
   SEO — Metadados dinâmicos e Structured Data
   ============================================ */

(function () {
  'use strict';

  const config = window.OfertasConfig || {};

  function injectStructuredData(ofertas) {
    const siteName = document.title || 'Ofertas';

    const baseData = {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: siteName,
      description: document.querySelector('meta[name="description"]')?.content || '',
    };

    if (ofertas && ofertas.length > 0) {
      baseData.mainEntity = {
        '@type': 'ItemList',
        itemListElement: ofertas.map((oferta, index) => ({
          '@type': 'ListItem',
          position: index + 1,
          item: {
            '@type': 'Product',
            name: oferta.titulo,
            image: oferta.imagem,
          },
        })),
      };
    }

    const script = document.createElement('script');
    script.type = 'application/ld+json';
    script.textContent = JSON.stringify(baseData, null, 2);
    document.head.appendChild(script);
  }

  // Hook no carregamento das ofertas para injetar dados estruturados
  const originalFetch = window.fetch;
  window.fetch = function (...args) {
    return originalFetch.apply(this, args).then(response => {
      if (typeof args[0] === 'string' && args[0].includes('ofertas.json')) {
        const cloned = response.clone();
        cloned.json().then(data => {
          if (data && data.length > 0) {
            injectStructuredData(data);
          }
        }).catch(() => {});
      }
      return response;
    });
  };

  // Fallback: injetar após carregamento via app.js
  document.addEventListener('DOMContentLoaded', () => {
    const observer = new MutationObserver(() => {
      if (document.querySelector('.story-slide.active')) {
        const ofertas = window.__viewer?.ofertas;
        if (ofertas && ofertas.length > 0 && !document.querySelector('script[type="application/ld+json"]')) {
          injectStructuredData(ofertas);
        }
        observer.disconnect();
      }
    });

    observer.observe(document.getElementById('story-container') || document.body, {
      childList: true,
      subtree: true,
    });
  });
})();
