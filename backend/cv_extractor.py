import os
from io import BytesIO

from pypdf import PdfReader
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential

from telemetry import get_tracer


tracer = get_tracer("cv_extractor")


def extract_with_pypdf(pdf_bytes: bytes) -> str:
    with tracer.start_as_current_span(
        "cv.extract.pypdf"
    ) as span:
        span.set_attribute(
            "cv.input_bytes",
            len(pdf_bytes),
        )

        reader = PdfReader(BytesIO(pdf_bytes))

        pages = []

        for page in reader.pages:
            text = page.extract_text()

            if text:
                pages.append(text)

        extracted_text = "\n".join(pages)

        span.set_attribute(
            "cv.page_count",
            len(reader.pages),
        )
        span.set_attribute(
            "cv.extracted_characters",
            len(extracted_text),
        )

        return extracted_text


def extract_with_azure(pdf_bytes: bytes) -> str:
    endpoint = os.environ[
        "DOCUMENT_INTELLIGENCE_ENDPOINT"
    ]

    with tracer.start_as_current_span(
        "cv.extract.azure_document_intelligence"
    ) as span:
        span.set_attribute(
            "cv.input_bytes",
            len(pdf_bytes),
        )
        span.set_attribute(
            "azure.document_intelligence.model",
            "prebuilt-read",
        )

        client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=DefaultAzureCredential(),
        )

        poller = client.begin_analyze_document(
            "prebuilt-read",
            body=BytesIO(pdf_bytes),
        )

        result = poller.result()
        extracted_text = result.content or ""

        span.set_attribute(
            "cv.extracted_characters",
            len(extracted_text),
        )

        return extracted_text


def extract_cv_text(pdf_bytes: bytes) -> str:
    provider = os.getenv(
        "CV_EXTRACTOR",
        "pypdf",
    ).lower()

    with tracer.start_as_current_span(
        "cv.extract"
    ) as span:
        span.set_attribute(
            "cv.extractor",
            provider,
        )

        if provider == "pypdf":
            return extract_with_pypdf(
                pdf_bytes
            )

        if provider == "azure":
            return extract_with_azure(
                pdf_bytes
            )

        raise ValueError(
            f"Unsupported CV_EXTRACTOR provider: "
            f"{provider}"
        )
