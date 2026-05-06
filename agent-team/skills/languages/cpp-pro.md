# Skill: C++ Pro

## Purpose

Use this skill for professional C++ development in libraries, systems code, tests, and build configuration.

## Applies when

Use this skill when work involves:

- C++ source or header files
- CMake or build configuration
- memory ownership
- performance-sensitive code
- native tests
- ABI or API boundaries

## Detection triggers

Load this skill if task or repo contains:

```yaml
triggers:
  text:
    - C++
    - cpp
    - CMake
    - native
  files:
    - "*.cpp"
    - "*.cc"
    - "*.cxx"
    - "*.hpp"
    - "*.hh"
    - "CMakeLists.txt"
  code_symbols:
    - std::unique_ptr
    - std::shared_ptr
    - std::move
    - constexpr
```

## Developer instructions

- Follow existing standard version and style.
- Prefer RAII for resource ownership.
- Make ownership and lifetimes explicit.
- Avoid raw owning pointers.
- Preserve ABI/API compatibility unless task requires change.
- Keep CMake changes scoped.
- Do not trade correctness for premature optimization.

## Testing guidance

Look for:

```bash
cmake --build build
ctest --test-dir build
ninja test
make test
```

## Review checklist

- ownership and lifetimes are clear
- move/copy semantics are intentional
- undefined behavior risk is considered
- thread-safety assumptions are documented
- tests cover changed behavior
- build changes are minimal

## Anti-patterns

Avoid:

```yaml
anti_patterns:
  - raw owning pointers
  - manual new/delete without clear ownership
  - hidden undefined behavior
  - unnecessary template complexity
  - broad CMake rewrites
```

## Output note

If relevant, include:

```md
## Skills Applied
- cpp-pro
```
