# Project Brief

## Mục tiêu

Xây dựng một chatbot RAG nhỏ hoặc demo đánh giá cho luật phòng, chống ma túy Việt Nam và các tin tức liên quan.

Chatbot cần trả lời câu hỏi dựa trên bằng chứng được retrieve và trích dẫn nguồn. Group project nên đủ đơn giản để demo local.

## Luồng người dùng chính

1. User đặt câu hỏi về luật ma túy hoặc tin tức liên quan.
2. App retrieve context liên quan.
3. Qwen tạo câu trả lời chỉ dựa trên context đã retrieve.
4. App hiển thị câu trả lời và tài liệu nguồn.
5. User có thể hỏi tiếp các câu follow-up.

## Nguồn tri thức

Với PageIndex, chỉ upload các file PDF được tool hỗ trợ:

- `data/landing/legal/luat-phong-chong-ma-tuy-2021.pdf`
- `data/landing/legal/nghi-dinh-105-2021-huong-dan-luat-phong-chong-ma-tuy.pdf`
- `data/landing/legal/nghi-dinh-57-2022-danh-muc-chat-ma-tuy-va-tien-chat.pdf`

Pipeline markdown/news/vector-store hiện có vẫn có thể dùng local, nhưng phần PageIndex nên tập trung vào các PDF này.

## Tính năng bắt buộc

- Đặt câu hỏi.
- Retrieve context từ PageIndex hoặc pipeline local retrieval hiện có.
- Generate câu trả lời bằng Qwen.
- Có citation theo format `[Source, Year]`.
- Hiển thị source documents/chunks đã dùng.
- Trả `I cannot verify this information` khi bằng chứng không đủ.

## Tính năng nên có

- Conversation memory cho câu hỏi follow-up.
- Evaluation pipeline với ít nhất 15 cặp Q&A chuẩn.
- So sánh A/B, ví dụ hybrid retrieval vs PageIndex-only retrieval.

## Phạm vi demo

Giữ demo nhỏ gọn:

- Một file app là chấp nhận được.
- Một retrieval wrapper là chấp nhận được.
- Một generation wrapper là chấp nhận được.
- Một evaluation script là chấp nhận được.