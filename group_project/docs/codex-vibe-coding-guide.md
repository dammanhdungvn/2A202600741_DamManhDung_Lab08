# Codex Vibe Coding Guide

## Má»¥c tiÃªu

File nÃ y hÆ°á»›ng dáº«n cÃ¡ch dÃ¹ng Codex Ä‘á»ƒ vibe coding hiá»‡u quáº£ cho group project RAG chatbot/evaluation.

Codex sáº½ lÃ m tá»‘t hÆ¡n náº¿u báº¡n luÃ´n Ä‘Æ°a Ä‘Ãºng ngá»¯ cáº£nh:

- `AGENTS.md`
- docs trong `group_project/docs/`
- file code cá»¥ thá»ƒ Ä‘ang muá»‘n sá»­a
- yÃªu cáº§u nhá», rÃµ, cÃ³ tiÃªu chÃ­ kiá»ƒm tra

## Hiá»ƒu nhanh `/` vÃ  `@`

Trong Codex/AI coding tools, thÆ°á»ng cÃ³ hai kiá»ƒu thao tÃ¡c hay gáº·p:

### `/`

`/` thÆ°á»ng lÃ  command hoáº·c workflow shortcut.

VÃ­ dá»¥ cÃ³ thá»ƒ gáº·p:

```text
/plan
/review
/fix
/test
```

TÃ¹y app/tool mÃ  command cÃ³ sáºµn khÃ¡c nhau. Náº¿u khÃ´ng cháº¯c command cÃ³ tá»“n táº¡i khÃ´ng, cá»© viáº¿t báº±ng cÃ¢u thÆ°á»ng cÅ©ng Ä‘Æ°á»£c.

VÃ­ dá»¥ thay vÃ¬:

```text
/plan build rag chatbot
```

báº¡n cÃ³ thá»ƒ viáº¿t:

```text
HÃ£y láº­p káº¿ hoáº¡ch build RAG chatbot theo AGENTS.md vÃ  docs trong group_project/docs. ChÆ°a code vá»™i.
```

### `@`

`@` thÆ°á»ng dÃ¹ng Ä‘á»ƒ tag file/folder/context cho AI Ä‘á»c.

VÃ­ dá»¥:

```text
@AGENTS.md
@group_project/docs/project-brief.md
@group_project/docs/page-index.md
@group_project/src/pageindex_client.py
```

Khi tag file, báº¡n Ä‘ang nÃ³i vá»›i Codex: "HÃ£y Ä‘á»c file nÃ y lÃ m ngá»¯ cáº£nh chÃ­nh".

Náº¿u UI khÃ´ng há»— trá»£ tag `@`, báº¡n váº«n cÃ³ thá»ƒ viáº¿t Ä‘Æ°á»ng dáº«n bÃ¬nh thÆ°á»ng:

```text
HÃ£y Ä‘á»c AGENTS.md vÃ  group_project/docs/page-index.md trÆ°á»›c.
```

## Quy trÃ¬nh vibe coding khuyáº¿n nghá»‹

### BÆ°á»›c 1: LuÃ´n báº¯t Codex Ä‘á»c context trÆ°á»›c

Prompt máº«u:

```text
Báº¡n lÃ  senior AI Engineer. TrÆ°á»›c khi code, hÃ£y Ä‘á»c:
@AGENTS.md
@group_project/docs/project-brief.md
@group_project/docs/page-index.md
@group_project/docs/qwen-api.md
@group_project/docs/page-index.md
@group_project/docs/qwen-api.md

Sau Ä‘Ã³ tÃ³m táº¯t ngáº¯n báº¡n hiá»ƒu task nÃ y tháº¿ nÃ o. ChÆ°a sá»­a file.
```

Má»¥c tiÃªu: trÃ¡nh Codex Ä‘oÃ¡n sai.

### BÆ°á»›c 2: YÃªu cáº§u plan nhá»

Prompt máº«u:

```text
Dá»±a trÃªn docs Ä‘Ã£ Ä‘á»c, hÃ£y láº­p plan build PageIndex client cho group project.
YÃªu cáº§u:
- chá»‰ upload 3 PDF legal Ä‘Ã£ ghi trong docs
- Ä‘á»c PAGEINDEX_API_KEY tá»« .env
- lÆ°u doc_id vÃ o manifest
- chÆ°a code vá»™i
```

Má»¥c tiÃªu: kiá»ƒm tra hÆ°á»›ng Ä‘i trÆ°á»›c khi cho code.

### BÆ°á»›c 3: Cho code tá»«ng pháº§n nhá»

Prompt máº«u:

