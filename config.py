SERVICE_URL = 'http://localhost:5000'
MCP_SERVER_URL = 'http://localhost:4000/sse'
MODEL_URL = 'http://192.168.98.202:11434'

MODEL_NAME = 'qwen3:4b'
EMBEDDING_MODEL_NAME = 'qwen3-embedding:4b'

EMBEDDING_MODEL_FILENAME_MAPPER = {
    'qwen3-embedding:4b': 'qwen3',
}
SYSTEM_PROMPT = """
    You are an AI assistant for Question and Answering system.
    Your answer should be professional and precise based on the tools you have access to.
    Before you help a user, you need to work with tools to interact with 
    our database which contains fraudulent and non-fraudulent transaction data, and 
    you also could interact with fraud manual documents.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
"""

EVALUATOR_QUESTION_ANSWER = {
    "How is credit card fraud defined in the document?": "When an individual uses another individual's credit card for personal reasons while the owner of the card and the card issuer are not aware of the fact that the card is being used. Further, the individual using the card has no connection with the cardholder or issuer, and has no intention of either contacting the owner of the card or making repayments for the purchases made.",
    "What are the three ways in which credit card frauds are committed according to the document?": "An act of criminal deception (mislead with intent) by use of unauthorized account and/or personal information. Illegal or unauthorized use of account for personal gain. Misrepresentation of account information to obtain goods and/or services.",
    "What is the purpose of the Card Verification Method (CVM)?": "The purpose of CVM is to ensure that the person submitting the transaction is in possession of the actual card, since the code cannot be copied from receipts or skimmed from magnetic stripe.",
    "What are the traits of frauds initiated by a card number generator?": "The traits of frauds initiated by a card number generator are the following: Multiple transactions with similar card numbers (e.g. same Bank Identification Number (BIN)), A large number of declines.",
    "How does the document describe an efficient fraud management solution?": "An efficient fraud management solution is one that minimizes the total cost of fraud, which includes the financial loss due to fraud as well as the cost of fraud prevention systems.",
}