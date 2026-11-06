# GTM Audit

A standard auditing pass against an existing Google Tag Manager container. Run this when:

- Conversion data looks wrong in GA4.
- A recent GTM publish broke something and nobody is sure what.
- A new team has inherited a container someone else built.
- The container has > 30 tags and nobody can remember what they all do.

The Hyper MCP exposes the GTM API as `gtm_*` tools (note: the prefix is `gtm_*`, not `google_tag_manager_*`). Each tool is one entity with `operation` parameters (`get`, `list`, `create`, `update`, `delete`, etc.).

## Audit checklist

The 8 checks below cover ~95% of GTM problems.

### 1. Inventory: how many tags, triggers, variables?

```
google_tag_manager_tags_manage(operation="list", workspace_path="accounts/123/containers/456/workspaces/789")
google_tag_manager_triggers_manage(operation="list", workspace_path="...")
google_tag_manager_variables_manage(operation="list", workspace_path="...")
```

Healthy ranges (rough — bigger sites legitimately have more):

| Entity | < 30 tags | 30–80 | > 80 |
| --- | --- | --- | --- |
| Tags | Easy to understand | Audit needed every quarter | Likely has duplicates / stale tags |
| Triggers | Probably fine | Look for unused | Most are unused — most teams over-create triggers |
| Variables | Fine | Some likely unused | Definitely has unused ones |

If totals are at the high end of any row, schedule a cleanup pass.

### 2. Find duplicate tags

The most common GTM problem: two tags fire on the same trigger because someone created a "v2" without disabling the original. Result: events fire twice → conversion counts double.

Pull all tags, group by `type` + the trigger they fire on. Anything firing the same event to the same destination on the same trigger is suspect.

```
# Get all tags
result = google_tag_manager_tags_manage(operation="list", workspace_path="...")

# Look for duplicates: same type, same firing trigger, similar parameters
# (No SQL here — just inspect the response)
```

Confirm against GA4 DebugView: trigger the page, see if the event fires once or twice.

### 3. Find tags with no firing triggers

A tag with `firingTriggerId: []` is dead — it can never fire. Either delete it or attach the missing trigger.

Common cause: someone deleted the trigger but not the tag. The tag sits there confusing future readers.

### 4. Find triggers with no tags

A trigger nothing depends on is just clutter. Delete.

```
# After listing tags + triggers, build a set of trigger IDs in use:
used = set()
for tag in tags:
    used.update(tag.firing_trigger_id or [])
    used.update(tag.blocking_trigger_id or [])

unused_triggers = [t for t in triggers if t.trigger_id not in used]
```

### 5. Find variables that aren't referenced

GTM variables are referenced from tags and triggers. If a variable name appears nowhere in any tag's parameters or trigger's filters, delete it.

```
# Search the JSON of every tag + trigger for {{Variable Name}} references
```

### 6. Check for missing consent gates (GDPR / CCPA)

If the site collects EU traffic, every analytics + advertising tag should be gated on a consent variable. The pattern:

- A consent variable (`Cookiebot Consent State`, `OneTrust Active Groups`, custom JS variable) returns the user's consent status.
- Each marketing / analytics tag has a *blocking trigger* on `Consent != Granted`.

Without this, GDPR fines are real.

```
# For every analytics / advertising tag, verify it has a blocking trigger
# on the consent variable. Tags missing the gate are flagged.
```

GA4 has built-in consent mode that can do this differently — check whether the container is using consent mode v2 or manual gates. Either is fine, missing both is not.

### 7. Check for hard-coded measurement IDs / property IDs

Bad: GA4 measurement ID `G-XXXXXXX` typed directly into 14 different tags.
Good: GA4 measurement ID stored in a single Constant variable, referenced from all tags.

Cleanup: create a `Constant` variable, replace every hard-coded reference. Critical when migrating between properties.

### 8. Check version history for recent changes

If something broke "around last Tuesday," the publish history is the prime suspect.

```
google_tag_manager_versions_manage(operation="list", container_path="accounts/123/containers/456")
google_tag_manager_version_headers_manage(operation="list", container_path="accounts/123/containers/456")
```

Each version has a `publishedTimestamp` and a name. Find the version that was live during the breakage window. Diff against the previous version (the GTM UI does this best — the API can fetch both versions and you compare the JSON).

```
google_tag_manager_versions_manage(operation="get", version_path="accounts/.../versions/12")
google_tag_manager_versions_manage(operation="get", version_path="accounts/.../versions/11")
```

If a tag / trigger / variable changed between v11 and v12 and v12 was the publish that broke things, you have your culprit.

## The publish workflow (don't break this part)

GTM has a 4-stage workflow that exists for a reason — bypass it and you'll publish broken tags to production.

```
1. Workspace      ← edit here (sandboxed, doesn't affect live container)
   google_tag_manager_workspaces_manage(operation="create", name="audit-2026-q2", ...)

2. Preview         ← test in GTM Preview mode with the page open
   (UI-only — no API operation, but the agent can tell the user to do this)

3. Version         ← snapshot the workspace into a versioned set of changes
   google_tag_manager_versions_manage(operation="create", workspace_path="...", name="audit-cleanup", notes="removed 12 unused tags")

4. Publish         ← make the version live
   (UI or version operation with publish=true)
```

**Never edit directly in the default workspace** if more than one person uses the container. Create a named workspace, do the work, version + publish, delete the workspace.

## Common audit findings (what they usually mean)

| Finding | Likely cause | Fix |
| --- | --- | --- |
| 4× the expected `purchase` events in GA4 | Two tags fire on the same trigger | Disable / delete the duplicate |
| Conversion event missing entirely | Tag exists but blocking trigger fires (consent, page exclusion) | Check blocking triggers, verify consent state |
| Events firing on the wrong domain | Trigger lacks a `Page Hostname` filter | Add hostname filter to trigger |
| Form submission tracked, but no form data captured | Form variables not registered as DataLayer Variables | Create DataLayer Variables for each field |
| Tag fires on every page instead of just confirmation | Trigger is `All Pages` instead of a URL-specific trigger | Tighten the trigger condition |
| Old tag firing a Universal Analytics event | Container never migrated when GA4 launched | Delete UA tags (UA was sunset July 2024) |
| New page type missing all tracking | Page template doesn't have the GTM container snippet | Verify the GTM script tag is on every page template |

## Reporting the audit

Present findings as a table the team can act on:

```
| # | Finding                                  | Severity | Action                       | Tag / Trigger ID |
|---|------------------------------------------|----------|------------------------------|------------------|
| 1 | Duplicate `purchase` event tag           | High     | Delete tag #47               | tag_47           |
| 2 | 14 unused triggers                       | Low      | Delete                       | (list)           |
| 3 | GA4 measurement ID hardcoded in 8 tags   | Medium   | Move to Constant variable    | (list)           |
| 4 | EU traffic, no consent gate on Meta tag  | High     | Add consent blocking trigger | tag_22           |
```

Severity rubric:
- **High** = data is currently wrong / privacy non-compliant. Fix this week.
- **Medium** = will become a problem (migration risk, maintenance burden). Fix this month.
- **Low** = cleanup, no functional impact. Fix when convenient.

After the audit, the team should know exactly what to delete, what to fix, and in what order.
