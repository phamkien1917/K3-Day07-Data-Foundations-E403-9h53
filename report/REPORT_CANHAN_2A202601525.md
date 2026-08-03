# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Phạm Trung Kiên
**Nhóm:** 9h53
**Ngày:** 03/08/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> *Viết 1-2 câu:* Độ tương tự cosine cao (gần bằng 1) nghĩa là hai vector đại diện cho hai văn bản có hướng rất giống nhau trong không gian vector đa chiều, cho thấy chúng có sự tương đồng lớn về ngữ nghĩa và chủ đề.

**Ví dụ có độ tương tự CAO:**
- Câu A: Con mèo đang ngủ trên chiếc ghế dài.
- Câu B: Chú mèo đang nằm nghỉ trên ghế sofa.
- Tại sao tương đồng: Cả hai câu miêu tả cùng một sự việc, dùng các từ đồng nghĩa (con mèo - chú mèo, ngủ - nằm nghỉ, ghế dài - ghế sofa), nên vector nhúng của chúng sẽ rất giống nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Con mèo đang ngủ trên chiếc ghế dài.
- Câu B: Lãi suất ngân hàng tiếp tục tăng trong tháng này.
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác biệt (động vật/sinh hoạt và tài chính), không có từ vựng hay ngữ nghĩa chung.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> *Viết 1-2 câu:* Độ tương tự cosine đo lường góc giữa hai vector nên không bị ảnh hưởng bởi độ lớn (độ dài) của vector. Điều này phù hợp với văn bản vì hai đoạn văn cùng chủ đề nhưng có độ dài khác nhau vẫn sẽ có độ tương đồng cosine cao, trong khi khoảng cách Euclid giữa chúng có thể rất lớn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Công thức: làm_tròn_lên((10000 - 50) / (500 - 50)) = làm_tròn_lên(9950 / 450) = làm_tròn_lên(22.11)
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> *Viết 1-2 câu:* Số lượng chunk sẽ tăng lên: làm_tròn_lên((10000 - 100)/(500 - 100)) = làm_tròn_lên(9900/400) = 25 chunks. Việc tăng độ chồng chéo (overlap) giúp bảo toàn tốt hơn ngữ cảnh ở ranh giới giữa các chunk, tránh việc một câu hay một ý quan trọng bị cắt đứt làm đôi.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> *Viết 2-3 câu: dùng biểu thức chính quy (regex) gì để phát hiện câu? Xử lý trường hợp ngoại lệ (edge case) nào?*
Sử dụng thư viện `re` với pattern `(?<=[.!?])\s+|(?<=\.)\n` để tách câu ngay sau dấu câu (chấm, chấm than, hỏi chấm) kết hợp khoảng trắng hoặc xuống dòng. Xử lý ngoại lệ chuỗi rỗng bằng cách trả về mảng rỗng nếu đầu vào trống để tránh tạo ra chunk lỗi.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> *Viết 2-3 câu: thuật toán hoạt động thế nào? Base case (trường hợp cơ sở) là gì?*
Thuật toán đệ quy nhận đầu vào là đoạn text và danh sách separators. Trường hợp cơ sở (base case) là khi đoạn text ngắn hơn hoặc bằng `chunk_size` hoặc hết separator thì trả về list chứa duy nhất text đó. Nếu đoạn quá dài, chia nhỏ bằng separator đầu tiên, duyệt qua các đoạn con, cộng dồn vào chunk hiện tại đến khi vừa đủ kích thước thì tạo chunk mới; đoạn con nào vẫn quá to thì gọi lại đệ quy.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> *Viết 2-3 câu: lưu trữ thế nào? Tính độ tương tự ra sao?*
`add_documents` chạy hàm nhúng sinh vector và lưu dictionary thông tin vào list `_store` trong bộ nhớ (hoặc ChromaDB nếu cài đặt). Hàm `search` nhúng câu hỏi truy vấn, tính cosine similarity (tích vô hướng) giữa vector truy vấn và tất cả các vector của chunks trong store, sau đó sắp xếp giảm dần để trả về top-K.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> *Viết 2-3 câu: lọc (filter) trước hay sau? Xóa bằng cách nào?*
`search_with_filter` tiến hành lọc các chunk có metadata khớp với yêu cầu TRƯỚC (để giảm không gian tìm kiếm), rồi mới chạy similarity search trên tập đã lọc. `delete_document` thực hiện xóa bằng cách dùng List Comprehension lọc bỏ những record có `id` hoặc `doc_id` trong metadata trùng với ID cần xóa, đồng thời xóa trong Chroma (nếu có).

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> *Viết 2-3 câu: cấu trúc prompt? Cách đưa ngữ cảnh (inject context) vào thế nào?*
Agent gọi hàm `search` của store để lấy ra top-K chunks liên quan nhất. Nối nội dung các chunks này bằng khoảng trắng/xuống dòng để tạo thành chuỗi Context, sau đó inject vào prompt theo cấu trúc: "Context: {context} \n\n Question: {question} \n\n Answer:" và đưa vào LLM để sinh câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.1.1, pluggy-1.6.0 -- C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe
cachedir: .pytest_cache
rootdir: C:\AI\K3-Day07-Data-Foundations
plugins: anyio-4.13.0
collecting ... collected 42 items

... [42 passed tests details omitted for brevity] ...

============================= 42 passed in 0.06s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Con mèo ngủ trên ghế | Chú mèo nằm trên sofa | cao | 0.0772 (Mock) | Sai |
| 2 | Thời tiết hôm nay rất đẹp | Trời hôm nay nắng ấm và trong xanh | cao | 0.1461 (Mock) | Sai |
| 3 | Con mèo ngủ trên ghế | Giá vàng hôm nay tăng mạnh | thấp | 0.1139 (Mock) | Đúng |
| 4 | Học máy là một lĩnh vực của AI | Machine learning thuộc trí tuệ nhân tạo | cao | 0.2056 (Mock) | Đúng |
| 5 | Tôi thích ăn phở | Xe ô tô chạy bằng xăng | thấp | 0.0506 (Mock) | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:* Điểm số sử dụng `_mock_embed` (như bài lab yêu cầu ở giai đoạn 1) gần như ngẫu nhiên và rất thấp ngay cả khi hai câu đồng nghĩa (ví dụ Cặp 1 chỉ đạt 0.0772, thấp hơn cả cặp 3 hoàn toàn không liên quan). Điều này cho thấy mock embedder chỉ băm chuỗi ra vector cơ học và không hiểu nghĩa; để embeddings thực sự biểu diễn được ngữ nghĩa, ta bắt buộc phải dùng các mô hình nhúng (như sentence-transformers hoặc OpenAI) đã được huấn luyện trên dữ liệu lớn.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
