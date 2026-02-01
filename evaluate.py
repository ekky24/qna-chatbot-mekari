import requests
from llama_index.core.evaluation import SemanticSimilarityEvaluator
from llama_index.embeddings.ollama import OllamaEmbedding
import config

if "qwen3" in config.EMBEDDING_MODEL_NAME:
    embed_model = OllamaEmbedding(
        model_name=config.EMBEDDING_MODEL_NAME,
        base_url=config.MODEL_URL,
    )
else:
    raise ValueError("Unsupported embedding model")

evaluator = SemanticSimilarityEvaluator(embed_model=embed_model)

scores = []
for question, reference in config.EVALUATOR_QUESTION_ANSWER.items():
    print(f"Evaluating question: {question}")

    # getting response from the chat service
    payload = {
        "msg": question
    }
    _ = requests.get(f"{config.SERVICE_URL}/init")
    response = requests.post(f"{config.SERVICE_URL}/chat", json=payload)
    response_json = response.json()
    response = response_json.get("response", "")

    result = evaluator.evaluate(
        response=response,
        reference=reference
    )
    scores.append(result.score)
    
    print(f"Similarity Score: {result.score}")
    print("-" * 50)

print(f"Average Score: {sum(scores) / len(scores):.4f}")