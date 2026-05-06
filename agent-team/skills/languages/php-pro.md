# Skill: PHP Pro

## Purpose

Use this skill for professional PHP development in web applications, libraries, tests, and framework code.

## Applies when

Use this skill when work involves:

- PHP source files
- Composer projects
- PHP web applications
- Laravel or Symfony-style code
- PHP tests
- database-backed PHP features

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - PHP
    - Composer
    - Laravel
    - Symfony
  files:
    - "*.php"
    - "composer.json"
    - "composer.lock"
    - "phpunit.xml"
  code_symbols:
    - namespace
    - use
    - class
    - trait
    - interface
```

## Developer instructions

- Follow existing framework and namespace conventions.
- Prefer typed parameters and return types when consistent with the project.
- Keep controller/request/business logic boundaries consistent.
- Validate user input through project conventions.
- Avoid leaking internal exception details.
- Do not add Composer dependencies without clear need.

## Testing guidance

Look for:

```bash
composer test
vendor/bin/phpunit
php artisan test
composer lint
```

## Review checklist

- input validation follows project conventions
- database writes are intentional and tested
- exceptions do not leak internals
- typed signatures are accurate
- tests cover changed behavior
- Composer changes are scoped

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - mixing business logic into controllers when services exist
  - raw SQL with interpolated user input
  - broad Composer updates
  - suppressing errors with @
  - changing framework conventions casually
```

## Output note

If relevant, include:

```md
## Skills Applied
- php-pro
```
