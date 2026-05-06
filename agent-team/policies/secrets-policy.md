# Policy: Secrets Handling

## Rule

Agents must never expose, commit, or print secrets.

---

## Secrets include

- API keys
- access tokens
- refresh tokens
- private keys
- passwords
- database credentials
- OAuth credentials
- signing keys
- webhook secrets

---

## Agent behavior

Agents must:

- avoid reading secrets unless necessary
- avoid printing environment values
- avoid committing `.env`
- use `.env.example` for placeholders
- mask sensitive values in reports
- warn if secrets appear in diffs

---

## If a secret is found

If an agent detects a secret in code or git diff:

1. stop normal work
2. warn the human
3. do not repeat the secret
4. recommend rotation
5. remove from code if instructed

---

## Placeholder format

Use placeholders like:

```text
__REPLACE_WITH_API_KEY__
__REPLACE_WITH_WEBHOOK_SECRET__
__REPLACE_WITH_DATABASE_PASSWORD__
```
