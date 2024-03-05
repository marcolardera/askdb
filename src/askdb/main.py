"""
Main GUI application
"""

import json
import logging
import os
import sys

from askdb.database import Database
from askdb.llm import question_to_sql, sql_to_text
from askdb.utils import get_config, get_prompt_template, query_result_to_table
from nicegui import ui, run
from pathlib import Path
from xdg_base_dirs import xdg_config_home

CONFIG_DIR=Path(xdg_config_home(), "askdb")
CONFIG_FILE="connections.json"

logging.basicConfig(level="INFO", format="%(asctime)s - %(levelname)s - %(message)s")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

try:
    config=get_config(CONFIG_DIR/CONFIG_FILE)
except FileNotFoundError:
    logging.error(f"{CONFIG_FILE} not found in config directory {CONFIG_DIR}")
    sys.exit()
except json.decoder.JSONDecodeError:
    logging.error(f"{CONFIG_FILE} contains invalid JSON")
    sys.exit()

db_options={item["name"] : item["connection_string"] for item in config}

def main() -> None:

    def ask_db():
        spinner.set_visibility(True)
        connection_string=db_options[db_select.value]
        question=question_label.value

        db=Database(connection_string)
        metadata=db.extract_metadata()

        prompt=get_prompt_template(connection_string)
        sql=question_to_sql(prompt, metadata, question)
        logging.info(sql)

        result=db.execute_sql_query(sql)

        logging.info(result)
        with open("prompts/result.txt") as file:
            prompt=file.read()
        answer=sql_to_text(prompt, question, sql, result.result)
        logging.info(answer)

        output.set_text(answer)
        query_md.set_content(f"```sql\n{sql}\n```")
        table_data=query_result_to_table(result)
        table.columns=table_data[0]
        table.rows=table_data[1]

        ui.update(output, query_md, table)
        spinner.set_visibility(False)

    async def ask_db_wrapper():
        try:
            await run.io_bound(ask_db)
        except Exception as e:
            logging.error(e, exc_info=True)
            ui.notify("Something went wrong...", position="top", type="negative", close_button="Close")
            spinner.set_visibility(False)

    
    
    ui.markdown("# AskDB GUI")

    db_select=ui.select(
        options=list(db_options.keys()),
        label="Select the database", 
        value=list(db_options.keys())[0]).classes("w-1/3")

    with ui.row().classes("w-full no-wrap"):
        question_label=ui.input("Ask a question").classes("w-4/5")
        ui.button("Submit", on_click=ask_db_wrapper).classes("w-1/5")

    ui.markdown("## Response:")
    spinner=ui.spinner(size="3em")
    spinner.set_visibility(False)
    output=ui.label()

    with ui.expansion("Show SQL", icon="storage").classes("w-full"):
        query_md=ui.markdown()
        table=ui.table(columns=[], rows=[])

    ui.run(title="AskDB", reload=False)


if __name__ in {"__main__", "__mp_main__"}:
    main()