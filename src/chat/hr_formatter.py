def format_hr_insight(total_overtime: int, left_overtime: int, pct: float) -> str:
    return (
        "Based on the HR dataset:\n"
        f"- Employees with OverTime='Yes': {total_overtime}\n"
        f"- Of those, employees who left (Attrition='Yes'): {left_overtime}\n"
        f"- Attrition rate among overtime employees: {pct:.2f}%\n\n"
        "HR interpretation (consultant view):\n"
        "Overtime is often associated with workload strain and burnout risk. "
        "If this rate is notably higher than the overall attrition rate, consider "
        "workload balancing, manager coaching, and targeted retention actions for roles "
        "with frequent overtime."
    )