```text
Äá»c @group_project/docs/page-index.md trÆ°á»›c.
Thá»±c hiá»‡n bÆ°á»›c 1 trong plan: viáº¿t file group_project/src/pageindex_client.py.

YÃªu cáº§u:
- Ä‘á»c .env tá»« root
- dÃ¹ng PageIndexClient
- upload 3 PDF trong docs
- lÆ°u manifest vÃ o group_project/pageindex_manifest.json
- khÃ´ng hard-code API key
- sau khi code xong cháº¡y smoke test phÃ¹ há»£p
```

KhÃ´ng nÃªn nÃ³i:

```text
Build full app luÃ´n.
```

VÃ¬ task quÃ¡ rá»™ng, Codex dá»… lÃ m lan man.

### BÆ°á»›c 4: Sau má»—i láº§n code, báº¯t Codex verify

Prompt máº«u:

```text
HÃ£y cháº¡y smoke test cho file vá»«a viáº¿t.
Náº¿u test lá»—i, sá»­a lá»—i. KhÃ´ng sá»­a file khÃ´ng liÃªn quan.
```

Hoáº·c:

```text
Kiá»ƒm tra git diff vÃ  giáº£i thÃ­ch file nÃ o Ä‘Ã£ thay Ä‘á»•i.
```

### BÆ°á»›c 5: Build Qwen client

Prompt máº«u:

```text
Äá»c:
@group_project/docs/qwen-api.md
@group_project/docs/qwen-api.md

Viáº¿t group_project/src/qwen_client.py.
YÃªu cáº§u:
- dÃ¹ng OpenAI SDK compatible
- api_key tá»« QWEN_API_KEY
- base_url tá»« QWEN_BASE_URL
- model tá»« QWEN_MODEL_NAME
- function generate_answer(question, contexts)
- náº¿u thiáº¿u evidence thÃ¬ tráº£ "I cannot verify this information"
- khÃ´ng hard-code secret
```

### BÆ°á»›c 6: Build RAG pipeline

Prompt máº«u:

```text
Viáº¿t group_project/src/rag_pipeline.py.

YÃªu cáº§u:
- nháº­n question
- gá»i pageindex_client Ä‘á»ƒ retrieve context
- gá»i qwen_client Ä‘á»ƒ generate answer
- return dict gá»“m answer vÃ  sources
- citation format [Source, Year]
- code Ä‘Æ¡n giáº£n Ä‘á»ƒ demo
```

### BÆ°á»›c 7: Build UI

Prompt máº«u:

```text
Viáº¿t group_project/app.py báº±ng Streamlit.

YÃªu cáº§u:
- Ã´ chat nháº­p cÃ¢u há»i
- gá»i rag_pipeline
- hiá»ƒn thá»‹ answer
- hiá»ƒn thá»‹ sources bÃªn dÆ°á»›i
- cÃ³ session_state lÆ°u history Ä‘Æ¡n giáº£n
- khÃ´ng lÃ m UI phá»©c táº¡p
```

### BÆ°á»›c 8: Build evaluation

Prompt máº«u:

```text
Äá»c group_project/README.md pháº§n Evaluation.

Táº¡o:
- group_project/evaluation/golden_dataset.json vá»›i 15 Q&A
- group_project/evaluation/eval_pipeline.py
- group_project/evaluation/results.md template

Chá»n DeepEval náº¿u dá»… nháº¥t. Náº¿u cáº§n API model thÃ¬ dÃ¹ng Qwen config tá»« .env.
```

## Prompt máº«u dÃ¹ng háº±ng ngÃ y

### Khi muá»‘n lÃ m PageIndex

```text
Äá»c:
@group_project/docs/page-index.md
@group_project/docs/page-index.md

Sau Ä‘Ã³ viáº¿t hoáº·c sá»­a PageIndex client. Chá»‰ upload 3 PDF legal Ä‘Ã£ ghi trong docs.
```

### Khi muá»‘n lÃ m Qwen

```text
Äá»c:
@group_project/docs/qwen-api.md
@group_project/docs/qwen-api.md

Sau Ä‘Ã³ viáº¿t hoáº·c sá»­a Qwen client. KhÃ´ng hard-code API key, base URL, model name.
```

### Khi muá»‘n lÃ m Weaviate optional

```text
Äá»c @group_project/docs/weaviate.md.
Chá»‰ viáº¿t script test connect Weaviate. KhÃ´ng tÃ­ch há»£p vÃ o chatbot vá»™i.
```

### Khi muá»‘n Codex Ä‘á»c vÃ  chÆ°a code

```text
HÃ£y Ä‘á»c cÃ¡c file sau vÃ  tÃ³m táº¯t ngá»¯ cáº£nh. KhÃ´ng sá»­a file:
@AGENTS.md
@group_project/docs/codex-vibe-coding-guide.md
```

