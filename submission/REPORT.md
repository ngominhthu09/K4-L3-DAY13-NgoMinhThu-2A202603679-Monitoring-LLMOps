# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

## 1. Thông tin học viên

- **Họ và tên:** Ngô Minh Thu
- **MSSV:** 2A202602679
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/ngominhthu09/K4-L3-DAY13-NgoMinhThu-2A202603679-Monitoring-LLMOps *(tên repository hiện còn MSSV cũ; cần đổi trên GitHub trước khi nộp)*
- **Commit code đã kiểm chứng ở evidence #01:** `38cf7844b22b82d2f78fa14d35188be81c048656`; SHA nộp sẽ được cập nhật sau commit evidence cuối.
- **Challenge ID:** `K4-l3b-challenge-s05`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-2A202602679`.

## 2. Evidence index

> Checklist này theo README/CP4 mới. Các file có trạng thái **Cần chụp** phải được tạo từ runtime và project Langfuse cá nhân trước khi nộp.

| # | Evidence | Đường dẫn tương đối | Trạng thái |
|---:|---|---|---|
| 01 | Pytest cuối | `evidence/01-pytest.png` | Có: SHA `38cf784`, 24 passed. |
| 02 | Log validator | `evidence/02-log-validator.png` | Có: Estimated Score 100/100. |
| 03 | Dashboard validator | `evidence/03-dashboard-validator.png` | Có: HỢP LỆ 6/6 panel. |
| 04 | Structured log với correlation ID tự đặt | `evidence/04-structured-log.png` | Có: `req-1a2b3c4d`. |
| 05 | PII redaction | `evidence/05-pii-redaction.png` | Có: bốn loại PII đều được redact. |
| 06 | Trace list (≥ 10 root traces) | `evidence/06-trace-list.png` | Có: project khớp MSSV, tổng khoảng 149 observations. |
| 07 | Trace waterfall/tree | `evidence/07-trace-waterfall.png` | **Chụp lại:** ảnh hiện có chỉ là load-test output, không phải waterfall. |
| 08 | Metadata agent và generation | `evidence/08a-trace-metadata.png`, `evidence/08b-generation-metadata.png` | **Chụp lại:** ảnh hiện có lộ public key. |
| 09 | Prompt versions v1/v2 | `evidence/09-prompt-versions.png` | Có: version #1 baseline/production và #2 candidate/latest. |
| 10 | Promote và rollback production | `evidence/10a-prompt-promote.png`, `evidence/10b-prompt-rollback.png` | Có: production ở v2 rồi rollback về v1. |
| 11 | Dashboard runtime đủ 6 panel | `evidence/11-dashboard-overview.png` | Có: đủ 6 panel, time range và thresholds. |
| 12 | Incident metric | `evidence/12-incident-metric.png` | Có P95 2654 ms > 2000 ms; cần xác nhận yêu cầu biểu đồ baseline/incident nếu giảng viên bắt buộc timeline. |
| 13 | Incident log bất thường | `evidence/13-incident-log.png` | **Cần chụp** cùng correlation ID với #14. |
| 14 | Incident trace | `evidence/14-incident-trace.png` | Có trace retrieval 2.50 s; vẫn cần #13 cùng correlation ID. |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---|---|---|
| `validate_logs.py` | Không lưu output baseline | 100/100; 137 log records; thiếu field/enrichment: 0; 60 correlation ID | Đạt JSON schema, propagation, enrichment và PII scrubbing. |
| `validate_dashboard.py` | Không lưu output baseline | Hợp lệ: 6/6 panel | Contract dashboard đầy đủ. |
| `pytest` | Không lưu output baseline | 24 passed trong 3.26 s | Toàn bộ test hiện có đều qua. |
| Số traces hợp lệ | — | 67 root observations (`lab-agent-run`), khoảng 149 observations tổng | Xem trace list; mỗi request có cây agent/retrieval/generation. |
| Số PII leak | — | 0 | Kết quả từ log validator. |
| Latency P95 / TTFT P95 | — | 2654 ms / 50 ms | Snapshot incident mới nhất; P95 vượt ngưỡng SLO 2000 ms. |
| Retrieval success rate | — | 100.0% | Incident là chậm retrieval, không phải retrieval thất bại. |

## 4. Logging và PII

- **Cách tạo/nhận và truyền correlation ID:** `CorrelationIdMiddleware` nhận `x-request-id`; nếu không có thì tạo `req-<8-hex>`. ID được bind vào `structlog` context, lưu ở `request.state.correlation_id`, trả lại trong response header `x-request-id`, và truyền vào `LabAgent.run`. Metadata trace cũng có `correlation_id` để nối với log.
- **Các metadata được ghi vào structured log:** các trường chuẩn gồm `ts`, `level`, `service`, `event`, `correlation_id`, `env`, `user_id_hash`, `session_id`, `feature`, `model`, `latency_ms`, `ttft_ms`, `tokens_in`, `tokens_out`, `cost_usd`, `quality_score`, `error_type`, `tool_name`, `tool_success` và `payload` đã được tóm tắt/scrub.
- **Cách bảo đảm PII được scrub trước khi ghi:** processor `scrub_event` chạy trước JSON renderer/file writer và scrub đệ quy tất cả string, dict, list, tuple. `scrub_text` redacts email, số điện thoại Việt Nam, CCCD 12 số và số thẻ thanh toán. User ID chỉ được ghi dưới dạng SHA-256 rút gọn (`user_id_hash`).
- **Cách kiểm chứng kết quả:** `evidence/02-log-validator.png` cho thấy 137 record, 0 trường bắt buộc/enrichment thiếu và 0 PII leak. `evidence/04-structured-log.png` minh họa hai event cùng `correlation_id=req-1a2b3c4d`; `evidence/05-pii-redaction.png` xác nhận bốn loại PII đều đã được redact.

## 5. Tracing và prompt versioning

- **Cách xác nhận traces do chính tôi tạo trong project cá nhân:** `evidence/06-trace-list.png` hiển thị organization `ngominhthu09's Organization`, project `day13-k4-l3b-2A202602679`, và các observation `lab-agent-run`, `retrieval`, `generation`. Không dùng key/ảnh API key trong evidence.
- **Cấu trúc root/retrieval/generation observations:** root trace `day13-agent-request` chứa `lab-agent-run` (agent); hai child observations là `retrieval` (retriever/span) và `generation` (LLM generation). Generation ghi model, token usage và cost; không capture raw input/output.
- **Cách nối trace với log:** cùng `correlation_id` nằm trong JSON log và trace metadata. Ví dụ `req-00ad9bec` có log `request_received` lúc `2026-09-30T05:03:16.454044Z` và `response_sent` lúc `05:03:19.111601Z`; trace `7ef44f7c34bc4dad6cfb6ce8dbee1e48` hiển thị metadata cùng ID.
- **Prompt name:** `day13-chat`.
- **Version/label baseline:** version `#1`, labels `baseline` và `production`.
- **Version/label candidate:** version `#2`, label `candidate` (có thêm `latest`).
- **Trace ID của mỗi version:** version #2/candidate: `8504ff98fe65927ad25171370af3e267` (prompt link `day13-chat - v2`); version #2/production trong incident: `7ef44f7c34bc4dad6cfb6ce8dbee1e48`. Evidence hiện chưa hiển thị riêng trace ID đã chạy bằng version #1/baseline.
- **Cách promote và rollback `production`:** chuyển label `production` từ #1 sang #2 mà không sửa code, chạy request và kiểm tra metadata `prompt_name`, `prompt_label`, `prompt_version`; rollback bằng cách gán lại `production` về #1. Trace incident lúc 12:03 hiển thị version 2/label `production`; ảnh prompt lúc 12:59 hiển thị `production` đã ở #1 và #2 là `candidate`, là evidence cho trạng thái rollback.

