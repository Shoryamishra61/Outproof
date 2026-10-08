"""In-memory isolated mutants must be detected by the existing boundary oracle."""

import ast
import inspect
import types

import pytest
from ground_rule import policy

from tests.release.test_boundaries import test_adversarial_boundary as boundary_oracle


@pytest.mark.parametrize(
    "gate,fault",
    [
        ("BUDGET", "budget"),
        ("CURRENCY", "currency"),
        ("DURATION", "duration"),
        ("WALKING", "walking"),
    ],
)
def test_boundary_oracle_kills_isolated_gate_mutant(gate: str, fault: str) -> None:
    tree = ast.parse(inspect.getsource(policy))
    changed = 0
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "check"
            and node.args
            and isinstance(node.args[0], ast.Attribute)
            and node.args[0].attr == gate
        ):
            node.args[1] = ast.Constant(value=True)
            changed += 1
    assert changed == 1
    namespace = dict(vars(policy))
    exec(compile(ast.fix_missing_locations(tree), "isolated_policy_mutant", "exec"), namespace)
    oracle = types.FunctionType(
        boundary_oracle.__code__,
        {**boundary_oracle.__globals__, "validate_plan": namespace["validate_plan"]},
    )
    boundary_oracle(fault, 0)
    with pytest.raises(AssertionError):
        oracle(fault, 0)
