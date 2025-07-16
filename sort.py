import pandas as pd

# Load unsorted CSV
df = pd.read_csv("input.csv")
df = df.where(pd.notnull(df), None)  # Replace NaN with None

# Helper: priority of group-level and task-level fields
group_field_order = {
    "PROCESS_DESCRIPTION": 1,
    "PROCESS_DEPENDENCY": 2,
    "PROCESS_REF": 3,
    "PROCESS_TOOL": 4,
    "PROCESS_POC": 5,
    # "PROCESS_TASK": 6
}

task_field_order = {
    "PROCESS_DESCRIPTION": 1,
    "PROCESS_DEPENDENCY": 2,
    "PROCESS_REF": 3,
    "PROCESS_TOOL": 4,
    "PROCESS_POC": 5,
    "PROCESS_DAY": 6
}

# Output list
sorted_rows = []

# Step 1: Get all PROCESS_GROUPs sorted by LOV_SEQUENCE
groups = df[df["LOV_TYPE"] == "PROCESS_GROUP"].sort_values("LOV_SEQUENCE")

for _, group_row in groups.iterrows():
    group_name = group_row["LOV_VALUE"]

    # Append the PROCESS_GROUP row itself
    # sorted_rows.append(group_row)
    sorted_rows.append(group_row.to_dict())

    # Step 2: Add group-level items in fixed order
    group_items = df[(df["LOV_PARENT_TYPE"] == "PROCESS_GROUP") & (df["LOV_PARENT"] == group_name)]
    for field, order in group_field_order.items():
        items = group_items[group_items["LOV_TYPE"] == field].sort_values("LOV_SEQUENCE")
        sorted_rows.extend(items.to_dict("records"))

    # Step 3: Add task-level items (PROCESS_TASK + children)
    tasks = df[(df["LOV_TYPE"] == "PROCESS_TASK") & (df["LOV_PARENT_TYPE"] == "PROCESS_GROUP") & (df["LOV_PARENT"] == group_name)].sort_values("LOV_SEQUENCE")

    for _, task_row in tasks.iterrows():
        task_name = task_row["LOV_VALUE"]

        # Add the task row itself
        # sorted_rows.append(task_row)
        sorted_rows.append(task_row.to_dict())

        # Add children of this task in fixed order
        task_items = df[(df["LOV_PARENT_TYPE"] == "PROCESS_TASK") & (df["LOV_PARENT"] == task_name)]
        for field, order in task_field_order.items():
            items = task_items[task_items["LOV_TYPE"] == field].sort_values("LOV_SEQUENCE")
            sorted_rows.extend(items.to_dict("records"))

# Convert to DataFrame and save
sorted_df = pd.DataFrame(sorted_rows)
sorted_df.to_csv("sorted_output.csv", index=False)

print("✅ Sorted CSV written to sorted_output.csv")
