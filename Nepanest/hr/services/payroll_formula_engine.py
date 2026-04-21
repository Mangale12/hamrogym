import ast
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP


ZERO = Decimal("0.00")


class FormulaEvaluationError(ValueError):
    pass


def to_decimal(value) -> Decimal:
    if value in (None, ""):
        return ZERO
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def apply_rounding(value, rounding_rule: str) -> Decimal:
    value = to_decimal(value)
    if rounding_rule == "round_0":
        return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    if rounding_rule == "ceil":
        return value.quantize(Decimal("0.01"), rounding=ROUND_CEILING)
    if rounding_rule == "floor":
        return value.quantize(Decimal("0.01"), rounding=ROUND_FLOOR)
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def evaluate_formula(expression: str, context: dict[str, Decimal]) -> Decimal:
    if not expression or not str(expression).strip():
        return ZERO
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise FormulaEvaluationError(f"Invalid formula syntax: {expression}") from exc
    return apply_rounding(_eval_node(tree.body, context), "round_2")


def _eval_node(node, context):
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left, context)
        right = _eval_node(node.right, context)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            if right == 0:
                raise FormulaEvaluationError("Division by zero in formula.")
            return left / right
        raise FormulaEvaluationError("Unsupported formula operator.")

    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand, context)
        if isinstance(node.op, ast.USub):
            return operand * Decimal("-1")
        if isinstance(node.op, ast.UAdd):
            return operand
        raise FormulaEvaluationError("Unsupported unary operator.")

    if isinstance(node, ast.Name):
        return to_decimal(context.get(node.id, ZERO))

    if isinstance(node, ast.Constant):
        return to_decimal(node.value)

    raise FormulaEvaluationError("Unsupported expression in formula.")
