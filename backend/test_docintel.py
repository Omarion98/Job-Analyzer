import os
import sys

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential


endpoint = os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"]

client = DocumentIntelligenceClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

pdf_path = sys.argv[1]

with open(pdf_path, "rb") as pdf_file:
    poller = client.begin_analyze_document(
        "prebuilt-read",
        body=pdf_file,
    )

result = poller.result()

print("\n--- EXTRACTED TEXT ---\n")
print(result.content)