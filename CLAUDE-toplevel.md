# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the SWF (Streaming Workflow) testbed ecosystem.

## SWF Testbed Ecosystem Overview

This directory contains the coordinated multi-repository system for the **ePIC streaming workflow testbed** - a distributed scientific computing system for high-energy physics data processing.

### Repository Structure
```
github/
├── swf-testbed/          # Infrastructure, CLI, and orchestration (REQUIRED)
├── swf-monitor/          # Django web application for monitoring (REQUIRED)
├── swf-common-lib/       # Shared utilities library (REQUIRED)
├── swf-data-agent/       # Data management agent (optional)
├── swf-processing-agent/ # Processing workflow agent (optional)
└── swf-fastmon-agent/    # Fast monitoring agent (optional)
```

**Critical**: The three core repositories (swf-testbed, swf-monitor, swf-common-lib) must exist as siblings in the same parent directory. Additional agent repositories are optional and will be added as the testbed expands.

## Multi-Repository Development Workflow

### Infrastructure Branching Strategy
- **Always use infrastructure branches**: `infra/baseline-v1`, `infra/baseline-v2`, etc.
- **Create coordinated branches** with the same name across all affected repositories
- **Document changes** through descriptive commit messages, not branch names
- **Never push directly to main** - always use branches and pull requests

### Current Infrastructure Versions
**CURRENT STATUS**: All core repositories are on coordinated `infra/baseline-v3` branches with:
- Virtual environment documentation updates (CRITICAL warnings added)
- Top-level CLAUDE.md moved to swf-testbed/CLAUDE-toplevel.md with symlink
- Directory verification guidance added

Check for existing infrastructure branches across core repositories:
```bash
# Check core repos for current infrastructure baseline
for repo in swf-testbed swf-monitor swf-common-lib; do
  echo "=== $repo ===" 
  cd $repo && git branch -a | grep infra && cd ..
done
```

### Coordination Commands
```bash
# Create coordinated infrastructure branch across core repos
for repo in swf-testbed swf-monitor swf-common-lib; do
  cd $repo && git checkout -b infra/baseline-vN && cd ..
done

# Run comprehensive tests across all repositories
cd swf-testbed && ./run_all_tests.sh
```

## Quick Start Commands

### System Initialization
```bash
cd $SWF_PARENT_DIR/swf-testbed
source .venv/bin/activate
pip install -e $SWF_PARENT_DIR/swf-common-lib $SWF_PARENT_DIR/swf-monitor .
# CRITICAL: Set up Django environment
cp $SWF_PARENT_DIR/swf-monitor/.env.example $SWF_PARENT_DIR/swf-monitor/.env
# Edit .env to set DB_PASSWORD='your_db_password' and SECRET_KEY
cd $SWF_PARENT_DIR/swf-monitor/src && python manage.py migrate
cd $SWF_PARENT_DIR/swf-testbed && swf-testbed init
```

### Infrastructure Services
```bash
# Start with Docker (recommended)
cd $SWF_PARENT_DIR/swf-testbed && swf-testbed start

# Or start locally (requires PostgreSQL/ActiveMQ installed)
cd $SWF_PARENT_DIR/swf-testbed && swf-testbed start-local
```

### Testing
```bash
# Test entire ecosystem
cd $SWF_PARENT_DIR/swf-testbed && ./run_all_tests.sh

# Test individual components
cd $SWF_PARENT_DIR/swf-monitor && ./run_tests.sh
cd $SWF_PARENT_DIR/swf-common-lib && ./run_tests.sh
```

## Repository-Specific Guidance

Each repository contains its own CLAUDE.md with detailed, repository-specific guidance:

- **swf-testbed/CLAUDE.md**: CLI commands, process management, Docker orchestration
- **swf-monitor/CLAUDE.md**: Django development, database migrations, ActiveMQ integration  
- **swf-common-lib/CLAUDE.md**: Shared utilities, logging infrastructure, packaging

**IMPORTANT**: When working with this ecosystem, Claude Code should automatically read all repository-specific CLAUDE.md files from the three core repositories (swf-testbed, swf-monitor, swf-common-lib) to understand the complete system context and available commands.

**CRITICAL**: Always verify current working directory with `pwd` before any operations, especially git commands. Never assume location - always check explicitly to prevent errors in multi-repository workflows.

## System Architecture

### Distributed Agent System
- **Loosely coupled agents** communicating via ActiveMQ messaging
- **Process management** via supervisord for cross-platform compatibility
- **Web monitoring** via Django application with REST API
- **Shared utilities** via common library for logging and utilities

### Infrastructure Services
- **PostgreSQL**: Database for monitoring data and metadata
- **ActiveMQ**: Message broker for agent communication
- **Docker Compose**: Development infrastructure services
- **supervisord**: Cross-platform process management

### External Dependencies
- **PanDA**: Distributed workload management system
- **Rucio**: Distributed data management system
- Scientific computing focus for ePIC experiment data processing

## Development Best Practices

### Cross-Repository Changes
1. **Plan infrastructure phase**: Identify all repositories that need changes
2. **Create coordinated branches**: Same `infra/baseline-vN` across affected repos
3. **Work systematically**: Make changes across repositories as needed
4. **Test integration**: Run `./run_all_tests.sh` before merging
5. **Coordinate merges**: Merge pull requests simultaneously across repositories

### Environment Requirements
- **Python 3.9+** across all repositories
- **Docker Desktop** for development infrastructure
- **Git** with coordinated branch management
- **PostgreSQL + ActiveMQ** (via Docker or local installation)

### Testing Strategy
- **Repository isolation**: Each repo has independent test suite
- **Integration testing**: Cross-repository test execution via `run_all_tests.sh`
- **Mock external dependencies**: PostgreSQL, ActiveMQ, HTTP APIs
- **Platform compatibility**: Tests run on macOS, Linux, Windows

## Security and Configuration

### Secrets Management
- **Environment variables** via `.env` files (never committed)
- **Database credentials** isolated per environment
- **API keys and tokens** via secure environment configuration
- **Production deployment** requires additional security hardening

### Configuration Files
- `.env.example` files provide templates for environment setup
- `docker-compose.yml` for development infrastructure
- `supervisord.conf` for process management configuration
- `pyproject.toml` for Python packaging and dependencies

## Troubleshooting

### Common Issues
- **Core repository structure**: Ensure swf-testbed, swf-monitor, and swf-common-lib are siblings
- **Environment variables**: Check SWF_HOME is set correctly (auto-configured by CLI)
- **Database connections**: Verify PostgreSQL is running and accessible
- **ActiveMQ connectivity**: Check message broker is running on expected ports

### Diagnostic Commands
```bash
# Check system status
cd swf-testbed && swf-testbed status  # or status-local

# Verify core repository structure
ls -la swf-testbed swf-monitor swf-common-lib

# Check branch coordination across core repos
for repo in swf-testbed swf-monitor swf-common-lib; do echo "=== $repo ===" && cd $repo && git branch && cd ..; done
```

This ecosystem requires coordinated development across the three core repositories with careful attention to infrastructure branching and testing integration.