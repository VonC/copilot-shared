# Why project logos use a shared visual system

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

## Invocation model

Creating a logo family is an optional documentation and branding task, not a
hidden step in the llm-shared development or release workflows. A maintainer
can design the family directly, or ask an AI to derive prompt candidates from
the project's README and confirmed brand choices.

🤖 A project with several documented themes needs more than a collection of
individually attractive pictures. Readers should recognize that the theme
logos belong together, understand what each one represents, and still
recognize the project-wide emblem at a small size.

## One identity, several semantic roles

A useful logo family separates two kinds of decisions:

- the **visual system** stays constant across the whole project;
- the **visual metaphor** changes for each project theme.

The visual system includes the palette, line weight, geometry, level of
detail, background, margins, and rendering style. The metaphor is the concrete
object or action that distinguishes one theme from another. In llm-shared, for
example, documents, a review loop, a groundhog test gate, and a Git trail use
different metaphors while sharing the same colors and drawing language.

This separation is why each generated prompt has two parts: one theme-specific
concept block and one shared style block. Repeating the shared block is
deliberate. Image generators do not otherwise guarantee that separate calls
will preserve the same visual grammar.

## Stable themes make better symbols

The strongest themes describe durable responsibilities of the project, not
temporary implementation details. A useful theme is:

- important enough to appear repeatedly in the documentation;
- distinct from the other themes;
- expressible as one concrete object, action, or relationship;
- likely to survive routine refactoring and release changes.

Broad ideas such as "technology", "quality", or "the cloud" usually produce
generic gears, shields, robots, and clouds. A project-specific action produces
a more memorable symbol: a document becoming a checklist, a branch merging
into a chart, or an animal repeating a test walk.

Three to five themes are normally enough. Fewer may not justify a family;
more make the symbols hard to distinguish and make the combined emblem too
busy.

## The combined emblem is a compression

The project-wide logo should summarize the family, not reproduce every detail.
It can place simplified theme marks inside one enclosing shape, connect them
with one continuous path, or reuse one motif that all themes share.

A literal collage fails at small sizes because each miniature competes for
attention. The combined emblem instead preserves one dominant silhouette and
uses the theme marks as secondary evidence. It must still work when a reader
does not know the individual logos yet.

## Small-size constraints improve the source image

The target is a logo, even when the generator returns a raster image. Designing
for 64 by 64 pixels forces choices that remain useful in navigation, browser
tabs, wiki headings, presentations, and release material:

- one dominant silhouette;
- bold outlines and simple geometry;
- limited colors and minimal shading;
- generous space around the artwork;
- no text, letters, or numbers that can be malformed or disappear.

The source can be generated at a larger resolution, but it should not depend on
details that vanish when reduced.

## Why generation and transparency are separate

A uniform white or near-white background gives the generator a predictable
canvas and gives the isolation tool a measurable boundary. Asking the model for
transparent output directly is less reliable: it may return a checkerboard
pattern, an opaque alpha channel, or erase white details inside the artwork.

The llm-shared isolation workflow flood-fills only background connected to the
cell borders. White paper, check marks, eyes, and highlights enclosed by the
artwork therefore survive. It also creates an opaque white version and a
transparent version from the same crop, so both assets stay aligned.

## The prompt file is part of the design record

Keeping `wiki/assets/logo-prompts.md` beside the generated files records the
semantic and visual decisions that produced them. A future maintainer can
regenerate one theme, add a theme without changing the family style, or explain
why a symbol looks the way it does.

The image is an output; the prompt file is the reproducible design source.

Related, in Diátaxis order: [create a logo family](../how-to/create-a-logo-family-for-a-project.md)
and the [prompt and asset reference](../reference/project-logo-prompt-template.md).
