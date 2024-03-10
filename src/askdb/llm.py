import openai

from askdb.database import Table, Database

def get_openai_models() -> list[str]:
    client=openai.OpenAI()
    models=[]
    for model in client.models.list():
        models.append(model.id)
    models.sort()
    return [m for m in models if m.startswith("gpt") and "instruct" not in m]

def question_to_sql(prompt_template, schema: list[Table], question: str, model:str) -> str:
    schema_section=""
    for table in schema:
        schema_section += table.ddl
        schema_section += Database.pretty_print_examples(table.examples)
    
    prompt_template=prompt_template.replace("{schema}", schema_section)
    prompt_template=prompt_template.replace("{question}", question)

    client=openai.OpenAI()
    result=client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt_template}]
    )

    return result.choices[0].message.content

def sql_to_text(prompt_template: str, question: str, query: str, result: str, model: str) -> str:
    prompt_template=prompt_template.replace("{question}", question)
    prompt_template=prompt_template.replace("{query}", query)
    prompt_template=prompt_template.replace("{result}", str(result))

    client=openai.OpenAI()
    result=client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt_template}]
    )

    return result.choices[0].message.content