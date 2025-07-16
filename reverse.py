import pandas as pd
import yaml
from collections import defaultdict

# Load Excel
df = pd.read_csv("output.csv")
df = df.where(pd.notnull(df), None)

# Normalize types
df['LOV_TYPE'] = df['LOV_TYPE'].str.upper()

priority = {
    "PROCESS_GROUP": 0,
    "PROCESS_TASK": 1,
    "PROCESS_DESCRIPTION": 2,
    "PROCESS_DEPENDENCY": 3,
    "PROCESS_REF": 4,
    "PROCESS_TOOL": 5,
    "PROCESS_POC": 6,
    "PROCESS_DAY": 7
}
df['PRIORITY'] = df['LOV_TYPE'].map(priority).fillna(99)
df.sort_values(by=['PRIORITY', 'LOV_PARENT_TYPE', 'LOV_PARENT', 'LOV_TYPE', 'LOV_SEQUENCE'], inplace=True)
# Store workflows
workflow = []

# Group-level storage
group_dict = {}

for _, row in df.iterrows():
    lov_type = row['LOV_TYPE']
    lov_value = row['LOV_VALUE']
    lov_display = row['LOV_DISPLAY_VALUE']
    lov_parent_type = row['LOV_PARENT_TYPE']
    lov_parent = row['LOV_PARENT']

    if lov_type == 'PROCESS_GROUP':
        group_dict[lov_value] = {
            'name': lov_value,
            'display_value': lov_display,
            'description': '',  # to be filled later
            'dependency': '',
            'ref': [],
            'tool': [],
            'poc': [],
            'tasks': []
        }

    elif lov_type == 'PROCESS_DESCRIPTION' and lov_parent_type == 'PROCESS_GROUP':
        group_dict[lov_parent]['description'] = lov_value

    elif lov_type == 'PROCESS_DEPENDENCY' and lov_parent_type == 'PROCESS_GROUP':
        group_dict[lov_parent]['dependency'] = lov_value

    elif lov_type == 'PROCESS_REF' and lov_parent_type == 'PROCESS_GROUP':
        group_dict[lov_parent]['ref'].append({'value': lov_value, 'display_value': lov_display})

    elif lov_type == 'PROCESS_TOOL' and lov_parent_type == 'PROCESS_GROUP':
        group_dict[lov_parent]['tool'].append({'value': lov_value, 'display_value': lov_display})

    elif lov_type == 'PROCESS_POC' and lov_parent_type == 'PROCESS_GROUP':
        group_dict[lov_parent]['poc'].append({'value': lov_value, 'display_value': lov_display})

    elif lov_type == 'PROCESS_TASK':
        # Add empty shell task
        for g in group_dict.values():
            if g['name'] == lov_parent:
                g['tasks'].append({
                    'name': lov_value,
                    'display_value': lov_display,
                    'description': '',
                    'dependency': '',
                    'ref': [],
                    'tool': [],
                    'poc': [],
                    'day': None
                })
                break

    elif lov_type.startswith("PROCESS_") and lov_parent_type == "PROCESS_TASK":
        # Find the task to update
        for g in group_dict.values():
            for task in g['tasks']:
                if task['name'] == lov_parent:
                    if lov_type == 'PROCESS_DESCRIPTION':
                        task['description'] = lov_value
                    elif lov_type == 'PROCESS_DEPENDENCY':
                        task['dependency'] = lov_value
                    elif lov_type == 'PROCESS_REF':
                        task['ref'].append({'value': lov_value, 'display_value': lov_display})
                    elif lov_type == 'PROCESS_TOOL':
                        task['tool'].append({'value': lov_value, 'display_value': lov_display})
                    elif lov_type == 'PROCESS_POC':
                        task['poc'].append({'value': lov_value, 'display_value': lov_display})
                    elif lov_type == 'PROCESS_DAY':
                        try:
                            task['day'] = int(lov_value)
                        except ValueError:
                            task['day'] = lov_value  # fallback to string if parsing fails
                    break

# Assemble YAML structure
workflow_yaml = {'Workflow': list(group_dict.values())}

# Output to YAML file
with open("output.yaml", "w") as f:
    yaml.dump(workflow_yaml, f, sort_keys=False)

print("✅ YAML file 'output.yaml' generated.")
