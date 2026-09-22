#!/usr/bin/env python3
"""Create a serverless Vertex AI RAG Engine corpus and import pg49513.txt."""

import os
from vertexai.preview import rag
from vertexai.preview.rag.utils import resources as rr
import vertexai

PROJECT_ID = "qwiklabs-gcp-04-58a029e5210a"
LOCATION = "us-central1"  # Serverless RAG is us-central1 only
GCS_PATH = "gs://swingscout-charts-58a029e5210a/rag/pg49513.txt"

PARSING_PROMPT = (
    "Extract the individual useful facts, botanical descriptions, and herbal medicinal remedies described in this text. "
    "Ignore and omit all Gutenberg metadata, license boilerplate, and tables of contents. "
    "Output clean, self-contained prose."
)


def main():
    print(f"Initializing Vertex AI for project {PROJECT_ID} in {LOCATION}...")
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    # 1. Switch the region's RAG managed DB to serverless mode (project-level, once).
    cfg = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragEngineConfig"
    print(f"Updating RAG Engine Config to Serverless mode: {cfg}")
    rag.update_rag_engine_config(
        rag_engine_config=rag.RagEngineConfig(
            name=cfg,
            rag_managed_db_config=rag.RagManagedDbConfig(mode=rr.Serverless()),
        )
    )
    print("RAG Engine Config successfully updated to Serverless mode.")

    # 2. Create the corpus with text-embedding-005
    print("Creating RAG corpus...")
    corpus = rag.create_corpus(
        display_name="herbal-literature-corpus",
        embedding_model_config=rag.EmbeddingModelConfig(
            publisher_model="publishers/google/models/text-embedding-005"
        ),
    )
    print(f"Created corpus: {corpus.name}")

    # 3. Import + parse + chunk + embed
    print(f"Importing and indexing {GCS_PATH}...")
    resp = rag.import_files(
        corpus_name=corpus.name,
        paths=[GCS_PATH],
        transformation_config=rag.TransformationConfig(
            chunking_config=rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
        ),
        llm_parser=rag.LlmParserConfig(
            model_name="gemini-3.6-flash",
            custom_parsing_prompt=PARSING_PROMPT,
        ),
    )
    print(f"Import response: imported {resp.imported_rag_files_count} file(s).")
    print(f"\nSUCCESS: Corpus is ready! Corpus Name: {corpus.name}")
    return corpus.name


if __name__ == "__main__":
    main()
