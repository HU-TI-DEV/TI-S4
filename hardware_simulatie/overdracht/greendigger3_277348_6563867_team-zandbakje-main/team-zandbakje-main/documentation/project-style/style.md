---
Title: Style.md
Sources: [https://google.github.io/styleguide/cppguide.html], 
---

`Author: Replitard`  
`Contributors: Ocarian`

# Style Guide

## 0. Scope
This document defines the project’s writing, naming, and notation standards. This also applies to documentation we make for the client, that is to be handed over to the next team. 

**Table of contents**
1. [Language used](#1-language-used)
2. [Naming conventions for folders](#2-naming-conventions-for-folders)
3. [Naming conventions for filenames](#3-naming-conventions-for-filenames)
4. [Notation Guide](#4-notation-guide)
   1. [C++](#41-c)
   2. [Git](#42-Git)
   3. [Python](#43-Python)
   4. [SDF](#44-sdf)
   5. [Markdown](#45-markdown)
5. [Client communication guide](#5-client-communication-guide-email)
6. [Changelog](#6-change-log)

---

## 1. Language used
### 1.1 Default language
- Default: **English**.
- Exceptions:
  - **Dutch** for: client preference.

### 1.2 Tone and writing rules
- Style: formal or informal-professional.
- Use:
  - Short sentences.
  - Active voice (absolute language use).
  - No slang.
- Avoid:
  - Ambiguous “it/this/that” without a clear referent.
  - Unexplained acronyms (define on first use).

### 1.3 Spelling & formatting
- Spelling: [US / UK] English
- Dates: `DD-MM-YYYY` (example: `03-12-2026`).
- Time: `24h` (example: `14.30`).
- Units: Scientific Notation (SI) (example: `mm`, `V`, `A`, `Hz`), with a space: `10 mm`.

---

## 2. Naming conventions for folders
### 2.1 General rules
- Case style: dashed (`many-sensors`).
- Keep names short and descriptive.

### 2.2 Git structure
- `docs/` — Documentation.
- `code/` — Source code.
- `media/` — Images, diagrams, media.

### 2.3 Examples
- Good: `docs/system-architecture/`, `src/sensors/`, `tools/gazebo-sdf/`.
- Bad: `New Folder/`, `misc2/`, `Stuff/`.

---

## 3. Naming conventions for filenames
### 3.1 General rules
- Case style: snake case (`snake_case`).
- No spaces, no capital letters.
- No magic numbers or naming shortcuts (field =/= fld).
- Use meaningful suffixes (no `final_final_v2`).

### 3.2 File type rules
- Markdown docs: `topic_name.md`.
- Diagrams: `diagram_name.puml` / `diagram_name.svg` / etc.
- C/C++:
  - Headers: `module_name.h`.
  - Source: `module_name.c`.

### 3.3 Versioning (if needed?)
- Prefer Git history over filename versions.
- If versions must exist: `name_vDDMMYYYY.ext`.

---

## 4. Notation guide

## 4.1 C++
### 4.1.1 Formatting
- Indent: 4 spaces. Use autoformat tool.
- Braces: K&R (Or Allman).
- No magic numbers or naming shortcuts (field =/= fld).

### 4.1.2 Naming
- Types/classes: `PascalCase`.
- Functions/methods: `camelCase`.
- Variables: `camelCase`.
- Constants: `CONSTANT_NAME`.
- Files: match module name.

### 4.1.3 Header / source layout
- Header contains: public API, forward decls, minimal includes.
- Source contains: implementation and private helpers.

### 4.1.4 Includes
- Order:
  1) corresponding header.
  2) standard library.
  3) third-party.
  4) project headers.
- Use `<...>` for system/third-party and `"..."` for project includes.

### 4.1.5 Comments
- Prefer “why” over “what”.
- Use `//` for short notes, `/* ... */` sparingly.
- Doc comments: Doxygen, can be generated using any tool.

### 4.1.6 Error handling
- Approach: throw exceptions.

---

## 4.2 Git
### 4.2.1 Commit messages
- Changes relevant to the API or UI:
    - `feat` Commits that add, adjust or remove a new feature to the API or UI
    - `fix` Commits that fix an API or UI bug of a preceded `feat` commit
- `refactor` Commits that rewrite or restructure code without altering API or UI behavior
    - `perf` Commits are special type of `refactor` commits that specifically improve performance
- `style` Commits that address code style (e.g., white-space, formatting, missing semi-colons) and do not affect application behavior
- `test` Commits that add missing tests or correct existing ones
- `docs` Commits that exclusively affect documentation
- `build` Commits that affect build-related components such as build tools, dependencies, project version, ...
- `ops` Commits that affect operational aspects like infrastructure (IaC), deployment scripts, CI/CD pipelines, backups, monitoring, or recovery procedures, ...
- `chore` Commits that represent tasks like initial commit, modifying `.gitignore`, ...

Examples:  
- `style font camera.sdf`
- `build include dependency main`
- `refactor/test update SensorTest function`

### 4.2.2 Creating new tasks
- Have a clear title for parent issue.
- Use sub issues to group tasks that contribute to the same thing.
- Always write a description for the tasks (sub tasks included).

### 4.2.3 Git Branches
The workflow for the branches will be based on [Feature Branches](https://github.com/HU-TI-DEV/TI-S4/blob/main/infrastructuur/testing_en_tooling/Git_branches.md).
**Overview**: Each new feature or bug fix gets its own dedicated branch created from the main development branch.

**How it works**:
- Create a new branch for each feature (e.g., `feature/user-authentication`)
- Develop the feature in isolation
- Submit a pull request for code review
- Merge back to the main branch once approved
- Delete the feature branch after merging

**Advantages**:
- Clear separation of work
- Easy to track which features are in progress
- Enables parallel development
- Facilitates code review and quality assurance

---

## 4.3 Python
### 4.3.1 Naming
- Files: 'snake_case.py`.
- Classes: `PascalCase`.
- Functions/vars: `snake_case`.
- Constants: `CONSTANT_NAME`.
- No shortcuts or magic numbers.

### 4.3.2 Imports
- Order: stdlib, third-party, project.

### 4.3.3 Docstrings, comments, types
- Docstrings for public modules/classes/functions (PEP 257 style).
- Comments explain “why”, not “what”.
- Type hints for public and non-trivial functions.

### 4.3.4 Errors and logging
- Raise exceptions. Use specific types.

---

## 4.4 SDF
<!-- Generated style guide for SDF due to unfamiliarity, edited to comform with the rest. -->
### 4.4.1 Formatting
- Consistent ordering of elements:
  - `<model>` > `<link>` > `<collision>/<visual>` > `<sensor>` > `<plugin>`.

### 4.4.2 Naming
- Model names: Camel case `camelCase`.
- Links/joints: `base_link`.
- Frames: explicit and consistent.

### 4.4.3 Units and frames
- Units: meters, radians, seconds.
- Coordinate frame convention: East-North-Up (ENU).
- Document assumptions near the model root.

---

## 4.5 Markdown
### 4.5.1 Formatting
- One H1 per file.
- Headings increase by 1 level at a time.
- Blank line before lists and code blocks.
- Be sure to use `</br>` to cut off senteces to avoid walls of text.

### 4.5.2 Code blocks
- Always specify language:
  - [```cpp, ```c, ```html, ```xml, ```bash].
- Keep code blocks minimal and runnable where possible.
- When referencing a line of code:
  - `File / Function / Line`.

### 4.5.3 Links and references
- Internal links: relative paths.
- External links: include source name and date if relevant (Though the less links the better).
- Citations style: simple footnotes

---

## 5. Client communication guide (Email)
- Use school e-mailadres
- Address the recipient correctly (informal/formal)
- Make sure to name all teammembers
- CC teammembers and BCC teamcoach
- Paste the correspondance into the discord "greendigger" channel

---

## 6. Change log
- `03-03-2026` - `Style.md version 1.0`
- `18-03-2026` - `added Git workflow.`
- `24-03-2026` - `changed git structure requirement.`