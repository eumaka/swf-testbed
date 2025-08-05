# 🤖 AI ASSISTANT GUIDANCE - READ THIS FIRST

**⚠️ MANDATORY FOR ALL AI ASSISTANTS WORKING ON SWF-TESTBED ⚠️**

## 🚨 CRITICAL THINKING REQUIREMENTS

Before implementing ANY solution, Claude must explain:

1. **Complete Data Flow Analysis**
   - Where does data come from?
   - Where does it get stored?
   - Where does it get used?
   - What persists between runs?
   - What gets cached or reused?

2. **Problem Definition**
   - What is the actual problem vs what I think it is?
   - What assumptions am I making?
   - What evidence do I have that my understanding is correct?

3. **Solution Validation**
   - Why will this solution work?
   - What could go wrong?
   - How can I verify it worked?
   - What side effects might occur?

## DO NOT CODE UNTIL:
- You can trace the complete data flow
- You can explain why the current behavior is happening
- You can explain exactly what needs to change
- You have stated all assumptions explicitly

## Common Failure Patterns to Avoid:
- Jumping to implementation without understanding the system
- Assuming data behaves as expected without verification
- Ignoring data persistence between script runs
- Making changes without understanding their scope
- Failing to clear cached/persistent data

## When Stuck:
1. Stop coding
2. Explain what you think is happening
3. Ask for verification of your understanding
4. Only proceed when understanding is confirmed

## 🚨 FILE OPERATIONS RULE
**MAJOR ERROR WARNING: Deleting files, directories, database tables, databases or other entities without explicit user request or authorization is strictly forbidden and constitutes a major error. NEVER use rm, delete, DROP TABLE, or any deletion operations unless explicitly instructed by the user.**

## 🚨 ENVIRONMENT SETUP RULE
**DO NOT RUN PYTHON COMMANDS WITHOUT VENV:** Every Python command must be preceded by:
```bash
cd /eic/u/wenauseic/github/swf-testbed && source .venv/bin/activate && source ~/.env
```
**This includes:** python, pip, pytest, any example_agents scripts, or swf-testbed commands

## 🏗️ MULTI-REPOSITORY DEVELOPMENT

### Development Environment
- **Launch Claude Code from the parent directory** containing all swf-* repositories
- This enables access to all core repositories for coordinated development
- Do not launch from within individual repository directories

### Branch Management
- **Always use infrastructure branches**: `infra/baseline-v1`, `infra/baseline-v2`, etc.
- **CRITICAL: Always push with `-u` flag on first push**: `git push -u origin branch-name`
- Never push directly to main - always use branches and pull requests

## 📁 ARCHITECTURE OVERVIEW

### Agent-Based Architecture
- Agents are Python processes managed by supervisord
- Communication is asynchronous via ActiveMQ messaging
- Base agent handles all infrastructure concerns automatically

### Infrastructure Components

**Two Deployment Modes:**

**Development Mode** (Docker-managed):
- ActiveMQ and PostgreSQL via Docker containers
- Use `swf-testbed start/stop/status`

**System Mode** (System-managed):
- ActiveMQ and PostgreSQL as system services (e.g., artemis.service, postgresql-16.service)
- Use `swf-testbed start-local/stop-local/status-local`
- Use `python report_system_status.py` for comprehensive readiness check

**Common Components:**
- **Process Management**: supervisord manages Python agents (both modes)
- **Web Interface**: Django application (swf-monitor)
- **CLI**: Typer-based command line interface

## 🔧 DEVELOPMENT PRACTICES

### Standardized Agent Pattern
```python
from base_agent import ExampleAgent  # Auto-handles environment setup
# Pure business logic only - no infrastructure sausage-making
```

### Environment Setup (Auto-Loading Pattern)
ALL example agent scripts should include environment auto-loading:
```python
def setup_environment():
    """Auto-activate venv and load environment variables."""
    # Implementation handles venv activation and ~/.env loading
    # Unsets proxy variables for localhost connections
```

## 📚 DOCUMENTATION STRUCTURE

This `docs/` directory provides modular documentation for AI readability:
- Focus on single concerns
- Cross-reference related topics  
- Easier for AI assistants to find specific information
- Allows incremental updates without affecting unrelated sections

Main [README.md](../README.md) provides complete overview but can be overwhelming for specific tasks.

---

**🎯 SUCCESS PATTERN: Follow critical thinking → understand data flow → implement solution → verify results**

