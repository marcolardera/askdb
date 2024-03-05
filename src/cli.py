"""
Basic command line interface for testing purposes
"""

import click
import json
import logging
import sys

from database import Database
from llm import question_to_sql, sql_to_text
from pathlib import Path
from utils import get_config, get_prompt_template
from xdg_base_dirs import xdg_config_home

CONFIG_DIR=Path(xdg_config_home(), "askdb")
CONFIG_FILE="connections.json"

logging.basicConfig(level="INFO", format="%(asctime)s - %(levelname)s - %(message)s")

@click.command()
@click.argument("question")  
@click.option("database", "--database", "-d", help="Name of the database (from connections.json)")  
def main(question, database) -> None:
    
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
    db=Database(connection_string)

    metadata=db.extract_metadata()
    prompt=get_prompt_template(connection_string)

    sql=question_to_sql(prompt, metadata, question)
    logging.info(f"Query = {sql}")

    result=db.execute_sql_query(sql)
    logging.info(f"Result object = {result}")

    with open("src/prompts/result.txt") as file:
        prompt=file.read()

    answer=sql_to_text(prompt, question, sql, result.result)
    logging.info(f"Answer: {answer}")


if __name__ == "__main__":
    main()