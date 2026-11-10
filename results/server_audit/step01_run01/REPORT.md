# Server audit — Paper 6

**Status: REVIEW REQUIRED; not training approval**

| Split | Source | Target | Aligned pairs | Duplicate pair rows |
|---|---:|---:|---:|---:|
| train | 1072192 | 1072192 | 1072192 | 281 |
| valid | 134024 | 134024 | 134024 | 6 |
| test | 134025 | 134025 | 134025 | 5 |

## Cross-split overlap (unique whitespace-normalized values)

```json
{
  "train__valid": {
    "source": 60,
    "target": 2627,
    "pair": 49,
    "group_id": 0
  },
  "train__test": {
    "source": 61,
    "target": 2623,
    "pair": 55,
    "group_id": 0
  },
  "valid__test": {
    "source": 14,
    "target": 358,
    "pair": 13,
    "group_id": 0
  }
}
```

Next: send this file plus audit.json, environment.json and inventory.json.
Do not launch training yet. Full sentence contents are not exported by this audit.
Paths/config excerpts are included; inspect them before sharing outside the research team.
