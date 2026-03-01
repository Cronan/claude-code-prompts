---
name: jsx-artifact
description: |
  Generate self-contained JSX artifacts -- single-file React components
  styled with Tailwind CSS, rendered in the browser with no build step.
  Produces standalone HTML files that work on any platform with a browser,
  including headless Linux and Raspberry Pi. No Node.js, npm, or toolchain
  required.
user-invocable: true
disable-model-invocation: true
context: fork
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
---

# Generate a self-contained JSX artifact

You are building a single-file interactive artifact. The output is one HTML file that opens directly in a browser. No build step. No toolchain. No server.

The file must work on any machine with a modern browser: a developer laptop, a headless Linux box, a Raspberry Pi running Chromium. Do not assume Node.js, npm, or any local tooling exists.

## What you produce

A single `.html` file containing:

1. A `<script>` loading React 18 and ReactDOM from CDN (unpkg or cdnjs)
2. A `<script>` loading Babel standalone for in-browser JSX transformation
3. A `<script>` loading Tailwind CSS Play CDN
4. Optional: Recharts and/or Lucide React icons from CDN, only if needed
5. A `<script type="text/babel">` block with your component code
6. A mount point `<div id="root">` and a `ReactDOM.createRoot` call

Everything lives in one file. No imports from local paths. No fetch calls to external APIs. No asset files.

## CDN loading order

Place these in `<head>`, in this order:

```html
<script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
<script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js" crossorigin></script>
<script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
<script src="https://cdn.tailwindcss.com"></script>
```

Add these only when the component uses them:

```html
<!-- Data visualization -->
<script src="https://unpkg.com/recharts@2/umd/Recharts.js"></script>

<!-- Icons -->
<script src="https://unpkg.com/lucide-react@latest/dist/umd/lucide-react.js"></script>
```

Do not load libraries the component does not use.

## Accessing CDN-loaded libraries

Libraries loaded via CDN expose globals, not ES modules. Access them through their global names:

```jsx
const { useState, useEffect, useRef, useMemo, useCallback } = React;
const { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } = Recharts;
const { Search, Menu, X, ChevronDown } = lucide;
```

Do not use `import` statements. They will fail. Destructure from the global object at the top of your script block.

## Tailwind configuration

Configure Tailwind in a script block before the component code:

```html
<script>
  tailwind.config = {
    darkMode: 'class',
    theme: {
      extend: {
        colors: {
          // custom palette if needed
        }
      }
    }
  }
</script>
```

Add the `dark` class to `<html>` for dark mode (the default):

```html
<html lang="en" class="dark">
```

## Component rules

### Structure

Write a single top-level `App` component. Define helper components in the same script block above `App`. Use functional components exclusively. Use hooks for state.

```jsx
const StatusBadge = ({ status }) => {
  const colors = {
    active: 'bg-emerald-500/20 text-emerald-400',
    idle: 'bg-zinc-500/20 text-zinc-400',
    error: 'bg-red-500/20 text-red-400',
  };
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${colors[status] || colors.idle}`}>
      {status}
    </span>
  );
};

const App = () => {
  // ...
};

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
```

### Dark theme

Dark theme is the default. Design for dark first, light second.

Background hierarchy for dark mode:
- Page: `bg-zinc-950` or `bg-gray-950`
- Card/panel: `bg-zinc-900` or `bg-gray-900`
- Elevated surface: `bg-zinc-800` or `bg-gray-800`
- Input/well: `bg-zinc-800/50`
- Hover: `bg-zinc-700/50`

Text hierarchy:
- Primary: `text-zinc-100`
- Secondary: `text-zinc-400`
- Muted: `text-zinc-500`
- On accent: `text-white`

Borders: `border-zinc-800` or `border-zinc-700/50`

Accent colors: use the Tailwind palette. `emerald` for success, `red` for error, `amber` for warning, `blue` or `violet` for primary actions.

### Layout

Set the body to fill the viewport:

```html
<body class="bg-zinc-950 text-zinc-100 min-h-screen">
  <div id="root"></div>
