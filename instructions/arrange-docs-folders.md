# Arrange docs folders

This skill reorganizes the current documents under `docs/` to follow the new structure: `docs\vX.Y.Z\<topic>\<type>.vX.Y.Z.<topic>.md`.

## 1. Move the files

1. Find all markdown files in `docs/` and its immediate subdirectories that match the pattern `<type>.vX.Y.Z.<topic>.md` (e.g. `design.v1.0.0.auth.md`, `feature-request.v2.1.0.login.md`).
2. For each file found:
   - Identify its version (`vX.Y.Z`) and its topic (`<topic>`).
   - Create the target directory `docs\vX.Y.Z\<topic>\` if it does not exist.
   - Move the file to this target directory using `git mv <source> <destination>`.
3. Stage all moves with `git add -A docs/`.

## 2. Create the commit

Create a dedicated commit according to the grouped commits rules.
1. Write a single group commit message in the project-root `a.commit` file, following the [`group-commits-msg.template.md`](../templates/group-commits-msg.template.md) template. 
   - Use `docs:` for the commit type. 
   - A suitable title could be: `docs: arrange documents into version and topic subfolders`.
   - Explain the "Why" and "What" according to the template rules.
2. Format `a.commit` by running `bin\wac.bat` from the project root.
3. Validate and apply the commit by running `bin\gcba.bat --root-a-commit` from the project root.
4. Wait for the batch commit tool to finish successfully (exit status 0). Do not run `git commit` manually.
