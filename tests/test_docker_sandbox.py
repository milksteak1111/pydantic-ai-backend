"""Tests for DockerSandbox initialization (without running Docker)."""

import pytest


@pytest.fixture(scope="class")
def timeout_sandbox():
    """Shared Docker sandbox for TestDockerTimeoutEscaping class.

    Reduces container creation from 3 times to 1 time.
    """
    pytest.importorskip("docker")
    from pydantic_ai_backends import DockerSandbox

    sandbox = DockerSandbox()
    yield sandbox
    sandbox.stop()


@pytest.fixture(scope="class")
def edit_sandbox():
    """Shared Docker sandbox for TestDockerSandboxEdit class.

    Reduces container creation from 3 times to 1 time.
    """
    pytest.importorskip("docker")
    from pydantic_ai_backends import DockerSandbox

    sandbox = DockerSandbox()
    yield sandbox
    sandbox.stop()


class TestDockerSandboxInit:
    """Tests for DockerSandbox initialization parameters."""

    def test_init_default_values(self):
        """Test default initialization values."""
        from pydantic_ai_backends import DockerSandbox

        sandbox = DockerSandbox.__new__(DockerSandbox)
        # Call __init__ manually to test parameter defaults
        sandbox.__init__()

        assert sandbox._image == "python:3.12-slim"
        assert sandbox._work_dir == "/workspace"
        assert sandbox._auto_remove is True
        assert sandbox._idle_timeout == 3600
        assert sandbox._volumes == {}
        assert sandbox._runtime is None

    def test_init_with_volumes(self):
        """Test initialization with volumes parameter."""
        from pydantic_ai_backends import DockerSandbox

        volumes = {"/host/path": "/container/path"}
        sandbox = DockerSandbox.__new__(DockerSandbox)
        sandbox.__init__(volumes=volumes)

        assert sandbox._volumes == volumes

    def test_init_with_empty_volumes(self):
        """Test initialization with empty volumes dict."""
        from pydantic_ai_backends import DockerSandbox

        sandbox = DockerSandbox.__new__(DockerSandbox)
        sandbox.__init__(volumes={})

        assert sandbox._volumes == {}

    def test_init_with_none_volumes(self):
        """Test initialization with None volumes (default)."""
        from pydantic_ai_backends import DockerSandbox

        sandbox = DockerSandbox.__new__(DockerSandbox)
        sandbox.__init__(volumes=None)

        assert sandbox._volumes == {}

    def test_init_with_multiple_volumes(self):
        """Test initialization with multiple volume mappings."""
        from pydantic_ai_backends import DockerSandbox

        volumes = {
            "/host/workspace": "/workspace",
            "/host/data": "/data",
            "/host/config": "/config",
        }
        sandbox = DockerSandbox.__new__(DockerSandbox)
        sandbox.__init__(volumes=volumes)

        assert sandbox._volumes == volumes
        assert len(sandbox._volumes) == 3

    def test_init_with_all_parameters(self):
        """Test initialization with all parameters including volumes."""
        from pydantic_ai_backends import DockerSandbox

        volumes = {"/host/path": "/workspace"}
        sandbox = DockerSandbox.__new__(DockerSandbox)
        sandbox.__init__(
            image="python:3.11",
            sandbox_id="test-sandbox",
            work_dir="/app",
            auto_remove=False,
            idle_timeout=7200,
            volumes=volumes,
        )

        assert sandbox._image == "python:3.11"
        assert sandbox._id == "test-sandbox"
        assert sandbox._work_dir == "/app"
        assert sandbox._auto_remove is False
        assert sandbox._idle_timeout == 7200
        assert sandbox._volumes == volumes

    def test_init_with_session_id_alias(self):
        """Test that session_id works as alias for sandbox_id."""
        from pydantic_ai_backends import DockerSandbox

        volumes = {"/host": "/container"}
        sandbox = DockerSandbox.__new__(DockerSandbox)
        sandbox.__init__(session_id="my-session", volumes=volumes)

        assert sandbox._id == "my-session"
        assert sandbox._volumes == volumes


