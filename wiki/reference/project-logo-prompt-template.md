# Project logo prompt template and asset conventions

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Reusable prompt and output contract for creating one coherent logo family
for a software project.

## Invocation model

The meta-prompt is invoked directly in a language-model conversation. Its
approved output is then passed to an image generator. Logo-sheet extraction is
invoked separately through the `isolate-logos` skill or its Python
implementation; it is never an automatic implementation or release step.

## Required inputs

| Input | Required | Value |
| --- | --- | --- |
| Project name | yes | Human-readable project name |
| Project slug | yes | Lowercase filename component, normally words joined with dashes |
| Project description | yes | Purpose, value, and major responsibilities |
| Audience | recommended | People who should recognize and understand the identity |
| Main themes | optional | Three to five durable, distinct responsibilities; may be inferred |
| Brand personality | recommended | Adjectives such as reliable, playful, technical, or welcoming |
| Colors | optional | Existing hexadecimal brand colors, or a request to propose a palette |
| Elements to avoid | optional | Symbols, styles, colors, and visual clichés that are unsuitable |

## Reusable meta-prompt

Replace every bracketed value, then send the complete prompt to a language
model. Its output becomes the project's `wiki/assets/logo-prompts.md`.

```text
You are an art director specializing in visual identities for software
projects.

Create a coherent family of logo prompts from the project information below.
The family must contain one logo per major project theme and one project-wide
emblem that combines the themes.

PROJECT NAME:
[Human-readable project name]

PROJECT SLUG:
[lowercase-project-slug]

PROJECT DESCRIPTION:
[Short description, selected README sections, or value proposition]

AUDIENCE:
[Intended users]

MAIN THEMES OR FEATURES:
[Optional list of three to five themes. If absent, infer the most durable and
distinct themes from the project description.]

BRAND PERSONALITY:
[For example: technical, welcoming, reliable, playful, minimal]

COLORS:
[Hexadecimal brand colors, or "propose a palette"]

ELEMENTS TO AVOID:
[Unsuitable symbols, styles, colors, or visual clichés]

Produce a Markdown document named `logo-prompts.md` with these sections:

1. "Visual identity summary": state the identity in one short paragraph.
2. "Palette": list each color, hexadecimal value, and role.
3. "Shared style block": write one English block that will be appended
   verbatim to every theme prompt.
4. "Theme prompts": create between three and five numbered themes. For each
   theme, give its name, one sentence explaining the visual metaphor, and one
   English image-generation concept block.
5. "Combined project emblem": explain the unifying composition, then give one
   English image-generation concept block.
6. "Complete logo-sheet prompt": combine the approved concepts and shared
   style into one English prompt for a uniform grid containing every theme
   logo and the combined emblem.
7. "Generated file names": map every theme and the combined emblem to opaque
   and transparent PNG filenames.

Apply these rules:

- Separate semantic content from rendering style. Theme blocks describe what
  appears; the shared style block describes how the entire family is drawn.
- Select durable project responsibilities, not temporary implementation
  details.
- Give each theme one distinct, concrete visual metaphor.
- Prefer project-specific actions and relationships over generic gears,
  shields, clouds, light bulbs, code brackets, or robots.
- Keep one dominant silhouette per logo.
- Make every logo recognizable at 64 by 64 pixels.
- Use the same palette, line weight, geometry, detail level, and margins.
- Use a flat 2D vector-logo appearance with bold rounded outlines, simple
  geometric shapes, minimal detail, and crisp edges.
- Center each composition on a square white or near-white canvas.
- Use generous empty space around every logo.
- Include no text, letters, numbers, captions, signatures, or watermarks.
- Avoid photorealism, mockups, complex scenes, and decorative backgrounds.
- Treat the combined emblem as one simple composition, not a collage.
- If information is missing, state the smallest necessary assumption instead
  of inventing project capabilities.

The complete logo-sheet prompt must additionally require:

- a uniform grid with a stated row and column count;
- exactly one centered logo in each cell;
- the combined emblem in the final cell in reading order;
- equal cell sizes and generous separation between cells;
- no cell borders, labels, legends, repeated logos, or empty decoration;
- a uniform white or near-white background suitable for later removal.

Use this filename convention:

- combined opaque: `logo-[project-slug].png`
- combined transparent: `logo-[project-slug]-transparent.png`
- theme opaque: `logo-[project-slug]-[theme-slug].png`
- theme transparent: `logo-[project-slug]-[theme-slug]-transparent.png`

Return only the Markdown document.
```

## Prompt composition contract

Each individual image-generation prompt has this exact logical order:

```text
[Theme-specific concept block]

[Shared style block]
```

The concept block specifies the subject, action, relationship, and semantic
meaning. The shared block specifies palette, rendering style, geometry,
background, canvas, margins, and exclusions. The shared block is appended
verbatim; it is not paraphrased separately for each theme.

## Default shared style block

Use this block when a project has no established visual language:

```text
Flat 2D vector-logo appearance, sticker style, no text, letters, numbers,
captions, signatures, or watermarks. One dominant silhouette, bold rounded
outlines, simple geometric shapes, minimal detail, and crisp edges. Use only
the approved project palette. Plain white or near-white background, centered
composition, generous margins, square canvas, recognizable at 64x64 pixels.
No photorealism, mockup, complex scene, decorative background, or drop shadow.
```

Replace "approved project palette" with the selected colors and hexadecimal
values before generation.

## Logo-sheet contract

| Property | Requirement |
| --- | --- |
| Cell order | Reading order, left to right and then top to bottom |
| Cell count | One per theme plus one combined emblem |
| Grid | Uniform cells with an explicitly stated row and column count |
| Composition | Exactly one centered logo per cell |
| Spacing | Enough white space to prevent artwork crossing a cell boundary |
| Combined emblem | Final occupied cell |
| Background | Uniform white or near-white |
| Forbidden content | Dividers, captions, legends, mockups, repeated logos, decorative scenery |

When the cell count does not fill the final row, leave unused cells genuinely
empty and represent them as `-` in the isolation names list.

## Asset filenames

| Asset | Filename |
| --- | --- |
| Project emblem, opaque | `logo-<project>.png` |
| Project emblem, transparent | `logo-<project>-transparent.png` |
| Theme, opaque | `logo-<project>-<theme>.png` |
| Theme, transparent | `logo-<project>-<theme>-transparent.png` |
| Prompt record | `wiki/assets/logo-prompts.md` |

Use lowercase ASCII slugs with words separated by `-`. Keep the combined
emblem's basename free of a `-combined` suffix.

## Isolation command

```text
uv run --with pillow python <llm-shared>/tools/isolate_logos/isolate_logos.py SHEET.png --out-dir OUTPUT_DIR --cols COLUMN_COUNT --names CELL_NAMES --prefix logo-PROJECT
```

`CELL_NAMES` is a comma-separated reading-order list. A plain name produces
`<prefix>-<name>.png`; `-` skips a cell; and
`combined=logo-<project>` overrides the combined emblem's basename. Every kept
cell produces both an opaque and a `-transparent` file.

The exact processing options and defaults are maintained in the
[isolation tool README](../../tools/isolate_logos/README.md).

## llm-shared example

The checked-in [llm-shared prompt record](../assets/logo-prompts.md) applies
this structure to four themes and one combined emblem.

Related, in Diátaxis order: [why logo families use a shared system](../explanation/why-project-logos-use-a-shared-visual-system.md)
and [how to create the assets](../how-to/create-a-logo-family-for-a-project.md).
