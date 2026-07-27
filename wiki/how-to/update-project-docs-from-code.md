# How to keep project docs in sync with the code

<img src="../assets/logo-llm-shared-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

🤖 Goal: bring `README.md`, `ARCHITECTURE.md`, `docs/architecture/`, and any
existing `wiki/` or `docs/wiki/` Diataxis set back in line with the
implementation or a selected Git range.

## Invocation model

This is normally an AI-owned review: ask for the project-docs skill and the AI
inspects the relevant code before editing the documentation and validating the
result. Use the procedure directly when doing a manual documentation audit or
when reviewing the AI's evidence file by file.

## 📋 Steps of the documentation review

1. Run the skill, optionally scoping it:

   ```txt
   /review-and-update-project-docs
   ```

   Name specific Markdown targets or wiki roots to restrict the update. Name
   specific code or a Git range such as `v1.2.3..HEAD` to restrict the review.
   With no scope, all existing target docs are checked after a global code
   review.

2. The skill reviews the code first, then cross-references each target
   document, flagging what is outdated, missing, inaccurate, or still
   correct.

3. It updates only the stale sections, with one rule per document kind:

   - `README.md` — usage: what a user runs and sees,
   - `ARCHITECTURE.md` — boundaries and layer responsibilities,
   - `docs/architecture/*.md` — one concern per file; a new concern gets a
     new file,
   - `wiki/` or `docs/wiki/` — one Diataxis purpose per page, with categories
     presented as explanation, tutorials, how-to guides, then reference.

4. For a Git range, it maps every release topic to wiki coverage and checks the
   final tree so reverted or replaced behavior is not documented.

5. It validates changed links, page purpose, category order, and any focused
   documentation tests supplied by the project.

6. It reports what was updated, what was left unchanged, what was created,
   and any open questions it could not settle from the reviewed scope.

## ✅ Check the update

The diff touches only sections that were stale, and every statement added
can be traced to code the review saw — the skill does not write wishes,
it writes what is there.

Related: [Why documents come before code](../explanation/why-documents-before-code.md)
and the [skills catalog](../reference/skills-catalog.md).