## 6. Dashboard, SLO và alerts

- **Dashboard và sáu panel:** dashboard dùng `data/logs.jsonl`, refresh 30 giây/range 60 phút, gồm: (1) Latency percentiles & TTFT, (2) Request traffic, (3) Error rate & retrieval success, (4) Cost over time, (5) Input/output tokens, (6) Quality proxy. Snapshot incident mới nhất: P50/P95/P99 là 445/2654/2669 ms, TTFT P95 50 ms, 95 requests, error 0%, retrieval success 100%, tổng cost $0.1997, 3,163 input tokens, 12,684 output tokens, quality 0.86.
- **SLO và lý do chọn:** SLO `fast_successful_requests` là 99.5% request có `response_sent` với `latency_ms <= 2000` trong 28 ngày. Điều này gắn trực tiếp với trải nghiệm người dùng: trả lời thành công nhưng chậm vẫn không đạt SLO.
- **Cách tính error budget:** error budget là 0.5% trong cửa sổ 28 ngày. Với 10,000 request, tối đa 50 request được phép không thành công hoặc có latency lớn hơn 2000 ms; 9,950 request còn lại phải đạt SLO.
- **Ba alert và runbook tương ứng:**
  - `HighLatencyP95` — warning khi P95 latency > 2000 ms trong 5 phút; mở panel latency, lọc log theo ID, rồi mở trace cùng ID. Runbook: `docs/alerts.md#alert-1`.
  - `ElevatedErrorRate` — critical khi `request_failed/request_received > 2%` trong 5 phút; kiểm tra panel errors, `error_type` và trace. Runbook: `docs/alerts.md#alert-2`.
  - `RetrievalSuccessDegraded` — warning khi tỷ lệ `tool_success=true` < 90% trong 5 phút; kiểm tra event tool rồi trace retrieval. Runbook: `docs/alerts.md#alert-3`.

## 7. Điều tra challenge

