# SAAF COMPLIANCE PROTOCOL (Classified: @CNS)

## 1. Zero-Regression Protocol (The Shield)
- **Mandatory**: Identify dependent modules before any edit.
- **Verification**: Design a "Failure Test" that fails now but passes after the fix.
- **Sandbox**: Never run write/delete tests against Production databases.

## 2. Phase Gates Implementation
- Strictly follow the 8-phase governance lifecycle.
- **Authorized Phases**: Only proceed to the next phase if the current phase gate is approved.
- **Self-Healing**: Implement smart retries with exponential backoff for network operations.

## 3. TDD (Test-Driven Development)
- Write unit/integration tests before or alongside code implementation.
- All backend logic must have corresponding `pytest` cases.
- All Flutter UI must pass `flutter analyze` and widget tests.

## 4. Coding Standards (Clean Code Oath)
- **No Emojis**: Forbidden in `.py`, `.dart`, `.yaml`, `.json` files.
- **No Hardcoding**: All config must be loaded from `.env` or `config.yaml`.
- **Type Hinting**: Mandatory for all function signatures.
- **Modular Integrity**: Treat every file as a sealed implementation. Use public interfaces for interaction.

## 5. Security & Isolation
- Every database query must be filtered by `instance_name`.
- Protect PII and secrets at all times.

## 6. Theme-Agnostic Execution (SAAF-FRONTEND)
- **Neutral Executor**: The UI Agent MUST derive all styling, colors, and themes strictly from provided tokens or context.
- **No Defaults**: Never assume or force a dark/OLED theme by default. 
- **Dynamic Capabilities**: Usage of premium effects (Liquid Glass, Glow) must be dynamic and dependent on the provided design specification.
