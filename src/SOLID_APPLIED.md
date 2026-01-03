# SOLID Applied

This document summarizes how the refactor applies SOLID principles while preserving
behavior.

## Structure

- `src/altrus_cli/app/` — composition root and wiring (ScannerApp)
- `src/altrus_cli/domain/` — core services (ScannerService)
- `src/altrus_cli/ports/` — interfaces/Protocols
- `src/altrus_cli/infrastructure/` — concrete adapters (UDP/TCP, YAML, predictor)
- `src/altrus_cli/tests/` — unit tests for domain and adapters

## SOLID mapping

- **SRP:** ScannerService focuses on orchestration only; formatting, config loading, and
  transport are separated into their own modules.
- **OCP:** New transports or predictors can be added by implementing `PayloadReceiver`
  or `Predictor` without modifying ScannerService.
- **LSP:** Protocol implementations keep method contracts stable (`iter_messages`,
  `predict`) and can be swapped without behavioral changes.
- **ISP:** Small interfaces (receiver, predictor, formatter, config reader) replace a
  single monolithic API.
- **DIP:** High-level services depend on `ports` interfaces; concrete socket and file
  implementations live in `infrastructure`.
