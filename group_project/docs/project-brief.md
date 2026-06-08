# Project Brief

## Goal

Build a small RAG chatbot or evaluation demo for Vietnamese drug law and related news.

The chatbot should answer questions using retrieved evidence and cite sources. The group project should be simple enough to demo locally.

## Main User Flow

1. User asks a question about drug law or related news.
2. App retrieves relevant context.
3. Qwen generates an answer using only retrieved context.
4. App displays the answer and source documents.
5. User can ask follow-up questions.

## Knowledge Sources

For PageIndex, upload only the PDF files accepted by the tool:

- `data/landing/legal/luat-phong-chong-ma-tuy-2021.pdf`
- `data/landing/legal/nghi-dinh-105-2021-huong-dan-luat-phong-chong-ma-tuy.pdf`
- `data/landing/legal/nghi-dinh-57-2022-danh-muc-chat-ma-tuy-va-tien-chat.pdf`

The existing markdown/news/vector-store pipeline can still be used locally, but the PageIndex part should focus on these PDFs.

## Must-Have Features

- Ask a question.
- Retrieve context from PageIndex or the existing local retrieval pipeline.
- Generate an answer with Qwen.
- Include citation format `[Source, Year]`.
- Show source documents/chunks used.
- Return `I cannot verify this information` when evidence is insufficient.

## Nice-To-Have Features

- Conversation memory for follow-up questions.
- Evaluation pipeline with at least 15 golden Q&A pairs.
- A/B comparison such as hybrid retrieval vs PageIndex-only retrieval.

## Demo Scope

Keep the demo small:

- One app file is acceptable.
- One retrieval wrapper is acceptable.
- One generation wrapper is acceptable.
- One evaluation script is acceptable.

