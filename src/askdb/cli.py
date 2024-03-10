"""
Basic command line interface for testing purposes
"""

import click
import json
import logging
import os
import sys

from askdb.database import Database
from askdb.llm import question_to_sql, sql_to_text
from askdb.utils import get_config, get_prompt_template
from pathlib import Path
from xdg_base_dirs import xdg_config_home

CONFIG_DIR=Path(xdg_config_home(), "askdb")
CONFIG_FILE="connections.json"
DEFAULT_MODEL="gpt-4-turbo-preview"

logging.basicConfig(level="INFO", format="%(asctime)s - %(levelname)s - %(message)s")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

@click.command()
@click.argument("question")  
@click.option("database", "--database", "-d", help="Name of the database (from connections.json)")
@click.option("model", "--model", "-m", default=DEFAULT_MODEL, help="OpenAI model to use")  
def main(question, database, model) -> None:
    
    try:
        config=get_config(CONFIG_DIR/CONFIG_FILE)
    except FileNotFoundError:
        logging.error(f"{CONFIG_FILE} not found in config directory {CONFIG_DIR}")
        sys.exit()
    except json.decoder.JSONDecodeError:
        logging.error(f"{CONFIG_FILE} contains invalid JSON")
        sys.exit()

    if database:
        connection_string=None
        for item in config:
            if item["name"]==database:
                connection_string=item["connection_string"]
        if connection_string==None:
            logging.error(f"Unable to locate database {database} in the connection file")
            sys.exit()
    else:
        connection_string=config[0]["connection_string"]

    logging.info(f"Connection string = {connection_string}")
    logging.info(f"Model = {model}")
    db=Database(connection_string)

    metadata=db.extract_metadata()
    prompt=get_prompt_template(connection_string)

    sql=question_to_sql(prompt, metadata, question, model)
    logging.info(f"Query = {sql}")

    result=db.execute_sql_query(sql)
    logging.info(f"Result object = {result}")

    with open("prompts/result.txt") as file:
        prompt=file.read()

    answer=sql_to_text(prompt, question, sql, result.result, model)
    logging.info(f"Answer: {answer}")


if __name__ == "__main__":
    main()