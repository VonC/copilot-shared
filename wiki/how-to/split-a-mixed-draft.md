# How to split a mixed draft into requirements

<img src="../assets/logo-llm-shared-documents-transparent.png" alt="" width="200" align="right">

<!-- markdownlint-disable MD013 -->

📝 Goal: turn one draft note that mixes several distinct topics into an
ordered list of feature-requests and issues, each ready for its own
`/write-requirement` run.

## Invocation model

The user supplies the draft and asks the AI to split and define it; the AI
classifies the content, writes the requirement artifacts, and presents the
boundaries for human validation. Follow the steps manually only when you need a
custom split outside the skill chain.

## 🤔 When splitting is worth it

Reach for `/split-and-define` when the draft mixes several items, when the
items differ in dependency order, or when you want the skill to propose a
slug per item. Skip it when the draft is one self-contained requirement:
call `/write-requirement` directly with the type, version and topic.

## 📋 Steps to split the draft

1. Make sure the draft has been processed: `/process-draft` classified it
   as a collection and renamed it `docs\draft.vX.Y.Z.<slug>.md` on its own
   effort branch.

2. Run the split:

   ```txt
   /split-and-define on docs/draft.vX.Y.Z.<slug>.md
   ```

3. The skill appends a `## List of feature-requests and issues to create`
   section to the draft. Each entry carries:

   - the type (`Feature-request:` or `Issue:`),
   - a key title with a 2-3 word `[topic-slug]` in brackets,
   - the rationale for the regrouping.

   Items are ordered from most independent to most dependent, so they can
   be defined and implemented in that order.

4. The skill ends on a multi-choice with one
   `/write-requirement on docs/feature-request.vX.Y.Z.<slugN>.md` (or
   `issue.`) entry per slug. Pick the first item; repeat for each slug.

5. Keep the processed draft under its collection slug. When an item is developed
   on its own branch, name the branch from the item slug; underscores and hyphens
   are equivalent for workflow matching:

   ```txt
   docs\draft.v10.0.0.sentinel.md
   docs\issue.v10.0.0.route-cleanup.md
   branch: route_cleanup
   ```

   Do not rename the umbrella draft to `route-cleanup` or create a temporary
   same-slug draft alias. The menu-less `pw skill` and `pw handoff` commands
   first use ordinary branch memory and changed-draft resolution. If those find
   no topic, their shared resolver can connect the item to the requirement and
   unchanged umbrella:

   - exactly one requirement filename must match the normalized branch leaf,
   - a direct same-version, same-slug draft wins when exactly one exists,
   - otherwise exactly one same-version umbrella draft must mention the complete
     normalized item slug,
   - missing or ambiguous matches leave the topic unresolved.

6. Let each requirement writer run its explicit review handoff:

   ```txt
   pw skill --after-write requirement
   ```

   This reviews the requirement just written. It does not use settled-looking
   content to decide whether review already happened.

## ✅ Check after the split

The draft now ends with the list section, and each
`/write-requirement` run creates one `docs\<type>.vX.Y.Z.<topic>.md` that
enters its own review loop. An item branch can continue through `pw skill` and
the later `pw handoff` implementation chain without a same-slug draft, while
the umbrella collection remains intact.

Related: [From draft note to settled requirement](../tutorials/02-from-draft-to-settled-requirement.md),
[skills catalog](../reference/skills-catalog.md).
