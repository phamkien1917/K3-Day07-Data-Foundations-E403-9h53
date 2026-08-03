# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** 9h53
**Thành viên:** Phạm Trung Kiên - 2A202601525, Lương Ngọc Quang - 2A202601563, Vũ Minh Quang - 2A202601515
**Ngày:** 03/08/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> *Quy định và Chính sách Sinh viên: Tư vấn học vụ, Hướng dẫn chỗ ở, Quy tắc ứng xử, Quản lý thực tập và Xử lý khiếu nại.*

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | quy_tac_ung_xu_sinh_vien.txt | Nội bộ trường | 24/12/2025 | 20172 | doc_id, title |
| 2 | khung_tu_van_sinh_vien.txt | Nội bộ trường | 03/09/2025 | 18396 | doc_id, title |
| 3 | huong_dan_cho_o_cho_sinh_vien.txt | Nội bộ trường | 22/07/2026 | 14915 | doc_id, title |
| 4 | giai_quyet_khieu_nai_sinh_vien.txt | Nội bộ trường | Đang cập nhật | N/A | doc_id, title |
| 5 | quan_ly_thuc_tap_sinh.txt | Nội bộ trường | Đang cập nhật | N/A | doc_id, title |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | Chuỗi | `quy_tac_ung_xu_sinh_vien` | Giúp phân biệt rõ ràng các quy định khác nhau, phục vụ cho việc lọc (filter). |
| `title` | Chuỗi | `Quy tắc ứng xử sinh viên` | Trực quan hóa nguồn tài liệu để biết thông tin được trích xuất từ văn bản quy định nào. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| quy_tac_ung_xu | FixedSizeChunker (`fixed_size`) | 42 | 500 ký tự | Thường cắt ngang câu. |
| quy_tac_ung_xu | SentenceChunker (`by_sentences`) | 120 | 150 ký tự | Khá chi tiết nhưng dễ mất ngữ cảnh đoạn. |
| quy_tac_ung_xu | RecursiveChunker (`recursive`) | 35 | 600 ký tự | Tốt nhất, giữ nguyên đoạn văn bản. |

### Chiến lược của từng thành viên

**Thành viên 1 — Phạm Trung Kiên**
- **Loại chiến lược:** FixedSizeChunker (Mặc định)
- **Mô tả & lý do chọn cho chủ đề này:** Dùng phương pháp chia đều số lượng từ, kích thước chunk size là 500 ký tự, độ trượt 50 ký tự. Nhanh và đơn giản để test baseline.

**Thành viên 2 — Lương Ngọc Quang**
- **Loại chiến lược:** SentenceChunker
- **Mô tả & lý do chọn:** Chia nhỏ văn bản dựa trên dấu chấm câu. Giúp lấy được những quy định chi tiết ngắn gọn trong Bộ Quy tắc ứng xử.

**Thành viên 3 — Vũ Minh Quang**
- **Loại chiến lược:** RecursiveChunker
- **Mô tả & lý do chọn:** Chia văn bản theo đoạn (paragraph), khi đoạn quá dài mới chia theo câu. Rất phù hợp với văn bản quy định hành chính vì giữ được nguyên vẹn một điều luật.

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Phạm Trung Kiên | FixedSizeChunker | 6/10 | Nhanh, độ dài các chunk đều nhau. | Hay cắt ngang câu hoặc cắt ngang điều luật. |
| Lương Ngọc Quang | SentenceChunker | 7/10 | Tìm chính xác quy định ngắn. | Lấy thiếu ngữ cảnh nếu điều luật dài 2-3 câu. |
| Vũ Minh Quang | RecursiveChunker | 9/10 | Giữ vẹn nguyên toàn bộ điều luật/đoạn văn. | Tốn nhiều công sức để cài đặt thuật toán đệ quy. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Chiến lược đệ quy (RecursiveChunker) của Vũ Minh Quang là tốt nhất. Bởi vì tài liệu quy định/hướng dẫn thường chia theo các đề mục và đoạn văn, việc giữ nguyên cả đoạn sẽ giúp RAG trả lời chính xác và đầy đủ các điều kiện thay vì chỉ một câu đơn lẻ.*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | What is the maximum extended time allowed for tests and examinations under academic accommodation? | Up to 25% of the total allotted time. | huong_dan_cho_o_cho_sinh_vien |
| 2 | Can a student request a change in their assigned advisor? | Yes, under justifiable circumstances such as conflict of interest, incompatibility, or change in personal needs. | khung_tu_van_sinh_vien |
| 3 | Is it allowed to smoke or drink alcohol within university premises? | No, it is prohibited to smoke, drink alcohol within university premises, or attend class under the influence of alcohol. | quy_tac_ung_xu_sinh_vien |
| 4 | How many students does each Peer Advisor support? | Each Peer Advisor supports 10–20 first-year students. | khung_tu_van_sinh_vien |
| 5 | What type of disciplinary action is applied for a first-time violation of a minor nature? | Expression of Disapproval. | quy_tac_ung_xu_sinh_vien |

### Tổng hợp chất lượng truy xuất của nhóm

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Câu 1 | RecursiveChunker | Có (Top 1) | Lấy đúng đoạn về Accommodations |
| 2 | Câu 2 | RecursiveChunker | Có (Top 1) | |
| 3 | Câu 3 | SentenceChunker | Có (Top 1) | Vì quy định rất ngắn gọn (1 câu). |
| 4 | Câu 4 | FixedSizeChunker | Có (Top 2) | Có dính rác văn bản. |
| 5 | Câu 5 | RecursiveChunker | Có (Top 1) | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Lọc metadata bằng `doc_id` rất hữu ích nếu hệ thống nhầm lẫn giữa quy định xử phạt chung và xử lý khiếu nại (ví dụ lọc chỉ lấy trong `quy_tac_ung_xu_sinh_vien`).*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. Tính ưu việt của Recursive Chunking đối với văn bản quy phạm hành chính.
> 2. Sự cần thiết của metadata `doc_id` để tránh nhầm lẫn giữa các bộ quy tắc.

**Bài học rút ra khi so sánh trong nhóm:**
> *Cùng một tài liệu nhưng FixedSize làm mất ngữ cảnh, khiến mô hình ngôn ngữ sinh câu trả lời bị sai lệch (hallucination). Recursive giữ đúng ngữ cảnh sẽ cho câu trả lời chuẩn xác nhất.*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Nhóm sẽ trích xuất thêm các metadata sâu hơn như `chapter`, `article_number` (số điều khoản) để việc truy xuất còn chính xác đến từng mục.*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
