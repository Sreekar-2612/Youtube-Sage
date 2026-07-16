---
name: Munich Minimalist
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f4'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#444748'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f0f1f1'
  outline: '#747878'
  outline-variant: '#c4c7c7'
  surface-tint: '#5f5e5e'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#1c1b1b'
  on-primary-container: '#858383'
  inverse-primary: '#c8c6c5'
  secondary: '#5d5f5f'
  on-secondary: '#ffffff'
  secondary-container: '#dcdddd'
  on-secondary-container: '#5f6161'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#1a1c1c'
  on-tertiary-container: '#838484'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e5e2e1'
  primary-fixed-dim: '#c8c6c5'
  on-primary-fixed: '#1c1b1b'
  on-primary-fixed-variant: '#474746'
  secondary-fixed: '#e2e2e2'
  secondary-fixed-dim: '#c6c6c7'
  on-secondary-fixed: '#1a1c1c'
  on-secondary-fixed-variant: '#454747'
  tertiary-fixed: '#e3e2e2'
  tertiary-fixed-dim: '#c7c6c6'
  on-tertiary-fixed: '#1a1c1c'
  on-tertiary-fixed-variant: '#464747'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  display-lg:
    fontFamily: Syne
    fontSize: 80px
    fontWeight: '400'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Syne
    fontSize: 48px
    fontWeight: '400'
    lineHeight: '1.2'
    letterSpacing: 0.05em
  headline-lg-mobile:
    fontFamily: Syne
    fontSize: 32px
    fontWeight: '400'
    lineHeight: '1.2'
    letterSpacing: 0.05em
  headline-md:
    fontFamily: Syne
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.3'
    letterSpacing: 0.1em
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: 0.01em
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Hanken Grotesk
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1.4'
    letterSpacing: 0.15em
spacing:
  unit: 8px
  container-max: 1280px
  gutter: 32px
  margin-desktop: 64px
  margin-mobile: 20px
  stack-lg: 80px
  stack-md: 40px
---

## Brand & Style
This design system is built upon the principles of European high-fashion editorial: architectural clarity, airy negative space, and a refined, disciplined aesthetic. It evokes a sense of quiet luxury and intellectual sophistication, targeting an audience that values substance over ornament.

The visual style is **Minimalist with High-Contrast Editorial influences**. It utilizes a "less but better" approach, where every pixel is intentional. The interface relies on hairline-thin borders, expansive white space to create "breathing room," and sharp typography to establish hierarchy without the need for heavy decorative elements. The emotional response is one of calm, professional confidence and timeless modernism.

## Colors
The palette is monochromatic and atmospheric, drawing from architectural materials like limestone, fog, and charcoal.

- **Primary (#1A1A1A):** A deep, off-black used for primary text and structural hairlines. It provides the necessary "bite" against the light backgrounds.
- **Secondary (#F5F5F5):** A soft, cool grey used for subtle surface differentiation and secondary containers.
- **Tertiary (#A0A0A0):** A mid-tone grey reserved for disabled states, placeholder text, and secondary labels.
- **Neutral (#FFFFFF):** The foundation of the system. White is used aggressively to create an "airy" feel and to allow imagery to stand out.

Color should be used sparingly. Functional color (e.g., success or error) should be desaturated to maintain the sophisticated mood.

## Typography
The typography strategy is defined by high contrast in scale and tracking. **Syne** is utilized for headlines to mimic the thin, elongated, and avant-garde letterforms seen in the reference "MUNICH" text. **Hanken Grotesk** provides a clean, modern, and highly legible counterpoint for body copy.

- **Headlines:** Should use wide letter-spacing (tracking) for a gallery-like feel.
- **Body:** Set with generous line heights to ensure the text feels uncrowded and "airy."
- **Labels:** Always set in uppercase with increased letter-spacing to act as architectural markers within the UI.

## Layout & Spacing
The layout follows a **Fixed Grid** philosophy on desktop to maintain rigorous alignment, transitioning to a fluid model on mobile.

- **Grid:** A 12-column grid with wide 32px gutters creates a spacious, structured framework.
- **Vertical Rhythm:** Large "Stack" spacings (80px+) are used between major sections to emphasize the focus on negative space.
- **Breakpoints:**
  - **Desktop (1280px+):** Centered container with 64px outer margins.
  - **Tablet (768px - 1279px):** 8-column grid with 32px margins.
  - **Mobile (0 - 767px):** 4-column fluid grid with 20px margins; headlines scale down to ensure readability.

## Elevation & Depth
In keeping with the minimalist and thin-bordered aesthetic, this design system rejects heavy shadows and skeuomorphism.

- **Low-Contrast Outlines:** Hierarchy is established through 1px solid borders in `#1A1A1A` (for focus/active states) or `#E0E0E0` (for standard containers).
- **Tonal Layers:** Subtle depth is created by placing white cards on `#F5F5F5` backgrounds. 
- **Absence of Shadows:** Do not use drop shadows. Instead, use "ghost" borders and stark color blocks to define edges. If a hover state requires depth, use a slight background color shift or a thickening of the border from 1px to 2px.

## Shapes
The shape language is strictly **Sharp (0px)**. 

All buttons, input fields, cards, and image containers must have 90-degree corners. This reinforces the architectural and "high-fashion" precision of the brand. Rounded corners are inconsistent with this design narrative and should be avoided entirely, except for circular elements like avatars or specific icon containers where a square would be functionally detrimental.

## Components
- **Buttons:** Primary buttons are solid `#1A1A1A` with white uppercase text. Secondary buttons use a 1px border with no fill. All buttons have a sharp-cornered, rectangular profile.
- **Input Fields:** Minimalist design featuring only a 1px bottom border that transitions to a full 1px box on focus. Labels should be small and uppercase, floating above the field.
- **Cards:** Defined by 1px light grey borders and generous internal padding (32px+). Content within cards should follow the same high-contrast typographic rules.
- **Chips/Tags:** Small, rectangular boxes with 1px borders and `label-sm` typography. 
- **Lists:** Separated by 1px horizontal hairlines that span the full width of the container, emphasizing the linear nature of the design.
- **Imagery:** Photography should be desaturated or high-key to match the airy palette. Images should always be framed in sharp-edged containers.