- **Challenge ID:** `K4-l3b-challenge-s05`.
- **Khoảng thời gian điều tra:** khoảng `2026-09-30 05:03:16–05:03:19 UTC` (12:03:16–12:03:19 UTC+7) cho request đại diện `req-00ad9bec`.
- **Triệu chứng từ metrics:** dashboard cho P95 latency 2654 ms và P99 2669 ms, vượt threshold 2000 ms; đồng thời TTFT P95 chỉ 50 ms, error rate 0% và retrieval success 100%. Vấn đề là một bước nội bộ kéo dài, không phải lỗi HTTP hay thời điểm token đầu tiên.
- **Log line và correlation ID liên quan:** phải được cập nhật từ `evidence/13-incident-log.png`; correlation ID ở ảnh này phải khớp tuyệt đối với trace #14. Không dùng lại log cũ có ID khác.
- **Trace ID và span gây ảnh hưởng:** trace dự kiến `7ef44f7c34bc4dad6cfb6ce8dbee1e48`; `retrieval` mất 2.50 s, trong khi `generation` mất 153 ms và root mất 2.65 s. Chụp lại vào `evidence/14-incident-trace.png` trong project tên đúng và cập nhật trace ID nếu cần.
- **Root cause:** practice incident `rag_slow` làm hàm retrieval ngủ 2.5 giây (`STATE["rag_slow"]`), nên latency P95 tăng dù generation, TTFT và retrieval success vẫn bình thường.
- **Fix action:** tắt scenario `rag_slow`/loại bỏ delay, sau đó chạy lại workload và xác nhận P95 trở về dưới 2000 ms trước khi đóng alert.
- **Preventive measure:** giữ alert `HighLatencyP95` 5 phút, runbook bắt buộc đối chiếu dashboard → correlation ID → trace span; thêm regression test/load test với threshold latency cho retrieval.

## 8. Giải thích và tự đánh giá

- **Một quyết định kỹ thuật quan trọng và lý do:** scrub PII ở processor chung ngay trước bước render/ghi file thay vì dựa vào từng call site. Nhờ đó payload hay metadata mới cũng không dễ bypass PII protection.
- **Một lỗi/blocker đã gặp:** incident làm latency tăng nhưng error rate và retrieval success vẫn đẹp; nếu chỉ xem panel Errors thì dễ kết luận nhầm hệ thống bình thường.
- **Cách tìm nguyên nhân và xử lý:** bắt đầu bằng P95/P99 bất thường, lọc log lấy correlation ID, sau đó mở trace và so sánh duration retrieval (2.50 s) với generation (153 ms). Điều này khoanh vùng đúng `rag_slow`.
- **Cách hiểu luồng Metrics → Logs → Traces:** Metrics phát hiện *có* incident và khoảng thời gian; Logs chọn đúng request bị ảnh hưởng bằng correlation ID; Traces phân rã request để xác định *bước nào* gây chậm/lỗi. Ba lớp cần cùng trỏ đến một request để kết luận đáng tin cậy.
- **Vai trò của prompt version, token/cost, SLO hoặc rollback trong vận hành LLM:** prompt version giúp tái hiện request theo đúng cấu hình. Labels cho phép promote/rollback không đổi code; token/cost và SLO cho biết thay đổi prompt có làm chất lượng vận hành xấu đi không.
- **Điều quan trọng nhất đã học:** observability hữu ích khi log có cấu trúc, an toàn PII và trace có cùng correlation ID — không chỉ là có thật nhiều log.
- **Hạn chế hoặc phần chưa hoàn thành:** baseline output không được lưu; #07 waterfall, #08a/#08b metadata an toàn và #13 incident log cùng correlation ID với #14 vẫn chưa hoàn thành. Working tree cũng còn thay đổi chưa commit, nên cần chạy lại ba lệnh kiểm tra, cập nhật SHA và commit toàn bộ evidence.

## 9. Checklist trước khi nộp

- [x] Evidence #06, #09, #10a, #10b và #14 thuộc project `day13-k4-l3b-2A202602679`.
- [ ] Chụp lại #07 dưới dạng Timeline/Tree; chụp lại #08a/#08b sao cho không lộ `pk-lf-...`.
- [ ] Chụp `13-incident-log.png` với đúng correlation ID của #14, rồi ghi ID/trace ID vào mục 7.
- [ ] Xác nhận #12 đáp ứng yêu cầu metric incident; nếu bắt buộc baseline và incident cùng trục thời gian, bổ sung dashboard timeline.
- [ ] Đổi tên repository trên GitHub để MSSV trong tên repo khớp `2A202602679`; chỉ stage `app`, `tests`, `config`, `docs`, `submission`; không stage `.env`, `.venv`, `data/logs.jsonl` hoặc `config/challenge.json`.
- [ ] Commit/push evidence cuối, cập nhật SHA nộp và kiểm tra tất cả đường dẫn evidence mở được trên GitHub.
