import openai

from askdb.database import Table, Database

MODEL="gpt-4-turbo-preview"

def question_to_sql(prompt_template, schema: list[Table], question: str) -> str:
    schema_section=""
    for table in schema:
        schema_section += table.ddl
        schema_section += Database.pretty_print_examples(table.examples)
    
    prompt_template=prompt_template.replace("{schema}", schema_section)
    prompt_template=prompt_template.replace("{question}", question)

    client=openai.OpenAI()
    result=client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt_template}]
    )

    return result.choices[0].message.content

def sql_to_text(prompt_template: str, question: str, query: str, result: str) -> str:
    prompt_template=prompt_template.replace("{question}", question)
    prompt_template=prompt_template.replace("{query}", query)
    prompt_template=prompt_template.replace("{result}", str(result))

    client=openai.OpenAI()
    result=client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt_template}]
    )

    return result.choices[0].message.content