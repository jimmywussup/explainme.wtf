# FEAT-003: Public Landing Page {#root}

## 1. Goal {#landing.goal}
Create a high-converting, visually stunning landing page to distribute the compiled WordExplainer `.exe`. The site will be static Html/CSS/JS.

## 2. Aesthetic Architecture {#landing.design}
- **Theme**: Dark Mode default (background `#0B0F19`), neon accents (electric blue `#00F2FE` and purple `#4FACFE`).
- **Typography**: Inter or Roboto (Google Fonts).
- **Structure**:
    - **Hero Section**: Eye-catching h1 ("Understand any word instantly."), subtitle, and a primary CTA ("Download for Windows"). Include a stylized mockup image of the popup over a blurred code/browser background.
    - **Features**: 3-column grid highlighting "Instant Translation", "Follow-up Chat", "Works Anywhere".
    - **How it Works**: Simple 1-2-3 steps (Highlight -> Hotkey -> Meaning).
    - **Footer**: Copyright, Privacy Policy links.

## 3. Interactivity {#landing.js}
- Pure Vanilla JS for scroll animations (IntersectionObserver to fade elements in).
- Hover effects on buttons (glow effects, slight scale up).

## 4. Implementation Details {#landing.files}
- Placed in `landing_page/` directory.
- `index.html` (Semantic HTML5)
- `index.css` (Vanilla CSS, custom properties for variables, flexbox/grid layouts)
