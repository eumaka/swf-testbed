# Architecture and Design Choices

This document records the reasoning behind key architectural and design decisions
for the `swf-testbed` project. Its goal is to provide context for new
contributors and for future architectural reviews.

## Shared Code Strategy: Dedicated Package (`swf-common-lib`)

- **The Choice:** All code intended for use by more than one component will
  reside in a dedicated, versioned, and installable Python package named
  `swf-common-lib`.

- **Rationale:** This approach was chosen to prevent code duplication and
  divergence across the various `swf-` repositories. It establishes a single
  source of truth for common utilities, ensuring that bug fixes and improvements
  are propagated consistently to all dependent components. It also enables clear
  versioning and dependency management, allowing components to depend on specific
  versions of the shared library.

## Process Management: `supervisord`

- **The Choice:** The testbed's agent processes will be managed by `supervisord`.

- **Rationale:** `supervisord` was chosen for its simplicity, reliability, and
  cross-platform compatibility (it works on both Linux and macOS). As a
  Python-based tool, it fits well within the project's ecosystem and can be
  bundled as a dependency of the main `swf-testbed` package. It provides all
  necessary features—such as auto-restarting, log management, and a control
  interface (`supervisorctl`)—with a straightforward configuration file.

- **Alternatives Considered:**
  - **`systemd`:** A powerful alternative on Linux, but it is not cross-platform
      and would prevent the testbed from running easily on macOS.
  - **Docker Compose:** Excellent for managing multi-container services. While
      this is a powerful pattern, the primary distribution goal is to package the
      Python code itself, not necessarily to mandate a container-based runtime
      (see `docs/packaging_and_distribution.md`).
  - **Manual Scripts:** Running agents in separate terminals is feasible for
      development but is not a robust or scalable solution for a deployed
      testbed.
