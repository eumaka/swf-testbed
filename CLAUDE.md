# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Environment

### Claude Code Setup
- **Launch Claude Code from the parent directory** containing all swf-* repositories (e.g., `/Users/username/github/`)
- This enables access to all core repositories for coordinated multi-repository development
- Do not launch from within individual repository directories as this restricts cross-repo operations

## Development Commands

### Testing
- `./run_tests.sh` - Run tests for swf-testbed only (uses pytest)
- `./run_all_tests.sh` - Run tests across all swf-* repositories in parent directory
- Tests are located in `tests/` directory and use pytest framework

### Testbed Management
- `swf-testbed init` - Initialize environment (creates logs/ directory and supervisord.conf)
- `swf-testbed start` - Start testbed with Docker services (PostgreSQL, ActiveMQ) + agents
- `swf-testbed stop` - Stop all Docker services and agents
- `swf-testbed status` - Check status of Docker services and agents
- `swf-testbed start-local` - Start agents only (assumes PostgreSQL/ActiveMQ running locally)
- `swf-testbed stop-local` - Stop local agents only
- `swf-testbed status-local` - Check status of local services and agents

### Installation and Dependencies
**CRITICAL: Always activate virtual environment first: `source .venv/bin/activate`**
- `source .venv/bin/activate && pip install -e .` - Install in development mode (from swf-testbed directory)
- Dependencies managed via `pyproject.toml`
- `source .venv/bin/activate && pip install .[test]` - Install test dependencies
- Virtual environment located at `.venv/` - ALWAYS activate before any Python commands

## Architecture Overview

### Multi-Repository Structure
This is part of a coordinated multi-repository system with sibling repositories:
- **swf-testbed**: Core infrastructure, CLI, and orchestration (this repo)
- **swf-monitor**: Django web application for monitoring and data management
- **swf-common-lib**: Shared utilities and common code
- Additional agent repositories: swf-daqsim-agent, swf-data-agent, swf-processing-agent, swf-fastmon-agent

All repositories must be cloned as siblings in the same parent directory for proper operation.

### Agent-Based Architecture
The system implements loosely coupled agents that communicate via ActiveMQ messaging:
- Agents are Python processes managed by supervisord
- Each agent has a specific role in the streaming workflow
- Communication is asynchronous via message broker
- Process management configuration in `supervisord.conf`

### Infrastructure Components
- **Process Management**: supervisord manages all Python agent processes
- **Message Broker**: ActiveMQ provides messaging backbone
- **Database**: PostgreSQL for monitoring data and metadata
- **Web Interface**: Django application (swf-monitor) for system monitoring
- **CLI**: Typer-based command line interface for testbed management

### Environment Setup
- `SWF_HOME` environment variable automatically set to parent directory containing all swf-* repos
- Docker Compose provides PostgreSQL and ActiveMQ services for development
- Local installation supported for users who prefer host-managed services

## Development Practices

### Multi-Repository Development
- **Always use infrastructure branches**: `infra/baseline-v1`, `infra/baseline-v2`, etc. for all development
- Create coordinated branches with same name across all affected repositories
- Document specific features and changes through descriptive commit messages
- Never push directly to main - always use branches and pull requests
- Run `./run_all_tests.sh` before merging infrastructure changes
- Maintain sibling directory structure for all swf-* repositories

### Code Organization
- Shared code goes in `swf-common-lib` package to prevent duplication
- Agent-specific code stays in respective agent repositories
- CLI implementation in `src/swf_testbed_cli/main.py`
- Configuration templates in repository root

### Testing Strategy
- Pytest for unit tests
- Test infrastructure designed for cross-platform compatibility
- Tests assert on outcomes and structure, not exact output strings
- Automated test discovery across all swf-* repositories

## Documentation Maintenance

### README Table of Contents
The README.md contains a manual Table of Contents that must be kept synchronized with the document structure. When making changes to README.md:

1. **Check the TOC** against actual section headings after any structural changes
2. **Update anchor links** if section names change (use GitHub-style `#section-name` format)
3. **Add new sections** to the TOC in the correct order
4. **Remove deleted sections** from the TOC
5. **Reorder TOC items** to match the document structure

This maintenance should be part of any commit that involves adding, removing, or renaming sections in the README.

## Key Configuration Files

- `pyproject.toml`: Package configuration and dependencies
- `supervisord.conf`: Process management configuration template
- `docker-compose.yml`: Development infrastructure services
- `run_tests.sh` / `run_all_tests.sh`: Test execution scripts

## External Dependencies

- **PanDA**: Distributed workload management system for workflow orchestration
- **Rucio**: Distributed data management system
- **ActiveMQ**: Message broker for agent communication
- **PostgreSQL**: Database for monitoring and metadata storage
- **supervisord**: Process management for Python agents