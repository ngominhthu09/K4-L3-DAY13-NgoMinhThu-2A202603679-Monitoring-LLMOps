# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: `HighLatencyP95`
- Severity: warning
- Duration: 5m
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: P95 của `response_sent.latency_ms`, ngưỡng 2000 ms.
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 2000ms` trong 5 phút.
- Ảnh hưởng tới người dùng: phản hồi chậm dù request vẫn có thể thành công.
- Ba bước kiểm tra đầu tiên: (1) kiểm tra dashboard latency/TTFT, (2) lọc log có `latency_ms` cao và lấy `correlation_id`, (3) mở trace cùng ID để so sánh retrieval với generation.
- Mitigation tạm thời: tắt scenario gây chậm hoặc giảm tải; sau đó xác nhận P95 trở về dưới ngưỡng.
- Owner: `student-2A202603679`

## Alert 2

- Tên: `ElevatedErrorRate`
- Severity: critical
- Duration: 5m
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: error rate của `request_failed / request_received`, ngưỡng 2%.
- Điều kiện và thời gian duy trì: error rate lớn hơn 2% trong 5 phút.
- Ảnh hưởng tới người dùng: request thất bại thay vì nhận câu trả lời.
- Ba bước kiểm tra đầu tiên: (1) kiểm tra panel errors, (2) lọc `request_failed` theo error type và correlation ID, (3) mở trace cùng ID để xác định span lỗi.
- Mitigation tạm thời: khôi phục dependency lỗi hoặc tắt scenario; theo dõi error rate trước khi đóng alert.
- Owner: `student-2A202603679`

## Alert 3

- Tên: `RetrievalSuccessDegraded`
- Severity: warning
- Duration: 5m
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: tỷ lệ `tool_success == true`, ngưỡng tối thiểu 90%.
- Điều kiện và thời gian duy trì: retrieval success rate thấp hơn 90% trong 5 phút.
- Ảnh hưởng tới người dùng: câu trả lời thiếu context hoặc request thất bại khi truy xuất tài liệu.
- Ba bước kiểm tra đầu tiên: (1) kiểm tra retrieval success trên dashboard, (2) lọc các event có `tool_success=false`, (3) mở trace cùng ID để xác định nguyên nhân retrieval.
- Mitigation tạm thời: kiểm tra vector store/kết nối retrieval, khôi phục service và xác nhận success rate trở lại trên 90%.
- Owner: `student-2A202603679`
