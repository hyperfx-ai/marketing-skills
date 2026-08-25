#!/usr/bin/env bash
# Validates every skill in skills/ against the repo's authoring rules.
# - Frontmatter has `name` and `description`.
# - `name` matches the folder name.
# - SKILL.md is <= 500 lines.
# - Description includes a "Use when" trigger phrase and is 50-500 chars.
# - Body contains a Requirements section pointing at app.hyperfx.ai/mcp.
# - No banned internal references slipped through, in SKILL.md or any reference
#   file (hyper_cache_, the removed hyper_data_* tools, seti., etc.).

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
    # hyper_cache_ and the removed hyper_data_* tool family are banned because
    # the cache tables and those tools no longer exist. The `database` toolkit
    # (database_query / database_tables_list / database_tables_describe) is the
    # single database path.
    banned_patterns=(
        'hyper_cache_'
        'hyper_data_sql'
        'hyper_data_sync'
        '/Users/'
        '~/.cursor/'
        'agent_v6.jinja'
        'seti\.'
        'src/seti/'
    )
    # Scan SKILL.md and every reference file — a hyper_cache_ table name shipped
    # in references/ once because only SKILL.md was checked.
    while IFS= read -r skill_file; do
        for pattern in "${banned_patterns[@]}"; do
            if grep -qE "${pattern}" "${skill_file}"; then
                rel_path="${skill_file#"${skill_dir}"}"
                echo "FAIL ${skill_name}: ${rel_path} contains banned reference '${pattern}'" >&2
                errors=$((errors + 1))
            fi
        done
    done < <(find "${skill_dir}" -type f -name '*.md')
done

echo ""
if (( errors == 0 )); then
    echo "OK validated ${checked} skill(s) with no errors"
    exit 0
else
    echo "FAIL ${errors} validation error(s) across ${checked} skill(s)" >&2
    exit 1
fi
