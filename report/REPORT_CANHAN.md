# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** [Tên sinh viên]
**Nhóm:** [Tên nhóm]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao (tiệm cận 1.0) nghĩa là hai véc-tơ biểu diễn văn bản hướng về cùng một chiều trong không gian nhúng ngữ nghĩa (embedding space). Điều này thể hiện hai đoạn văn bản có nội dung, ý nghĩa hoặc ngữ cảnh rất tương đồng với nhau, bất kể độ dài ngắn của câu.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Hạn đăng ký môn học cho học kỳ hè là ngày nào?"
- Câu B: "Cho mình hỏi thời gian cuối cùng để hoàn tất đăng ký các lớp học hè?"
- Tại sao tương đồng: Cả hai câu đều dùng các từ ngữ đồng nghĩa và có cùng ý định truy vấn (intent) về mốc thời gian hạn chót đăng ký môn học hè.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Quy trình xin xét duyệt học bổng khuyến khích học tập."
- Câu B: "Thực đơn các món ăn tại nhà ăn sinh viên hôm nay."
- Tại sao khác: Hai câu thuộc về hai chủ đề hoàn toàn độc lập và không liên quan đến nhau (một bên là chính sách học thuật/học bổng, một bên là đời sống sinh hoạt/ẩm thực).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Khoảng cách Euclid bị ảnh hưởng bởi độ lớn (magnitude/độ dài) của véc-tơ, dễ khiến văn bản dài và văn bản ngắn có khoảng cách lớn dù cùng nội dung. Trái lại, Cosine Similarity chỉ đo góc giữa hai véc-tơ (hướng của ý nghĩa), loại bỏ hoàn toàn yếu tố độ dài văn bản, giúp so sánh ngữ nghĩa chính xác hơn giữa các câu/đoạn có độ dài ngắn khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính:  
> Bước nhảy giữa các chunk: `step = chunk_size - overlap = 500 - 50 = 450` ký tự.  
> Công thức tính số chunk: `ceil((độ_dài - overlap) / step) = ceil((10000 - 50) / 450) = ceil(9950 / 450) = ceil(22.111...) = 23`.  
> Đáp án: **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100: Bước nhảy `step = 500 - 100 = 400`. Số chunk = `ceil((10000 - 100) / 400) = ceil(9900 / 400) = ceil(24.75) = 25` chunks (tăng thêm 2 chunks).  
> Lý do muốn độ chồng chéo nhiều hơn: Tăng overlap giúp giữ lại liên kết ngữ cảnh ở ranh giới cắt giữa hai chunk kề nhau, tránh việc các câu hoặc ý nghĩa quan trọng bị xẻ đôi làm mất thông tin khi truy xuất (retrieval).

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng biểu thức chính quy `re.split(r'(?<=[.!?])\s+|\n+', text.strip())` để phân tách câu tại các mốc dấu chấm, chấm hỏi, chấm cảm hoặc xuống dòng. Xử lý ngoại lệ chuỗi rỗng/chỉ chứa khoảng trắng bằng cách trả về danh sách rỗng, đồng thời gộp tối đa `max_sentences_per_chunk` câu liên tiếp vào một chunk và loại bỏ khoảng trắng thừa.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Áp dụng thuật toán chia để trị đệ quy với thứ tự phân cách ưu tiên `["\n\n", "\n", ". ", " ", ""]`. Trường hợp cơ sở (base case) xảy ra khi độ dài chuỗi nhỏ hơn hoặc bằng `chunk_size` hoặc khi đã duyệt hết danh sách dấu phân cách (lúc này sẽ cắt thành các lát cố định). Sau khi phân tách đệ quy, tiến hành gộp lại các đoạn nhỏ kề nhau nếu tổng độ dài vẫn nằm trong giới hạn `chunk_size`.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Trong `add_documents`, từng document được tính véc-tơ nhúng qua `self._embedding_fn` và đóng gói thành dictionary lưu vào bộ nhớ danh sách `self._store` (và ChromaDB nếu có). Đối với `search`, véc-tơ của truy vấn được nhân tích vô hướng (dot product) với từng véc-tơ lưu trữ, sau đó sắp xếp giảm dần theo điểm số để chọn ra `top_k` kết quả có độ tương đồng cao nhất.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` áp dụng cơ chế lọc trước (pre-filtering): duyệt các record trong `self._store` và chỉ giữ lại những record có `metadata` khớp toàn bộ với `metadata_filter`, rồi mới tính độ tương đồng trên tập đã lọc. Với `delete_document`, tiến hành loại bỏ tất cả các record có `id` hoặc `metadata['doc_id']` trùng với `doc_id` truyền vào, trả về `True` nếu có phần tử bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Gọi `store.search(question, top_k)` để truy xuất các chunk liên quan nhất, gộp nội dung của chúng thành một khối văn bản ngữ cảnh (Context). Đưa ngữ cảnh và câu hỏi vào mẫu Prompt chuẩn RAG (hướng dẫn LLM chỉ trả lời dựa trên ngữ cảnh cung cấp), cuối cùng chuyển Prompt cho `self.llm_fn` để sinh ra câu trả lời.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
============================= test session starts =============================
platform win32 -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\Nitro Tiger\OneDrive\Dokumen\VInUni_AI\Lab\Lab-07\K3-Day07-Data-Foundations
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.06s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42


---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Hạn đăng ký môn học kỳ Hè là ngày nào? | Cho mình hỏi thời hạn đăng ký các môn học hè? | cao | -0.0177 | Sai (với Mock) |
| 2 | Quy định xin xét duyệt học bổng khuyến khích học tập. | Các tiêu chí để đạt học bổng học tập xuất sắc. | cao | -0.0846 | Sai (với Mock) |
| 3 | Lịch thi học kỳ 2 năm học 2025-2026. | Thời gian tổ chức các buổi thi cuối kỳ 2. | cao | 0.0727 | Đúng |
| 4 | Quy định về việc sử dụng phòng máy tính thư viện. | Cách thức đặt món ăn tại nhà ăn sinh viên. | thấp | -0.0035 | Đúng |
| 5 | Hướng dẫn đăng ký ký túc xá cho tân sinh viên. | Cách thức nộp hồ sơ xin việc tại các công ty CNTT. | thấp | -0.0058 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Kết quả bất ngờ nhất là các cặp câu 1 và 2 dù có ngữ nghĩa rất tương đồng nhưng điểm cosine similarity với `MockEmbedder` lại ra kết quả âm (gần bằng 0). Điều này cho thấy `MockEmbedder` chỉ tạo véc-tơ xác định dựa trên hàm băm (hash) ký tự phục vụ unit test chứ không học được ngữ nghĩa. Muốn phản ánh đúng quan hệ ngữ nghĩa thực sự giữa các câu trong không gian nhúng, ta bắt buộc phải sử dụng các mô hình embedding chuyên dụng (như `SentenceTransformers` hoặc `OpenAIEmbedder`).


---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What is the maximum extended time allowed for tests and examinations under academic accommodation? | ...extended testing time for tests and examinations under academic accommodation... | 0.3159 | Yes | Up to 25% of the total allotted time. |
| 2 | Can a student request a change in their assigned advisor? | ...students may request a change in their assigned academic advisor under justifiable circumstances... | 0.3855 | Yes | Yes, under justifiable circumstances such as conflict of interest, incompatibility, or change in personal needs. |
| 3 | Is it allowed to smoke or drink alcohol within university premises? | ...strictly prohibited to smoke or consume alcohol within university premises or attend class... | 0.4386 | Yes | No, it is prohibited to smoke, drink alcohol within university premises, or attend class under the influence of alcohol. |
| 4 | How many students does each Peer Advisor support? | ...Peer Advisors support first-year students, each supporting 10–20 students... | 0.2984 | Yes | Each Peer Advisor supports 10–20 first-year students. |
| 5 | What type of disciplinary action is applied for a first-time violation of a minor nature? | ...for a first-time violation of a minor nature, the disciplinary action applied is Expression of Disapproval... | 0.3172 | Yes | Expression of Disapproval. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Qua việc so sánh kết quả trong nhóm, tôi nhận thấy chiến lược `RecursiveChunker` kết hợp với phân đoạn theo cấu trúc điều khoản (section/heading) giữ trọn vẹn ngữ cảnh tốt hơn hẳn so với `FixedSizeChunker` (vốn hay bị cắt ngang câu) và `SentenceChunker` (vốn bị xẻ lẻ câu ngắn làm mất ngữ cảnh tổng thể).

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |



