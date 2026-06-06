import sys
import os
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)
# pyrefly: ignore [missing-import]
from mcp.server.fastmcp import FastMCP
from db_connector import connect_db, close_conn
# pyrefly: ignore [missing-import]
from llama_index.core import StorageContext, load_index_from_storage
# pyrefly: ignore [missing-import]
from llama_index.embeddings.ollama import OllamaEmbedding
# pyrefly: ignore [missing-import]
from llama_index.core import Settings
# pyrefly: ignore [missing-import]
from llama_index.core.postprocessor import SimilarityPostprocessor
import config

mcp = FastMCP('qna-mekari-mcp')

@mcp.tool()
def read_transaction(query: str = "SELECT * FROM transactions LIMIT 5") -> list:
    """
    Read data from the "transactions" table using a SQL SELECT query. 
    The table contains legitimate and fraud credit card transactions from the duration 1st Jan 2019 - 31st Dec 2020. 
    It covers credit cards of 1000 customers doing transactions with a pool of 800 merchants. 

    Args:
        query (str): SQL SELECT query. 
        Defaults to "SELECT * FROM transactions".
            Examples:
            - "SELECT cc_num, merchant, category, amt FROM transactions"
            - "SELECT cc_num, merchant, category, amt FROM transactions WHERE first = 'John Doe'"
            - "SELECT cc_num, merchant, category, amt FROM transactions ORDER BY first DESC"

    Schema:
        - id: Numeric field => The identifier of transaction.
        - trans_date_trans_time: Datetime field => The transaction date and time.
        - cc_num: Text field => The cardholder's credit card number.
        - merchant: Text field => The merchant name.
        - category: Text field => The category of the merchant.
        - amt: Numeric field => The amount of the transaction.
        - first: Text field => The cardholder's first name.
        - last: Text field => The cardholder's last name.
        - gender: Char field => The cardholder's gender. M for Male, F for Female.
        - street: Text field => The cardholder's street address.
        - city: Text field => The cardholder's city.
        - state: Text field => The cardholder's state.
        - zip: Text field => The cardholder's zip code. 
        - lat: Numeric field => The cardholder's latitude coordinate.
        - long: Numeric field => The cardholder's longitude coordinate.
        - city_pop: Numeric field => The population of the cardholder's city.
        - job: Text field => The cardholder's job title.
        - dob: Date field => The cardholder's date of birth
        - trans_num: Text field => The transaction number.
        - unix_time: Numeric field => The Unix timestamp of the transaction.
        - merch_lat: Numeric field => The merchant's latitude coordinate.
        - merch_long: Numeric field => The merchant's longitude coordinate.
        - is_fraud: Tinyint field => 1 if the transaction is fraudulent, 0 otherwise.
    
    Returns:
        list: List of tuples containing the query results.
    
    """
    conn, cursor = connect_db()
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error reading data: {e}")
        return []
    finally:
        close_conn(conn)

@mcp.tool()
def search_fraud_manuals(query: str) -> str:
    """
    Search fraud manual documents using the provided query string.
    
    Returns:
        str: The search results from the fraud manual documents.
    """
    embed_model = OllamaEmbedding(
        model_name=config.EMBEDDING_MODEL_NAME,
        base_url=config.MODEL_URL,
    )
    Settings.embed_model = embed_model
    Settings.llm = None

    storage_context = StorageContext.from_defaults(persist_dir=\
        f"storage_{config.EMBEDDING_MODEL_FILENAME_MAPPER[config.EMBEDDING_MODEL_NAME]}")
    index = load_index_from_storage(storage_context, embed_model=embed_model)
    query_engine = index.as_query_engine(
        similarity_top_k=8,
        response_mode="context_only",
        llm=None,
        node_postprocessors=[
            SimilarityPostprocessor(similarity_cutoff=0.6)
        ]
    )

    response = query_engine.query(query)
    return str(response)

if __name__ == "__main__":
    print("Starting server... ")
    mcp.settings.host = "127.0.0.1"
    mcp.settings.port = 4000
    mcp.run(transport="sse")

