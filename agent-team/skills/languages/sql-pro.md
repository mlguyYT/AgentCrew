# Skill: SQL Pro

## Purpose

Use this skill for professional SQL query, schema, migration, and data-access work.

## Applies when

Use this skill when work involves:

- SQL queries
- schema changes
- migrations
- indexes
- joins and aggregations
- database constraints
- data access performance

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - SQL
    - query
    - migration
    - index
    - database
  files:
    - "*.sql"
    - "migrations/**"
    - "db/**"
    - "schema.sql"
  code_symbols:
    - SELECT
    - INSERT
    - UPDATE
    - DELETE
    - JOIN
    - CREATE INDEX
```

## Developer instructions

- Prefer parameterized queries.
- Preserve existing migration conventions.
- Make schema changes reversible when the project supports rollback.
- Consider indexes for new lookup paths.
- Avoid destructive data changes without explicit human approval.
- Keep query behavior deterministic when ordering matters.
- Do not embed secrets or production data.

## Testing guidance

Look for:

```bash
pytest
npm test
make test
dbmate status
alembic upgrade head
rails db:migrate
```

Use project-specific migration and integration test commands first.

## Review checklist

- queries are parameterized
- migrations follow project conventions
- rollback or recovery is considered
- constraints match application behavior
- indexes support new access patterns
- destructive operations require human approval

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - string-concatenated SQL with user input
  - unbounded destructive updates
  - migrations mixed with unrelated refactors
  - missing order by when result order matters
  - adding indexes without a query reason
```

## Output note

If relevant, include:

```md
## Skills Applied
- sql-pro
```
