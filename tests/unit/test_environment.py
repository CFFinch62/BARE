"""Unit tests for the BARE environment (scope management)."""

import pytest
from bare_core.environment import Environment
from bare_core.errors import BareRuntimeError


class TestEnvironment:
    def test_set_and_get(self):
        env = Environment()
        env.set("x", 5.0)
        assert env.get("x", 1) == 5.0

    def test_undefined_variable(self):
        env = Environment()
        with pytest.raises(BareRuntimeError, match="not defined"):
            env.get("x", 1)

    def test_reassignment(self):
        env = Environment()
        env.set("x", 5.0)
        env.set("x", 10.0)
        assert env.get("x", 1) == 10.0

    def test_has(self):
        env = Environment()
        assert not env.has("x")
        env.set("x", 5.0)
        assert env.has("x")

    def test_get_all_variables(self):
        env = Environment()
        env.set("x", 1.0)
        env.set("y", 2.0)
        all_vars = env.get_all_variables()
        assert all_vars == {"x": 1.0, "y": 2.0}

    def test_get_all_variables_is_copy(self):
        """get_all_variables should return a copy, not a reference."""
        env = Environment()
        env.set("x", 1.0)
        snapshot = env.get_all_variables()
        env.set("x", 99.0)
        assert snapshot["x"] == 1.0

    def test_scope_isolation(self):
        """Separate environments should be completely independent."""
        env1 = Environment()
        env2 = Environment()
        env1.set("x", 1.0)
        assert not env2.has("x")
