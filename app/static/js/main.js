document.addEventListener('DOMContentLoaded', () => {
  const body = document.body;
  const nav = document.getElementById('primary-nav');
  const toggle = document.getElementById('nav-toggle');
  const header = document.getElementById('site-header');

  if (toggle) {
    toggle.addEventListener('click', () => {
      nav.classList.toggle('open');
      toggle.classList.toggle('open');
    });
  }

  nav?.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      nav.classList.remove('open');
      toggle?.classList.remove('open');
    });
  });

  const themeMap = {
    hero: '--color-hero',
    about: '--color-about',
    cases: '--color-cases',
    services: '--color-services',
    contact: '--color-contact'
  };

  const revealTargets = document.querySelectorAll('.section, .hero, .case-card, .detail-image');
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          if (entry.target.dataset.themeColor) {
            const key = entry.target.dataset.themeColor;
            const varName = themeMap[key];
            if (varName) {
              const value = getComputedStyle(document.documentElement).getPropertyValue(varName);
              if (value) {
                body.style.setProperty('--page-bg', value.trim());
                body.dataset.activeSection = key;
              }
            }
          }
        }
      });
    },
    { threshold: 0.35 }
  );

  revealTargets.forEach((target) => revealObserver.observe(target));

  const filterButtons = document.querySelectorAll('.filter-btn');
  const caseCards = document.querySelectorAll('.case-card');
  filterButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const filter = button.dataset.filter;
      filterButtons.forEach((btn) => btn.classList.remove('active'));
      button.classList.add('active');

      caseCards.forEach((card) => {
        const category = card.dataset.category;
        const match = filter === 'all' || category === filter;
        card.style.display = match ? 'block' : 'none';
      });
    });
  });

  const updateHeader = () => {
    if (window.scrollY > 60) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  };

  updateHeader();
  window.addEventListener('scroll', updateHeader, { passive: true });
});
