const yearTargets = document.querySelectorAll("#year");
yearTargets.forEach((target) => {
  target.textContent = new Date().getFullYear();
});

document.body.classList.add("js-enabled");

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const topbar = document.querySelector(".gh-nav");
const menuToggle = document.querySelector(".menu-toggle");
const nav = document.querySelector("#primary-nav");
const navLinks = nav ? Array.from(nav.querySelectorAll("a[href^='#']")) : [];

if (menuToggle && nav) {
  menuToggle.addEventListener("click", () => {
    const isOpen = nav.classList.toggle("open");
    menuToggle.setAttribute("aria-expanded", String(isOpen));
  });

  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      nav.classList.remove("open");
      menuToggle.setAttribute("aria-expanded", "false");
    });
  });
}

document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", (event) => {
    const targetId = anchor.getAttribute("href");
    if (!targetId || targetId === "#") return;

    const target = document.querySelector(targetId);
    if (!target) return;

    event.preventDefault();
    const offset = topbar ? topbar.getBoundingClientRect().height + 14 : 0;
    const top = target.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top, behavior: reducedMotion ? "auto" : "smooth" });
  });
});

const revealTargets = document.querySelectorAll(".reveal");
revealTargets.forEach((target, index) => {
  target.style.setProperty("--reveal-delay", `${index * 95}ms`);
});

if (!reducedMotion && "IntersectionObserver" in window && revealTargets.length) {
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in-view");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    {
      root: null,
      threshold: 0.15,
      rootMargin: "0px 0px -10% 0px",
    }
  );

  revealTargets.forEach((target) => revealObserver.observe(target));
} else {
  revealTargets.forEach((target) => target.classList.add("in-view"));
}

const sections = Array.from(document.querySelectorAll("section[data-section]"));
if (sections.length && navLinks.length) {
  const markActiveLink = (id) => {
    navLinks.forEach((link) => {
      const isMatch = link.getAttribute("href") === `#${id}`;
      link.classList.toggle("active", isMatch);
      if (isMatch) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  };

  const sectionObserver = new IntersectionObserver(
    (entries) => {
      const active = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (active?.target?.id) {
        markActiveLink(active.target.id);
      }
    },
    {
      root: null,
      threshold: [0.3, 0.55, 0.75],
      rootMargin: "-24% 0px -42% 0px",
    }
  );

  sections.forEach((section) => sectionObserver.observe(section));
  markActiveLink(sections[0].id);
}

const signupForm = document.querySelector(".signup-form");
const statusText = document.querySelector("#form-status");

if (signupForm && statusText) {
  signupForm.addEventListener("submit", (event) => {
    event.preventDefault();
    const emailInput = signupForm.querySelector("input[type='email']");
    const email = emailInput ? emailInput.value.trim() : "";
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!emailPattern.test(email)) {
      statusText.textContent = "Please enter a valid email address before joining the signal.";
      return;
    }

    statusText.textContent = "You are in. New GhostHeart signals will find you.";
    signupForm.reset();
  });
}

const particleField = document.querySelector("#particles");
if (particleField && !reducedMotion) {
  const particleCount = 20;
  for (let index = 0; index < particleCount; index += 1) {
    const particle = document.createElement("span");
    particle.className = "particle";

    const size = (Math.random() * 2.2 + 1.1).toFixed(2);
    const left = (Math.random() * 100).toFixed(2);
    const delay = (Math.random() * 12).toFixed(2);
    const duration = (Math.random() * 10 + 16).toFixed(2);

    particle.style.setProperty("--size", `${size}px`);
    particle.style.setProperty("--delay", `${delay}s`);
    particle.style.setProperty("--duration", `${duration}s`);
    particle.style.left = `${left}%`;
    particle.style.bottom = `${-12 - Math.random() * 30}%`;

    particleField.appendChild(particle);
  }
}

const parallaxTargets = Array.from(document.querySelectorAll(".parallax"));
if (!reducedMotion && parallaxTargets.length) {
  let rafId = null;

  const updateParallax = () => {
    const viewportCenter = window.innerHeight * 0.5;

    parallaxTargets.forEach((element) => {
      const rect = element.getBoundingClientRect();
      const depth = Number(element.dataset.depth || 0.05);
      const distanceFromCenter = rect.top + rect.height * 0.5 - viewportCenter;
      const shift = distanceFromCenter * depth * -0.18;
      element.style.transform = `translate3d(0, ${shift.toFixed(2)}px, 0)`;
    });

    rafId = null;
  };

  const requestTick = () => {
    if (rafId === null) {
      rafId = window.requestAnimationFrame(updateParallax);
    }
  };

  window.addEventListener("scroll", requestTick, { passive: true });
  window.addEventListener("resize", requestTick);
  requestTick();
}