</body>
```

Use flexbox and grid for layout. Common patterns:

- Sidebar + main: `flex min-h-screen` with a fixed-width sidebar and `flex-1` main area
- Dashboard grid: `grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4`
- Centered content: `flex items-center justify-center min-h-screen`

### Responsiveness

Design for three breakpoints: mobile (default), tablet (`md:`), desktop (`lg:`). Layouts should not break on a 1024x600 screen (common Raspberry Pi resolution). Test mentally at 800px and 1280px widths.

Avoid fixed widths. Use `max-w-` constraints with `mx-auto` for centered content. Use `overflow-x-auto` on tables and wide content.

### Data

Use hardcoded mock data defined as constants at the top of the script block. Make the data realistic and internally consistent. Name the constants descriptively:

```jsx
const SENSOR_READINGS = [
  { time: '00:00', temp: 21.3, humidity: 45 },
  { time: '04:00', temp: 19.8, humidity: 52 },
  // ...
];
```

Do not fetch from external URLs. Do not use `localStorage` or `sessionStorage`. The artifact is stateless across page loads.

State within a session (tab filters, search input, toggled panels) is fine and expected. Use `useState`.

### Images and icons

Do not reference external image URLs. Use inline SVGs for custom graphics. Use Lucide icons when available (load the CDN script). For placeholder images, use colored `<div>` elements with Tailwind backgrounds, not broken `<img>` tags.

### Interactivity

Common interactive patterns that work well in artifacts:

- Tabs and filters: `useState` for active tab, conditional rendering
- Search/filter: `useState` for query, `useMemo` for filtered results
- Expandable sections: `useState` for open/closed, height transition with Tailwind
- Sort controls: `useState` for sort key and direction
- Hover states: Tailwind `hover:` and `group-hover:` utilities

Avoid patterns that need a backend: form submission, authentication, real-time updates, WebSocket connections.

### Animation

Keep animations minimal. Use Tailwind transitions: `transition-all duration-200`, `transition-colors`, `hover:scale-105`. Avoid layout-thrashing animations. Do not use `requestAnimationFrame` loops unless the component is explicitly a visualization or game.

## What not to do

- Do not use `import` or `export` statements. CDN globals only.
- Do not use TypeScript syntax. Babel standalone does not transform it by default.
- Do not call external APIs or fetch remote data.
- Do not use `localStorage`, `sessionStorage`, or cookies.
- Do not load images from URLs. Inline SVGs or CSS-only graphics.
- Do not assume a specific screen resolution. Be responsive.
- Do not use `class` components. Functional components with hooks only.
- Do not use CSS-in-JS libraries. Tailwind covers styling.
- Do not add `<meta charset>` or viewport tags that conflict with the HTML defaults. Include standard ones:

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

## Platform considerations

The artifact must render correctly on:

- Chromium on Raspberry Pi OS (ARM, limited GPU, 1024x600 common)
- Firefox and Chrome on desktop Linux
- Safari on macOS
- Chrome/Edge on Windows

Practical constraints for low-powered hardware:

- Limit DOM node count. Avoid rendering hundreds of list items; paginate or virtualize.
- Prefer CSS transitions over JavaScript animation.
- Avoid `box-shadow` stacking and heavy `backdrop-blur` on large surfaces; these are GPU-intensive. Use sparingly.
- Keep Recharts datasets under 100 points. Large datasets cause visible lag on a Pi.
- Test your assumptions: if a Pi with 1GB RAM is running Chromium, a page using 200MB of JavaScript will swap.

## Offline fallback

If the user asks for an offline-capable artifact, include the library source inline instead of using CDN links. This makes the file larger but removes the network dependency. Use this approach only when requested; CDN links are preferred for file size.

When inlining is not practical (Recharts is 300KB+ minified), note the dependency and suggest the user pre-download the scripts to a local path. Provide the URLs.

## Reference files

Before writing complex artifacts, read the reference material in this skill directory:

- For component layout patterns and recurring UI structures, read `references/patterns.md`.
- For Tailwind dark theme tokens and spacing conventions, read `references/tailwind-guide.md`.
- For a complete working example, read `examples/example-dashboard.html`.
