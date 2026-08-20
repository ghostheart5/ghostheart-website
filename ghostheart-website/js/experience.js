document.documentElement.classList.add("js");

const body = document.body;
const menuToggle = document.querySelector("[data-menu-toggle]");
const siteNav = document.querySelector("[data-site-nav]");

function closeMenu() {
  body.classList.remove("menu-open");
  menuToggle?.setAttribute("aria-expanded", "false");
}

menuToggle?.addEventListener("click", () => {
  const open = body.classList.toggle("menu-open");
  menuToggle.setAttribute("aria-expanded", String(open));
});

siteNav?.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
window.addEventListener("resize", () => {
  if (window.innerWidth >= 940) closeMenu();
});

const page = body.dataset.page;
document.querySelectorAll("[data-nav]").forEach((link) => {
  if (link.dataset.nav === page) {
    link.classList.add("active");
    link.setAttribute("aria-current", "page");
  }
});

document.querySelectorAll("[data-year]").forEach((node) => {
  node.textContent = String(new Date().getFullYear());
});

const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const revealNodes = document.querySelectorAll(".reveal");
if (!reducedMotion && "IntersectionObserver" in window) {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("in-view");
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: .12, rootMargin: "0px 0px -7%" });
  revealNodes.forEach((node) => observer.observe(node));
} else {
  revealNodes.forEach((node) => node.classList.add("in-view"));
}

const emberField = document.querySelector("[data-embers]");
if (emberField && !reducedMotion) {
  for (let i = 0; i < 18; i += 1) {
    const ember = document.createElement("span");
    ember.className = "ember";
    ember.style.left = `${Math.random() * 100}%`;
    ember.style.setProperty("--size", `${1 + Math.random() * 2.5}px`);
    ember.style.setProperty("--speed", `${11 + Math.random() * 14}s`);
    ember.style.setProperty("--delay", `${Math.random() * 15}s`);
    emberField.appendChild(ember);
  }
}

const search = document.querySelector("[data-quote-search]");
const filters = Array.from(document.querySelectorAll("[data-filter]"));
const quoteCards = Array.from(document.querySelectorAll("[data-quote]"));
const empty = document.querySelector("[data-empty]");
let category = "all";

function filterQuotes() {
  const term = search?.value.trim().toLowerCase() || "";
  let count = 0;
  quoteCards.forEach((card) => {
    const categories = (card.dataset.category || "").split(",");
    const content = card.textContent.toLowerCase();
    const visible = (category === "all" || categories.includes(category)) && (!term || content.includes(term));
    card.classList.toggle("hidden", !visible);
    if (visible) count += 1;
  });
  empty?.classList.toggle("hidden", count !== 0);
}

search?.addEventListener("input", filterQuotes);
filters.forEach((filter) => {
  filter.addEventListener("click", () => {
    category = filter.dataset.filter || "all";
    filters.forEach((item) => item.classList.toggle("active", item === filter));
    filterQuotes();
  });
});
filterQuotes();
