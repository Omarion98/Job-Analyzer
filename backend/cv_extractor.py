import os
from io import BytesIO

from pypdf import PdfReader
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential


def extract_with_pypdf(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


def extract_with_azure(pdf_bytes: bytes) -> str:
    endpoint = os.environ["DOCUMENT_INTELLIGENCE_ENDPOINT"]

    client = DocumentIntelligenceClient(
        endpoint=endpoint,
        credential=DefaultAzureCredential(),
    )

    poller = client.begin_analyze_document(
        "prebuilt-read",
        body=BytesIO(pdf_bytes),
    )

    result = poller.result()

    return result.content or ""


def extract_cv_text(pdf_bytes: bytes) -> str:
    provider = os.getenv("CV_EXTRACTOR", "pypdf").lower()

    if provider == "pypdf":
        return extract_with_pypdf(pdf_bytes)

    if provider == "azure":
        print("AZURE as extractor")
        return extract_with_azure(pdf_bytes)

    raise ValueError(
        f"Unsupported CV_EXTRACTOR provider: {provider}"
    )