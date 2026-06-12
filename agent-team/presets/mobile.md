# Mobile App Preset

## Use When

Use for React Native, Flutter, native iOS (Swift), or native Android (Kotlin) projects.

## Default Skills

```text
typescript-pro when React Native
javascript-pro for older RN projects
java-pro for Android / Kotlin
```

## Architecture Focus

- keep navigation, state, network, and presentation layers separated
- preserve user-visible behavior across release channels
- gate any change that affects offline behavior, deep links, push notifications, or background tasks
- isolate platform-specific code paths so Android / iOS divergence is obvious

## Validation Defaults

- platform unit tests (jest / xctest / junit) when configured
- snapshot tests on UI components when they exist
- integration tests for navigation, deep links, and persistence
- a release-channel smoke test when shipping to beta

## Review Gates

- compatibility rollout check on schema, deep-link, or notification changes
- dependency and supply-chain gate on package.json / Podfile / build.gradle changes
- product behavior review on any user-visible change

## Required Specialists Suggestion

- Security Reviewer on keystore, biometric, payment, or deep-link routing changes
- UX / Design Reviewer on any screen, navigation, or interaction change
- Release Manager before any beta or production channel push

## Config Defaults (suggested)

```yaml
quality_profile: strict
required_specialists:
  - paths: ["**/screens/**", "**/components/**", "**/navigation/**"]
    roles: ["UX / Design Reviewer"]
  - paths: ["**/auth/**", "**/payments/**", "**/biometric*", "**/keychain*"]
    roles: ["Security Reviewer"]
```
