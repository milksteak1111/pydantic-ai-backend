# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.4] - 2025-01-16

### Added

- `volumes` parameter to `DockerSandbox` for mounting host directories
  - Enables persistent storage that survives container restarts
  - Format: `{"/host/path": "/container/path"}`
- `workspace_root` parameter to `SessionManager` for automatic per-session storage
  - Creates `{workspace_root}/{session_id}/workspace` directories automatically
  - Mounts as volume so files persist across container lifecycle
- New tests for volumes and workspace_root functionality (140 total tests, 100% coverage)
- Documentation for persistent storage in README

### Fixed

- Files no longer lost when Docker container stops or application restarts (when volumes configured)

## [0.0.1] - 2025-12-28

### Added

- Initial release extracted from pydantic-deep
- `BackendProtocol` - Unified interface for file operations
- `SandboxProtocol` - Extended interface for command execution
- `StateBackend` - In-memory file storage
- `FilesystemBackend` - Real filesystem operations with path sandboxing
- `CompositeBackend` - Route operations to different backends by path prefix
- `BaseSandbox` - Abstract base class for sandbox implementations
- `DockerSandbox` - Docker container-based sandbox with full file and execution support
- `LocalSandbox` - Local subprocess-based sandbox (no isolation, for development)
- `SessionManager` - Multi-user session management for Docker sandboxes
- `RuntimeConfig` - Configuration model for Docker runtime environments
- Built-in runtimes: python-minimal, python-datascience, python-web, node-minimal, node-react
- Type definitions: `FileData`, `FileInfo`, `WriteResult`, `EditResult`, `ExecuteResponse`, `GrepMatch`
- Lazy loading for optional Docker dependencies
- Path validation and sandboxing for security
- Ripgrep integration for fast file searching (with Python regex fallback)
- PDF reading support in DockerSandbox
- Encoding detection with chardet