**📖 ALWAYS READ [CLAUDE.md](../CLAUDE.md) for repository-specific instructions before starting work**

---

## Prompt Tips

**Note to the AI Assistant:** The following "Prompt Tips" are a guide for our
collaboration on this project. Please review them carefully and integrate them
into your operational context to ensure your contributions are consistent,
high-quality, and aligned with the project's standards.

### General

- **Adhere to established standards and conventions.** When implementing new
  features, prioritize the use of established standards, conventions, and
  naming schemes provided by the programming language, frameworks, or
  widely-used libraries. Avoid introducing custom terminology or patterns when a
  standard equivalent exists.
- **Portability is paramount.** All code must work across different platforms
  (macOS, Linux, Windows), Python installations (system, homebrew, pyenv, etc.),
  and deployment environments (Docker, local, cloud). Never hardcode absolute
  paths, assume specific installation directories, or rely on system-specific
  process names or command locations. Use relative paths, environment variables,
  and standard tools (like supervisorctl) rather than platform-specific process
  detection. When in doubt, choose the more portable solution.
- **Favor Simplicity and Maintainability.** Strive for clean, simple, and
  maintainable solutions. When faced with multiple implementation options,
  recommend the one that is easiest to understand, modify, and debug. Avoid
  overly complex or clever code that might be difficult for others (or your
  future self) to comprehend. Adhere to the principle of "Keep It Simple,
  Stupid" (KISS).
- **Follow Markdown Linting Rules.** Ensure all markdown content adheres to the
  project's linting rules. This includes, but is not limited to, line length,
  list formatting, and spacing. Consistent formatting improves readability and
  maintainability.
- **Maintain the prompts.** Proactively suggest additions or modifications to
  these tips as the project evolves and new collaboration patterns emerge.

### Project-Specific

- **Context Refresh.** To regain context on the SWF Testbed project, follow
  these steps:
    1. Review the high-level goals and architecture in `swf-testbed/README.md`
       and `swf-testbed/docs/architecture_and_design_choices.md`.
    2. Examine the dependencies and structure by checking the `pyproject.toml`
       and `requirements.txt` files in each sub-project (`swf-testbed`,
       `swf-monitor`, `swf-common-lib`).
    3. Use file and code exploration tools to investigate the existing codebase
       relevant to the current task. For data models, check `models.py`; for
       APIs, check `urls.py` and `views.py`.
    4. Consult the conversation summary to understand recent changes and
       immediate task objectives.

- **Verify and Propose Names.** Before implementing new names for variables,
  functions, classes, context keys, or other identifiers, first check for
  consistency with existing names across the relevant context. Once verified,
  propose them for review. This practice ensures clarity and reduces rework.

- **Preserve Human-Written Documentation.** Before making substantial changes to documentation files, carefully review existing content to identify human-authored sections that provide unique value. When adding new content, structure your changes to complement rather than replace existing documentation. If you must restructure or move content, explicitly call out what you're relocating and why, ensuring no substantive human-written content is lost. When in doubt, propose the change structure before implementation.

- **Schema Migration and Model Consistency Workflow** - When updating Django models or database schema, follow this systematic approach to maintain consistency across the entire application stack: (1) Request user approval to wipe the database for a clean start, since maintaining backward compatibility during development is unnecessary overhead. (2) The Django model is the single source of truth for schema - update models first, then cascade changes downward. (3) Create and apply Django migrations to implement the updated model schema. (4) Update all templates to match actual model field names and structure - templates must conform to the model, never the reverse. (5) Update views to match template parameter expectations and model field names - views serve as the bridge between models and templates. (6) Replace example data with simple, mostly-random content that validates the schema - use domain knowledge for sensible enum values and relationships, but don't over-engineer realistic scenarios. **Key Principle**: Model → Migration → Template → View → Data. Each layer must conform to the layer above it in this hierarchy.

- **Ensuring Robust and Future-Proof Tests** - Write tests that assert on outcomes, structure, and status codes—not on exact output strings or UI text, unless absolutely required for correctness. For CLI and UI tests, check for valid output structure (e.g., presence of HTML tags, table rows, or any output) rather than specific phrases or case. For API and backend logic, assert on status codes, database state, and required keys/fields, not on full response text. This approach ensures your tests are resilient to minor UI or output changes, reducing maintenance and avoiding false failures. Always run tests using the provided scripts (`./run_tests.sh` or `./run_all_tests.sh`) to guarantee the correct environment and configuration.