class TestDockerTimeoutEscaping:
    """Tests for timeout command escaping (fixes command!r bug).

    These tests verify that commands with quotes, variables, and pipes work
    correctly when timeout is specified. Previously failed due to command!r bug.
    """

    @pytest.mark.docker
    def test_execute_timeout_with_quotes(self, timeout_sandbox):
        """Test execute with timeout handles quoted strings correctly.

        Previously failed because command!r added extra quotes:
        command = "echo 'hello world'"
        command!r = "'echo \\'hello world\\''"  # BAD - extra quotes
        """
        # Command with double quotes
        result = timeout_sandbox.execute('echo "hello world"', timeout=5)
        assert result.exit_code == 0
        assert "hello world" in result.output

        # Command with single quotes
        result = timeout_sandbox.execute("echo 'goodbye world'", timeout=5)
        assert result.exit_code == 0
        assert "goodbye world" in result.output

    @pytest.mark.docker
    def test_execute_timeout_with_variables(self, timeout_sandbox):
        """Test execute with timeout handles shell variables correctly.

        Previously failed because command!r escaped $ incorrectly:
        command = "echo $HOME"
        command!r = "'echo $HOME'"  # $ gets escaped/not expanded
        """
        # Shell variable expansion
        result = timeout_sandbox.execute("echo $HOME", timeout=5)
        assert result.exit_code == 0
        # HOME should be expanded (not literal "$HOME")
        assert "$HOME" not in result.output or result.output.strip() != "$HOME"

        # Command substitution
        result = timeout_sandbox.execute("echo $(pwd)", timeout=5)
        assert result.exit_code == 0
        assert result.output.strip()  # Should output the working directory

    @pytest.mark.docker
    def test_execute_timeout_with_pipes(self, timeout_sandbox):
        """Test execute with timeout handles pipes and redirects correctly.

        Previously failed because command!r broke shell piping:
        command = "echo test | grep test"
        command!r = "'echo test | grep test'"  # Pipe becomes literal string
        """
        # Pipe command
        result = timeout_sandbox.execute("echo 'test line' | grep test", timeout=5)
        assert result.exit_code == 0
        assert "test line" in result.output

        # Multiple pipes
        result = timeout_sandbox.execute("echo 'hello world' | tr a-z A-Z | grep HELLO", timeout=5)
        assert result.exit_code == 0
        assert "HELLO WORLD" in result.output


class TestDockerSandboxEdit:
    """Tests for DockerSandbox.edit() method using Python string operations."""

    @pytest.mark.docker
    def test_edit_basic_single_occurrence(self, edit_sandbox):
        """Test basic edit with single occurrence."""
        # Write a simple file
        edit_sandbox.write("/workspace/test1.txt", "Hello, World!")

        # Edit single occurrence
        result = edit_sandbox.edit("/workspace/test1.txt", "World", "Universe")

        assert result.error is None
        assert result.occurrences == 1

        # Verify the change
        content = edit_sandbox.read("/workspace/test1.txt")
        assert "Universe" in content
        assert "World" not in content

    @pytest.mark.docker
    def test_edit_multiline_string(self, edit_sandbox):
        """Test editing multiline strings (main improvement over sed approach)."""
        # Write file with multiline content
        original = "def foo():\n    return 'old'\n\nprint('test')"
        edit_sandbox.write("/workspace/code.py", original)

        # Edit multiline string (this would fail with sed approach)
        old_function = "def foo():\n    return 'old'"
        new_function = "def foo():\n    return 'new'"

        result = edit_sandbox.edit("/workspace/code.py", old_function, new_function)

        assert result.error is None
        assert result.occurrences == 1

        # Verify the multiline replacement worked
        content = edit_sandbox.read("/workspace/code.py")
        assert "return 'new'" in content
        assert "return 'old'" not in content
        assert "print('test')" in content  # Rest of file unchanged

    @pytest.mark.docker
    def test_edit_multiple_occurrences_replace_all(self, edit_sandbox):
        """Test editing with multiple occurrences using replace_all."""
        # Write file with multiple occurrences
        edit_sandbox.write("/workspace/multi.txt", "foo bar foo baz foo")

        # Should fail without replace_all
        result = edit_sandbox.edit("/workspace/multi.txt", "foo", "qux")
        assert result.error is not None
        assert "3 times" in result.error

        # Should succeed with replace_all=True
        result = edit_sandbox.edit("/workspace/multi.txt", "foo", "qux", replace_all=True)
        assert result.error is None
        assert result.occurrences == 3

        # Verify all occurrences replaced
        content = edit_sandbox.read("/workspace/multi.txt")
        assert "qux" in content
        assert "foo" not in content
        assert content.count("qux") == 3
