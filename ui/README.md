# UI design references

Companion to [Awesome Anti-Slop](../README.md), whose main collection focuses on writing.

9 resources for interface inspiration, components and design skills. Alphabetical; no rankings or recommendations.

[catalog.json](catalog.json) records source URLs, pinned skill revisions, checksums, inspection scope and license metadata. Descriptions reflect inspected public pages or skill entries; components and generated designs were not independently evaluated. Linked designs, components and bundled references retain their own reuse terms.

## UI design

- [21st.dev](https://21st.dev/) - Community component, template and theme library with source code and prompts for coding agents. Offers free access with copy limits and paid plans; public homepage and pricing inspected.
- [Designeer](https://designeer.xyz/) - Curated catalog of interface craft, design inspiration, component libraries, tools and portfolios for designers and developers. Public homepage inspected; linked resources retain their own access and reuse terms.
- [Hallmark (Nutlope)](https://github.com/Nutlope/hallmark/blob/main/skills/hallmark/SKILL.md) - UI design skill for new websites and explicitly requested audits or redesigns, with design tokens, composition choices, accessibility checks and a bundled visual linter. Entry instructions inspected; generated results were not evaluated.
- [Inspora](https://inspora.design/) - Curated visual-design archive spanning web, branding, product, motion and illustration, with sign-in features for saving inspiration. Public homepage inspected; individual projects and underlying assets were not reviewed.
- [Magic UI](https://magicui.design/) - React, TypeScript, Tailwind CSS and Motion component library with animated effects, plus a separate Pro template offering. Public homepage inspected; component behavior and accessibility were not independently tested.
- [Mobbin](https://mobbin.com/) - Design-reference library of shipped mobile and web screens, flows, animations and UI elements, with free signup and paid plans. Public homepage inspected; account-only collections were not accessed.
- [React Bits](https://reactbits.dev/) - Animated React components, text effects, backgrounds and interactions, offered in JavaScript or TypeScript with CSS or Tailwind variants. Public library homepage inspected; components were not installed or tested.
- [Uiverse](https://uiverse.io/) - Community UI-element library with HTML/CSS, Tailwind, React and Figma options, including buttons, inputs, cards and loaders. Public homepage inspected; individual components and their reuse terms require separate review.
- [Unslop (heydamir)](https://github.com/heydamir/unslop/blob/main/skills/unslop/SKILL.md) - UI redesign skill by Damir Sokolovsky that derives a direction from the product, then reviews spacing, color, icons, copy, type, layout and motion. Distinct from prose tools named Unslop; CC BY 4.0 attribution applies.

## Contributing

Add UI resources to `ui/catalog.json` and regenerate both documents with `python3 scripts/render.py` from the repository root. Keep source attribution and inspection limits. Run `mise run check` to validate both collections, generated documents and links.
