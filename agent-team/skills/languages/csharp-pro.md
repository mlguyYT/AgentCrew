# Skill: C# Pro

## Purpose

Use this skill for professional C# and .NET development in services, libraries, tests, and tooling.

## Applies when

Use this skill when work involves:

- C# source files
- .NET projects
- ASP.NET services
- LINQ
- async C#
- NuGet packages

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - C#
    - dotnet
    - .NET
    - ASP.NET
  files:
    - "*.cs"
    - "*.csproj"
    - "*.sln"
    - "Directory.Build.props"
    - "global.json"
  code_symbols:
    - async Task
    - IEnumerable
    - IQueryable
    - using var
```

## Developer instructions

- Follow existing project and namespace conventions.
- Use async/await consistently.
- Dispose resources with `using` or `await using`.
- Keep LINQ readable and avoid hidden multiple enumeration.
- Preserve nullable reference type intent.
- Do not add NuGet packages without clear justification.

## Testing guidance

Look for:

```bash
dotnet test
dotnet build
dotnet format --verify-no-changes
```

## Review checklist

- async code is awaited correctly
- disposable resources are handled
- nullable annotations are respected
- LINQ does not hide expensive behavior
- tests cover changed behavior
- project file changes are scoped

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - sync-over-async
  - swallowing exceptions silently
  - multiple enumeration surprises
  - broad service registration changes
  - unrelated solution file churn
```

## Output note

If relevant, include:

```md
## Skills Applied
- csharp-pro
```
