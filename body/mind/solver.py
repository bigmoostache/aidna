from env_client import Task


def solve(task: Task) -> int:
    if task.operator == "+":
        return task.operand_a + task.operand_b
    elif task.operator == "-":
        return task.operand_a - task.operand_b
    elif task.operator == "*":
        return task.operand_a * task.operand_b
    elif task.operator == "/":
        return task.operand_a // task.operand_b
    else:
        raise ValueError(f"Unknown operator: {task.operator}")
