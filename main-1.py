import yaml
import pandas as pd
import logging

# Set up logging to file
logging.basicConfig(
    filename="validation.log",
    level=logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

with open("output.yaml") as f:
# with open("workflow.yaml") as f:
    data = yaml.safe_load(f)

rows = []

def add_row(lov_type, lov_value, lov_display, parent_type, parent, sequence):
    rows.append({
        "LOV_TYPE": lov_type,
        "LOV_VALUE": lov_value,
        "LOV_DISPLAY_VALUE": lov_display,
        "LOV_PARENT_TYPE": parent_type,
        "LOV_PARENT": parent,
        "LOV_SEQUENCE": sequence
    })

# Define required fields
REQUIRED_GROUP_FIELDS = ['name', 'display_value', 'dependency', 'description']
REQUIRED_TASK_FIELDS = ['name', 'display_value', 'dependency', 'description', 'ref', 'tool', 'poc','day']

for i, group in enumerate(data['Workflow'], 1):
    # Check required group fields
    for field in REQUIRED_GROUP_FIELDS:
        if field not in group:
            logging.warning(f"Missing required field '{field}' in PROCESS_GROUP at index {i}")
            continue  # optional: raise ValueError here

    group_name = group.get('name', f"UnnamedGroup_{i}")
    group_display = group.get('display_value', group_name)
    add_row("PROCESS_GROUP", group_name, group_display, "", "", i)

    if 'description' in group:
        add_row("PROCESS_DESCRIPTION", group['description'], group['description'], "PROCESS_GROUP", group_name, 1)
    else:
        logging.warning(f"Missing 'description' in group '{group_name}'")

    deps = group.get('dependency')

    if deps is None:
        deps = ['']  # Add an empty row
    elif isinstance(deps, str):
        deps = [deps]

    for j, dep in enumerate(deps, 1):
        add_row('PROCESS_DEPENDENCY', dep, dep, 'PROCESS_GROUP', group_name, j)

    for j, ref in enumerate(group.get('ref', []), 1):
        add_row("PROCESS_REF", ref['value'], ref['display_value'], "PROCESS_GROUP", group_name, j)

    for j, tool in enumerate(group.get('tool', []), 1):
        add_row("PROCESS_TOOL", tool['value'], tool['display_value'], "PROCESS_GROUP", group_name, j)

    for j, poc in enumerate(group.get('poc', []), 1):
        add_row("PROCESS_POC", poc['value'], poc['display_value'], "PROCESS_GROUP", group_name, j)

    for t_idx, task in enumerate(group.get('tasks', []), 1):
        for field in REQUIRED_TASK_FIELDS:
            if field not in task:
                logging.warning(f"Missing required field '{field}' in task under group '{group_name}' (task index {t_idx})")
                continue

        task_name = task.get('name', f"UnnamedTask_{t_idx}")
        task_display = task.get('display_value', task_name)
        add_row("PROCESS_TASK", task_name, task_display, "PROCESS_GROUP", group_name, t_idx)

        if 'description' in task:
            add_row("PROCESS_DESCRIPTION", task['description'], task['description'], "PROCESS_TASK", task_name, 1)

        deps = task.get('dependency')

        if deps is None:
            deps = ['']
        elif isinstance(deps, str):
            deps = [deps]

        for j, dep in enumerate(deps, 1):
            add_row('PROCESS_DEPENDENCY', dep, dep, 'PROCESS_TASK', task_name, j)

        for j, ref in enumerate(task.get('ref', []), 1):
            add_row("PROCESS_REF", ref['value'], ref['display_value'], "PROCESS_TASK", task_name, j)

        for j, tool in enumerate(task.get('tool', []), 1):
            add_row("PROCESS_TOOL", tool['value'], tool['display_value'], "PROCESS_TASK", task_name, j)

        for j, poc in enumerate(task.get('poc', []), 1):
            add_row("PROCESS_POC", poc['value'], poc['display_value'], "PROCESS_TASK", task_name, j)

        if 'day' in task:
            add_row("PROCESS_DAY", str(task['day']), str(task['day']), "PROCESS_TASK", task_name, 1)
        else:
            logging.warning(f"Missing 'day' in task '{task_name}'")

# Create DataFrame
df = pd.DataFrame(rows, columns=[
    "LOV_TYPE", "LOV_VALUE", "LOV_DISPLAY_VALUE",
    "LOV_PARENT_TYPE", "LOV_PARENT", "LOV_SEQUENCE"
])

# Save output if needed
# df.to_csv("output.csv", index=False)
df.to_csv("output1.csv", index=False)

print(df)
