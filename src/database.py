from dataclasses import dataclass
from sqlalchemy import create_engine, text
from sqlalchemy.schema import MetaData, CreateTable

@dataclass
class Table:
    name: str
    ddl: str
    examples: list[tuple]

@dataclass
class QueryResult:
    columns: list[str]
    result: list[tuple]

class Database:
    def __init__(self, connection_string: str) -> None:
        # SqlAlchemy no longer supports the postgres:// uri
        connection_string=connection_string.replace("postgres://", "postgresql://")
        connection_string=connection_string.replace("mysql://", "mysql+pymysql://")  
        engine=create_engine(connection_string)
        self.engine=engine

    def extract_metadata(self) -> list[Table]:
        metadata=MetaData()
        metadata.reflect(bind=self.engine)

        tables_list=[]
        for table in metadata.sorted_tables:
            ddl=CreateTable(table).compile(self.engine)

            with self.engine.connect() as conn:
                examples=conn.execute(table.select().limit(3))  
                examples=examples.fetchall()

            tables_list.append(Table(name=table.name, ddl=str(ddl), examples=examples))

        return tables_list
    
    def execute_sql_query(self, query: str) -> QueryResult:
        with self.engine.connect() as conn:
            result=conn.execute(text(query))
        return QueryResult(columns=list(result.keys()), result=result.fetchall())

    @staticmethod
    def pretty_print_examples(example: list[tuple]) -> str:
        result=[]
        for row in example:
            row=[str(item) for item in row]
            result.append(",".join(row))
        return "\n".join(result) + "\n"