### Khi muá»‘n Codex sá»­a Ä‘Ãºng má»™t file

```text
Chá»‰ sá»­a file @group_project/src/qwen_client.py.
KhÃ´ng sá»­a file khÃ¡c.
Sau khi sá»­a, cháº¡y smoke test.
```

### Khi muá»‘n Codex debug

```text
Lá»—i khi cháº¡y command nÃ y:
<paste lá»—i>

HÃ£y Ä‘á»c file liÃªn quan, tÃ¬m nguyÃªn nhÃ¢n, sá»­a tá»‘i thiá»ƒu vÃ  cháº¡y láº¡i command.
```

### Khi muá»‘n Codex review

```text
Review code trong @group_project/src/rag_pipeline.py.
Táº­p trung bug, thiáº¿u citation, thiáº¿u error handling, vÃ  chá»— hard-code secret.
ChÆ°a sá»­a file.
```

### Khi muá»‘n Codex ná»‘i nhiá»u file

```text
Äá»c:
@group_project/src/pageindex_client.py
@group_project/src/qwen_client.py

Viáº¿t @group_project/src/rag_pipeline.py Ä‘á»ƒ ná»‘i 2 module nÃ y.
```

## Checklist trÆ°á»›c khi báº£o Codex code

TrÆ°á»›c má»—i task, hÃ£y nÃ³i rÃµ:

- File nÃ o cáº§n Ä‘á»c.
- File nÃ o Ä‘Æ°á»£c phÃ©p sá»­a.
- Output mong muá»‘n.
- Command test/smoke test cáº§n cháº¡y.
- Äiá»u gÃ¬ khÃ´ng Ä‘Æ°á»£c lÃ m.

VÃ­ dá»¥ tá»‘t:

```text
Äá»c AGENTS.md vÃ  group_project/docs/page-index.md.
Chá»‰ sá»­a group_project/src/pageindex_client.py.
Viáº¿t function upload_documents() vÃ  save_manifest().
KhÃ´ng hard-code API key.
Sau khi code xong cháº¡y: python group_project/src/pageindex_client.py
```

## CÃ¡c lá»—i thÆ°á»ng gáº·p khi vibe coding

### Task quÃ¡ rá»™ng

KhÃ´ng nÃªn:

```text
Build toÃ n bá»™ chatbot.
```

NÃªn:

```text
Viáº¿t trÆ°á»›c pageindex_client.py Ä‘á»ƒ upload vÃ  lÆ°u doc_id.
```

### KhÃ´ng Ä‘Æ°a context

KhÃ´ng nÃªn:

```text
Sá»­a giÃºp tÃ´i.
```

NÃªn:

```text
Äá»c AGENTS.md vÃ  file lá»—i nÃ y trÆ°á»›c: @group_project/src/qwen_client.py
```

### KhÃ´ng nÃ³i test

KhÃ´ng nÃªn:

```text
Code xong bÃ¡o tÃ´i.
```

NÃªn:

```text
Code xong cháº¡y smoke test vÃ  bÃ¡o output quan trá»ng.
```

## Lá»™ trÃ¬nh prompt cho project nÃ y

Báº¡n cÃ³ thá»ƒ Ä‘i theo chuá»—i prompt sau:

1. Äá»c context:

```text
Äá»c AGENTS.md vÃ  toÃ n bá»™ docs trong group_project/docs. TÃ³m táº¯t project. ChÆ°a code.
```

2. PageIndex:

```text
Viết group_project/src/pageindex_client.py theo page-index.md.
```

3. Qwen:

```text
Viết group_project/src/qwen_client.py theo qwen-api.md.
```

4. Pipeline:

```text
Viáº¿t group_project/src/rag_pipeline.py ná»‘i PageIndex retrieval vÃ  Qwen generation.
```

5. UI:

```text
Viáº¿t group_project/app.py báº±ng Streamlit Ä‘á»ƒ demo chatbot.
```

6. Evaluation:

```text
Viáº¿t evaluation theo group_project/README.md, Æ°u tiÃªn Ä‘Æ¡n giáº£n cháº¡y Ä‘Æ°á»£c.
```

## NguyÃªn táº¯c vÃ ng

Codex lÃ m tá»‘t nháº¥t khi báº¡n giao viá»‡c nhÆ° giao cho má»™t junior engineer thÃ´ng minh:

- Ä‘Æ°a context
- giá»›i háº¡n pháº¡m vi
- nÃ³i rÃµ output
- báº¯t verify
- khÃ´ng yÃªu cáº§u quÃ¡ nhiá»u thá»© má»™t láº§n
