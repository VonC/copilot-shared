# How to create a logo family for a project

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Goal: create a coherent set of project-theme logos, one combined emblem,
and matching opaque and transparent PNG assets that can be reused throughout a
project wiki.

## Invocation model

Logo-family creation is a maintainer-requested documentation task. Ask an AI to
apply the reusable meta-prompt when the project identity inputs are ready, use
an image generator for the approved prompts, then ask an agent with the
`isolate-logos` skill to process the resulting sheet. None of these actions
runs automatically during implementation or release preparation.

## Collect the project identity inputs

Gather the following information before generating images:

- project name and filename-safe slug;
- a short description or the relevant part of the README;
- intended audience;
- three to five durable project themes, when already known;
- desired brand personality;
- existing brand colors, with hexadecimal values;
- visual elements or styles that must be avoided.

If the themes are not known, let the meta-prompt propose them, but approve the
theme list before image generation. Reject themes that are temporary,
overlapping, or only expressible through text.

## Create the project prompt record

Copy the [project logo meta-prompt](../reference/project-logo-prompt-template.md#reusable-meta-prompt)
and replace its input placeholders. Give it the project README as the
description when the README is concise; otherwise provide only the sections
that define the project's purpose and major responsibilities.

Save the result as:

```text
wiki/assets/logo-prompts.md
```

The generated record should contain a palette, one shared style block, one
concept block per theme, a combined-emblem concept, a logo-sheet prompt, and a
filename table. Keep the image-generation prompts in English for consistent
reuse across projects and image tools.

## Review the visual system before generating

Check the proposed record before spending an image-generation call:

- each theme maps to one distinct, concrete metaphor;
- every logo uses the same palette, outlines, geometry, and detail level;
- the combined emblem has one dominant silhouette rather than a collage;
- the prompts prohibit text, letters, numbers, captions, and watermarks;
- the design remains recognizable at 64 by 64 pixels;
- the background is uniformly white or near-white.

Change the prompt record first when a metaphor or palette is wrong. Do not use
post-processing to compensate for a concept that does not represent the
project.

## Generate the logo sheet

Use the complete sheet prompt from `wiki/assets/logo-prompts.md`. Ask for:

- one cell per theme and one cell for the combined emblem;
- a uniform grid with a known number of columns;
- one centered logo per cell;
- generous space between cells;
- no dividers, labels, captions, mockups, shadows, or decorative background;
- a plain white or near-white canvas.

Keep the generated sheet until every extracted asset has been verified. If the
generator cannot keep the visual system consistent across a sheet, generate
the logos separately with the exact same shared style block, then treat each
image as a one-cell sheet.

## Isolate and name the assets

You can ask an agent with the `isolate-logos` skill to split the sheet. Provide
the image path, column count, cell names in reading order, output directory,
and project prefix.

To run the implementation directly, use:

```text
uv run --with pillow python <llm-shared>/tools/isolate_logos/isolate_logos.py sheet.png --out-dir wiki/assets --cols 3 --names intake,review,release,-,docs,combined=logo-acme --prefix logo-acme
```

The names list describes every grid cell in reading order. Use `-` for an
empty or duplicate cell. Use `combined=logo-<project>` for the project-wide
emblem so its basename does not include `-combined`.

For every kept cell, the tool writes:

- `<base>.png`, centered on an opaque white square;
- `<base>-transparent.png`, with only the border-connected background removed.

Use `--cols 1` and one name when processing a separately generated logo as a
one-cell sheet. The complete option contract is in the
[logo isolation tool reference](../../tools/isolate_logos/README.md).

## Inspect every output

Open both variants of every logo and verify:

- the complete logo is present and centered;
- no part of a neighboring cell remains;
- the square margin is consistent across the family;
- internal white details remain visible in the transparent file;
- pale residue and background halos have not widened the crop;
- each logo is still recognizable when displayed at 64 by 64 pixels.

If the grid cut clips a logo, regenerate the sheet with more spacing or pass
explicit `--col-splits` and `--row-splits`. If pale artwork becomes
transparent, adjust `--white-threshold` and regenerate the affected assets.

## Add the assets to the wiki

Use the transparent variant in a normal wiki heading:

```html
<img src="../assets/logo-acme-review-transparent.png" alt="" width="200" align="right">
```

Use a meaningful `alt` value when the image communicates information that the
page text does not already provide. An empty `alt` value is appropriate when
the logo is decorative and the heading names the subject.

Link the new pages from `wiki/README.md`. Preserve the navigation order:
explanation, tutorials, how-to guides, then reference. A logo topic does not
need a page in every category.

## Preserve and validate the design record

Commit the prompt record with the generated assets. Check that:

- every relative Markdown and image link resolves;
- filenames follow the documented convention;
- the wiki uses the intended transparent variants;
- each page stays focused on one Diátaxis purpose;
- the family palette and metaphors in the prompt record match the final images.

Related, in Diátaxis order: [why the logos form a visual system](../explanation/why-project-logos-use-a-shared-visual-system.md)
and the [prompt and asset reference](../reference/project-logo-prompt-template.md).
