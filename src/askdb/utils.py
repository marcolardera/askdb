import json

from askdb.database import QueryResult

def get_config(file) -> list[dict]:
    with open(file) as jsonfile:
        content=jsonfile.read()
        return json.loads(content)

def get_prompt_template(connection_string: str) -> str:
    prefix=connection_string.split("://")[0]
    prefix=prefix.replace("postgres://", "postgresql://")
    try:
        with open(f"prompts/{prefix}.txt") as file:
            prompt=file.read()
    except FileNotFoundError:
        with open(f"prompts/general.txt") as file:
            prompt=file.read()
    
    return prompt

def query_result_to_table(result: QueryResult) -> tuple[list[dict], list[dict]]:
    """Conversion from the QueryResult object to a data structure suitable for NiceGUI tables"""
    columns=[]
    rows=[]
    for c in result.columns:
        columns.append({"name": c, "label": c, "field": c})
    
    for r in result.result:
        rows.append(dict(zip(result.columns, r)))
    
    return (columns, rows)