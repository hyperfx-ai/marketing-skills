#!/usr/bin/env bash
# Validates every skill in skills/ against the repo's authoring rules.
# - Frontmatter has `name` and `description`.
# - `name` matches the folder name.
# - SKILL.md is <= 500 lines.
# - Description includes a "Use when" trigger phrase and is 50-500 chars.
# - Frontmatter declares metadata.version (semantic version).
# - Body contains a Requirements section pointing at app.hyperfx.ai/mcp.
# - No banned internal references slipped through (hyper_cache_, seti., etc.).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${SCRIPT_DIR}/skills"

if [[ ! -d "${SKILLS_DIR}" ]]; then
    echo "ERROR: ${SKILLS_DIR} does not exist" >&2
    exit 1
fi

errors=0
checked=0

for skill_dir in "${SKILLS_DIR}"/*/; do
    skill_name="$(basename "${skill_dir}")"
    skill_md="${skill_dir}SKILL.md"
    checked=$((checked + 1))

    if [[ ! -f "${skill_md}" ]]; then
        echo "FAIL ${skill_name}: SKILL.md is missing" >&2
        errors=$((errors + 1))
        continue
    fi

    # Extract YAML frontmatter (everything between the first two `---` lines).
    if ! head -n 1 "${skill_md}" | grep -q '^---$'; then
        echo "FAIL ${skill_name}: SKILL.md must start with YAML frontmatter (---)" >&2
        errors=$((errors + 1))
        continue
    fi

    frontmatter_end=$(awk 'NR>1 && /^---$/ {print NR; exit}' "${skill_md}")
    if [[ -z "${frontmatter_end}" ]]; then
        echo "FAIL ${skill_name}: SKILL.md frontmatter is not closed" >&2
        errors=$((errors + 1))
        continue
    fi
    frontmatter="$(sed -n "2,$((frontmatter_end - 1))p" "${skill_md}")"

    # Required: name field matches folder.
    fm_name="$(printf '%s\n' "${frontmatter}" | awk -F': ' '/^name:/ {print $2; exit}')"
    if [[ -z "${fm_name}" ]]; then
        echo "FAIL ${skill_name}: missing frontmatter \`name:\`" >&2
        errors=$((errors + 1))
    elif [[ "${fm_name}" != "${skill_name}" ]]; then
        echo "FAIL ${skill_name}: frontmatter name '${fm_name}' does not match folder '${skill_name}'" >&2
        errors=$((errors + 1))
    fi

    # Required: description field, 50-500 chars, with a trigger phrase.
    fm_description="$(printf '%s\n' "${frontmatter}" | awk -F': ' '/^description:/ {sub(/^description: */, "", $0); print; exit}')"
    if [[ -z "${fm_description}" ]]; then
        echo "FAIL ${skill_name}: missing frontmatter \`description:\`" >&2
        errors=$((errors + 1))
    else
        desc_len=${#fm_description}
        if (( desc_len < 50 )); then
            echo "FAIL ${skill_name}: description is ${desc_len} chars (min 50)" >&2
            errors=$((errors + 1))
        elif (( desc_len > 500 )); then
            echo "FAIL ${skill_name}: description is ${desc_len} chars (max 500)" >&2
            errors=$((errors + 1))
        fi
        if ! printf '%s\n' "${fm_description}" | grep -qiE 'use when|when the user'; then
            echo "FAIL ${skill_name}: description must include a trigger phrase ('Use when' or 'when the user')" >&2
            errors=$((errors + 1))
        fi
    fi

    # Required: metadata.version (semantic version) for clean per-skill versioning.
    # Per the Agent Skills open standard, Hyper-specific fields live under the
    # `metadata:` map; version is `metadata.version`.
    if ! printf '%s\n' "${frontmatter}" | grep -qE '^[[:space:]]+version:[[:space:]]*"?[0-9]+\.[0-9]+\.[0-9]+'; then
        echo "FAIL ${skill_name}: missing metadata.version (semantic version, e.g. 1.0.0)" >&2
        errors=$((errors + 1))
    fi

    # Length cap: 500 lines.
    line_count=$(wc -l < "${skill_md}" | tr -d ' ')
    if (( line_count > 500 )); then
        echo "FAIL ${skill_name}: SKILL.md is ${line_count} lines (max 500). Move long-form material into references/." >&2
        errors=$((errors + 1))
    fi

    # Hyper-specific: must declare Hyper MCP requirement.
    if ! grep -q '## Requirements' "${skill_md}"; then
        echo "FAIL ${skill_name}: missing '## Requirements' section" >&2
        errors=$((errors + 1))
    fi
    if ! grep -q 'app.hyperfx.ai/mcp' "${skill_md}"; then
        echo "FAIL ${skill_name}: must reference app.hyperfx.ai/mcp in the Requirements section" >&2
        errors=$((errors + 1))
    fi

    # Banned strings (internal-only references that should never ship).
    banned_patterns=(
        'hyper_cache_'
        '/Users/'
        '~/.cursor/'
        'agent_v6.jinja'
        'seti\.'
        'src/seti/'
    )
    for pattern in "${banned_patterns[@]}"; do
        if grep -qE "${pattern}" "${skill_md}"; then
            echo "FAIL ${skill_name}: contains banned reference '${pattern}'" >&2
            errors=$((errors + 1))
        fi
    done
done

echo ""
if (( errors == 0 )); then
    echo "OK validated ${checked} skill(s) with no errors"
    exit 0
else
    echo "FAIL ${errors} validation error(s) across ${checked} skill(s)" >&2
    exit 1
fi
