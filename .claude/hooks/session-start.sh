#!/bin/bash
# Ensures the obsidian-skills plugin is available on every Claude Code session
# (PC, web, mobile) so the vault's tooling stays consistent across devices.
# Both commands are idempotent (no-op with success if already present).
set -uo pipefail

claude plugin marketplace add kepano/obsidian-skills || true
claude plugin install obsidian@obsidian-skills || true

exit 0
