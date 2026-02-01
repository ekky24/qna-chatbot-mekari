from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.ollama import OllamaEmbedding
import config

if "qwen3" in config.EMBEDDING_MODEL_NAME:
    embed_model = OllamaEmbedding(
        model_name=config.EMBEDDING_MODEL_NAME,
        base_url=config.MODEL_URL,
    )
else:
    raise ValueError("Unsupported embedding model") 

# Load documents from the specified directory
documents = SimpleDirectoryReader("raw_data/fraud_document").load_data()
print(f"Loaded {len(documents)} documents")

# Split documents into smaller chunks
text_splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)
nodes = text_splitter.get_nodes_from_documents(documents)
print(f"Split into {len(nodes)} chunks")

index = VectorStoreIndex(nodes, embed_model=embed_model)
index.storage_context.persist(persist_dir=f"mcp/storage_{config.EMBEDDING_MODEL_FILENAME_MAPPER[config.EMBEDDING_MODEL_NAME]}")

print("Indexing completed and persisted")