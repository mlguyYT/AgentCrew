# Skill: Java Pro

## Purpose

Use this skill for professional Java development in services, libraries, tests, and build tooling.

## Applies when

Use this skill when work involves:

- Java source files
- JVM services
- Maven or Gradle builds
- Java tests
- Spring or Jakarta projects
- concurrency or resource handling

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - Java
    - JVM
    - Maven
    - Gradle
  files:
    - "*.java"
    - "pom.xml"
    - "build.gradle"
    - "build.gradle.kts"
    - "settings.gradle"
  code_symbols:
    - public class
    - Optional
    - Stream
    - CompletableFuture
```

## Developer instructions

- Follow existing package and layering conventions.
- Prefer clear, explicit code over clever stream chains.
- Handle resources with try-with-resources where applicable.
- Preserve public API compatibility unless task requires a break.
- Avoid introducing framework annotations inconsistently.
- Do not add dependencies without a clear need.

## Testing guidance

Look for:

```bash
./gradlew test
./gradlew check
mvn test
mvn verify
```

## Review checklist

- nullability and Optional use are intentional
- resources are closed safely
- concurrency is bounded and understandable
- tests cover changed behavior
- build configuration changes are scoped
- public API changes are documented

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - broad catch blocks that hide failures
  - unnecessary inheritance
  - overcomplicated stream pipelines
  - mutable shared state without synchronization
  - unrelated build file churn
```

## Output note

If relevant, include:

```md
## Skills Applied
- java-pro
```
