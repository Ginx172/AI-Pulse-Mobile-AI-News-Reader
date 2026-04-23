# AI Pulse — Custom Sources Guide

AI Pulse ships with 103 curated AI information sources, but you can add your own
sources in three ways.

---

## Option 1 — Edit `sources/custom_sources.yaml` (Git-based)

This is the recommended approach for sources you want to persist across all
deployments of your instance.

1. Open `sources/custom_sources.yaml` in any text editor.
2. Add an entry under `sources:`:

```yaml
sources:
  - id: my-blog
    name: "My Blog"
    url: "https://example.com"
    rss_url: "https://example.com/feed.xml"   # null if unknown
    category: custom
    type: blog
    language: en
    weight: 1.2
    active: true
    added_at: "2026-04-23T19:00:00Z"
    added_by: "user"
```

3. Commit the file (`git add sources/custom_sources.yaml && git commit`).
4. Restart the backend — `load_all_sources()` will merge your entry with the official catalog.

See `sources/custom_sources.example.yaml` for a fully annotated example.

---

## Option 2 — `POST /sources/custom` (Runtime API)

Add a source at runtime without editing any files — useful from the mobile app.

```bash
curl -X POST http://localhost:8000/sources/custom \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Simon Willison",
    "url": "https://simonwillison.net",
    "weight": 1.2
  }'
```

The API will:
- Auto-generate a slug `id` from the name.
- Try to auto-discover the RSS feed (checks common paths + HTML `<head>`).
- Save the record to the `custom_sources` DB table.
- Return `201 Created` with the full record.

Other endpoints:
- `PATCH /sources/custom/{id}` — update name / url / rss_url / weight / active.
- `DELETE /sources/custom/{id}` — remove (DB records only).

---

## Option 3 — Toggle official sources via `PATCH /sources/{id}`

Disable (or re-enable) any of the 103 official sources without deleting them:

```bash
# Disable a source
curl -X PATCH http://localhost:8000/sources/openai-blog \
  -H "Content-Type: application/json" \
  -d '{"active": false}'

# Re-enable it
curl -X POST http://localhost:8000/sources/openai-blog/enable

# Apply a weight multiplier (boost)
curl -X PATCH http://localhost:8000/sources/huggingface-blog \
  -H "Content-Type: application/json" \
  -d '{"weight_override": 1.5}'
```

Overrides are stored in the `source_overrides` DB table and take effect on the
next pipeline run. The mobile Settings screen (Phase 4) will surface this as a
toggle list.

---

## Merge order

```
official YAML → custom YAML → custom DB → overrides DB
```

When the same `id` appears in multiple layers, the later layer wins. Overrides
(active / weight) from the `source_overrides` table are always applied last.
