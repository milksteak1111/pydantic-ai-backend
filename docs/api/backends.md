# Backends API

## LocalBackend

::: pydantic_ai_backends.backends.local.LocalBackend
    options:
      show_root_heading: true
      members:
        - __init__
        - ls_info
        - read
        - write
        - edit
        - glob_info
        - grep_raw
        - execute
        - execute_enabled

## StateBackend

::: pydantic_ai_backends.backends.state.StateBackend
    options:
      show_root_heading: true
      members:
        - __init__
        - files
        - ls_info
        - read
        - write
        - edit
        - glob_info
        - grep_raw

## CompositeBackend

::: pydantic_ai_backends.backends.composite.CompositeBackend
    options:
      show_root_heading: true
      members:
        - __init__
        - ls_info
        - read
        - write
        - edit
        - glob_info
        - grep_raw
