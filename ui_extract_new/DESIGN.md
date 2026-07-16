---
name: High-Contrast Tech Narrative
colors:
  surface: '#f9f9f9'
  surface-dim: '#dadada'
  surface-bright: '#f9f9f9'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f3f3'
  surface-container: '#eeeeee'
  surface-container-high: '#e8e8e8'
  surface-container-highest: '#e2e2e2'
  on-surface: '#1a1c1c'
  on-surface-variant: '#3d494b'
  inverse-surface: '#2f3131'
  inverse-on-surface: '#f1f1f1'
  outline: '#6d797c'
  outline-variant: '#bcc9cc'
  surface-tint: '#006876'
  primary: '#006876'
  on-primary: '#ffffff'
  primary-container: '#00acc1'
  on-primary-container: '#003a42'
  inverse-primary: '#55d7ed'
  secondary: '#b81311'
  on-secondary: '#ffffff'
  secondary-container: '#dc3128'
  on-secondary-container: '#fffbff'
  tertiary: '#8d4f00'
  on-tertiary: '#ffffff'
  tertiary-container: '#da8a36'
  on-tertiary-container: '#502b00'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#9eefff'
  primary-fixed-dim: '#55d7ed'
  on-primary-fixed: '#001f24'
  on-primary-fixed-variant: '#004e59'
  secondary-fixed: '#ffdad5'
  secondary-fixed-dim: '#ffb4a9'
  on-secondary-fixed: '#410001'
  on-secondary-fixed-variant: '#930005'
  tertiary-fixed: '#ffdcc0'
  tertiary-fixed-dim: '#ffb875'
  on-tertiary-fixed: '#2d1600'
  on-tertiary-fixed-variant: '#6b3b00'
  background: '#f9f9f9'
  on-background: '#1a1c1c'
  surface-variant: '#e2e2e2'
typography:
  display-lg:
    fontFamily: Montserrat
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Montserrat
    fontSize: 32px
    fontWeight: '800'
    lineHeight: 38px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Montserrat
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  body-lg:
    fontFamily: Montserrat
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Montserrat
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-technical:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.05em
  button-text:
    fontFamily: Montserrat
    fontSize: 14px
    fontWeight: '700'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
  max-width: 1280px
---

## Brand & Style

This design system is engineered for high-performance technology environments, blending high-contrast modernism with a precise, geometric aesthetic. The brand personality is assertive, technical, and high-energy, designed to evoke a sense of speed and reliability. 

The visual style utilizes a **High-Contrast / Bold** framework. It features heavy reliance on saturated accent colors against clean, architectural surfaces. The interface is characterized by deliberate white space, razor-sharp alignment, and punchy typographic hierarchies that communicate authority and technical sophistication.

## Colors

The palette is anchored by a high-intensity Teal primary for actions and progress, and an Orange-Red secondary for alerts, highlights, and critical data points. 

Surfaces are strictly limited to pure White (#FFFFFF) for primary containers and Light Grey (#F5F5F5) for secondary background layering to create a "punched-out" effect for UI elements. Text and iconography utilize a deep charcoal-black to maintain maximum legibility and visual weight.

## Typography

The typography system relies on the bold, geometric weights of **Montserrat** for all major interface elements, creating a strong vertical rhythm. To reinforce the tech-focused narrative, **JetBrains Mono** is introduced for small labels, data points, and technical metadata to provide a functional, "code-like" contrast. 

Headlines should be set with tight tracking to emphasize their block-like, geometric quality. Large display styles are reserved for desktop hero sections and must scale down significantly for mobile to maintain a compact, high-information-density layout.

## Layout & Spacing

The layout follows a strict **Fixed Grid** model on desktop and a fluid 4-column layout on mobile. Spacing is based on a rigid 4px baseline grid to ensure mathematical precision between elements.

- **Desktop:** 12-column grid, 1280px max-width, 24px gutters.
- **Tablet:** 8-column grid, 24px gutters, 24px side margins.
- **Mobile:** 4-column grid, 16px gutters, 16px side margins.

Use generous external margins to separate distinct content blocks, but maintain tight internal padding within components to reflect the efficient, technical nature of the system.

## Elevation & Depth

Hierarchy is achieved through **Low-Contrast Outlines** and tonal layering rather than traditional shadows. 

- **Level 0 (Background):** Light Grey (#F5F5F5).
- **Level 1 (Cards/Containers):** White (#FFFFFF) with a 1px solid border (#E0E0E0).
- **Active State:** Elements receive a 2px solid border using the Primary Teal.
- **Depth:** Avoid blurs. Instead, use "Hard Shadows" (offset 4px, 0% blur) in the secondary color for unique hover states on buttons to mimic a tactile, retro-tech feel.

## Shapes

The shape language is strictly **Soft** but leaning towards "Sharp." Standard UI components use a 4px (0.25rem) radius to prevent the interface from feeling aggressive while maintaining a precise, engineered appearance. 

Interactive elements like buttons and input fields must never exceed a 4px radius. Circular shapes are only permitted for status indicators and user avatars.

## Components

### Buttons
- **Primary:** Solid Teal background, White text, Bold/Uppercase, 4px radius. 
- **Secondary:** Solid Orange-Red background, White text, for high-priority actions.
- **Tertiary:** Transparent background, 1px Black border, Black text.

### Input Fields
- White background with a 1px Grey border. On focus, the border thickens to 2px Primary Teal. Labels use JetBrains Mono for a technical look.

### Cards
- White background, 1px solid border, 4px radius. Header areas should often have a Light Grey background to separate them from the card body.

### Lists & Data
- Use "Zebra-striping" with Light Grey and White for data-heavy tables. Borders should be minimal, favoring vertical alignment to guide the eye.

### Chips/Tags
- Small, rectangular with a 2px radius. Use Light Grey backgrounds with Bold text for categorizing technical data.