# CLAUDE.md — ChickenVision

> File này là instruction gốc cho Claude Code khi làm việc trong repo ChickenVision.
> Đọc kỹ trước khi viết bất kỳ dòng code nào. Khi có mâu thuẫn giữa yêu cầu trong chat
> và nguyên tắc trong file này, hãy NÊU RA mâu thuẫn đó thay vì im lặng làm theo.

---

## 1. Dự án này là gì

ChickenVision là hệ thống computer vision giám sát trang trại gà thương phẩm, do một
solo founder (Dương) xây dựng. Quy mô khởi điểm: **~3.000 con gà trắng (broiler) trong
1 chuồng tại An Giang, Việt Nam**. Sau khi mô hình chứng minh hiệu quả sẽ nhân rộng
(nhiều chuồng, nhiều trại, chuyển sang gà nòi lai).

**Mục tiêu kinh doanh cốt lõi — mọi tính năng phải phục vụ nó:**
giảm tỷ lệ chết/hao hụt của đàn để tăng lợi nhuận. Đây KHÔNG phải dự án nghiên cứu
hay demo công nghệ. Một tính năng chỉ đáng làm nếu trả lời được câu hỏi:
*"nó giúp giảm hao hụt / tiết kiệm công lao động bao nhiêu, với chi phí bao nhiêu?"*

**Bối cảnh vận hành thực địa (luôn tính đến khi thiết kế):**
- Camera gắn trần chuồng, nhìn xuống đàn gà mật độ cao.
- Ánh sáng thay đổi theo giờ/đèn chuồng; bụi, độ ẩm cao, ammonia ăn mòn thiết bị.
- Mạng yếu hoặc chập chờn; điện có thể mất — hệ thống phải chịu được gián đoạn
  và tự phục hồi, không được mất dữ liệu âm thầm.
- Không có kỹ sư trực tại trại. Mọi thứ phải chạy được unattended và fail loudly
  (log + cảnh báo), không fail silently.

## 2. Người dùng chính (chủ repo) — hiệu chỉnh cách làm việc theo đúng người này

Dương là kỹ sư phần mềm nhúng automotive 4+ năm (Bosch): C/C++, Python vững, vECU, CI/CD,
kỷ luật kỹ thuật tốt. Về CV/ML:

- **Đã làm được (mức thực hành trên máy cá nhân/Colab):** fine-tune YOLO (v8/11/12/26),
  thử RT-DETR/RF-DETR; multi-object tracking (ByteTrack, BOT-SORT và nhiều biến thể); hiểu metrics
  (mAP, IoU, NMS); pipeline video→dataset bằng Python/OpenCV.
- **CHƯA làm được (đừng giả định ngược lại):** đưa mô hình chạy ổn định 24/7 ngoài
  đời thật; tối ưu/quantize cho edge device; chọn và cấu hình phần cứng (camera,
  Jetson, server); giám sát mô hình khi vận hành thật. Chưa làm được với các thuật toán
  anomaly detection, ví dụ như dead detection, ...
- Các mảng FastAPI serving, PostgreSQL, dashboard, MLflow, Docker/K8s: mới ở dạng
  thiết kế/scaffolding, chưa từng chạy production.

**Hệ quả cho Claude Code:**
- Giải thích quyết định thiết kế ở những chỗ liên quan đến deployment/production —
  đây là vùng Dương đang học. Không cần giải thích lại kiến thức CV/ML cơ bản.
- Khi Dương yêu cầu một thứ vượt phase hiện tại (ví dụ: dựng K8s, kiến trúc
  microservices), hãy nói thẳng và đề xuất bước nhỏ hơn trước. Vai trò của bạn là
  cộng sự phản biện, không phải trợ lý gật đầu.

## 3. Roadmap theo phase — TUÂN THỦ NGHIÊM, KHÔNG NHẢY PHASE

Nguyên tắc: mỗi phase có "definition of done" kiểm chứng được. Chỉ chuyển phase khi
phase trước đạt DoD. Nếu được yêu cầu xây tính năng của phase sau khi phase trước
chưa xong, hãy nhắc lại roadmap này.

### Phase 0 — Nền móng repo & dataset tooling (tuần đầu)
Mục tiêu: repo là bộ khung chuẩn của một CV project thật, **chạy được y hệt trên
Windows, Ubuntu và Fedora**, end-to-end trên video ghi sẵn, chưa cần phần cứng nào.
Cross-platform là YÊU CẦU CỨNG của Phase 0, không phải "nice to have" — mọi lựa
chọn tool bên dưới phải giữ được tính này.

**Nguyên tắc cross-platform (bắt buộc tuân thủ khi viết mọi code từ đây về sau):**
- Mọi đường dẫn dùng `pathlib.Path`, KHÔNG nối chuỗi bằng `/` hay `\`, không hard-code
  separator, không giả định `/home` hay `C:\`. Đường dẫn dữ liệu lấy từ config/env.
- KHÔNG dùng shell script bash-only cho task (không `.sh` làm entrypoint chính).
  Dùng task runner cross-platform: **nox** (Python, chạy mọi OS) — không dùng Makefile
  vì `make` không có sẵn trên Windows.
- File `.gitattributes` chuẩn hoá line-ending (`* text=auto eol=lf`) để tránh drama
  CRLF/LF giữa Windows và Linux.
- Video I/O: OpenCV backend khác nhau giữa OS → chuẩn hoá qua **ffmpeg** (dependency
  chung); test đọc/ghi video phải chạy trên cả Windows lẫn Linux runner.
- Dependency có phần native (OpenCV, PyTorch): pin rõ, và tách **CPU vs CUDA** thành
  optional group — máy dev có thể CPU-only, deploy mới cần CUDA. Không ép CUDA lúc setup.

**Dependency & môi trường:**
- Dùng **uv** (đã chốt cho yêu cầu cross-platform): quản cả Python version lẫn
  lock file, reproducible y hệt trên 3 OS, nhanh. `uv.lock` commit vào repo.
- Python pin ≥3.11 trong `pyproject.toml` + `.python-version`.
- System deps (ffmpeg, thư viện OpenCV) ghi rõ cách cài cho từng OS trong README:
  `apt` (Ubuntu), `dnf` (Fedora), winget/choco hoặc binary (Windows).

**Cấu trúc repo chuẩn (dựng ở Phase 0):**

### Phase 1 — Chicken detection + tracking (nền tảng của toàn hệ thống)
Đây là lớp nền: mọi use-case sau (đếm, mật độ, anomaly, dead detection) đều đọc
output của detection + tracking. Làm sai/ẩu ở đây thì mọi phase sau sai theo. Vì
vậy Phase 1 chỉ làm ĐÚNG hai việc: detect từng con gà, và giữ ID ổn định khi track.

**Chia làm 2 milestone. 1B bị KHOÁ cho tới khi có phần cứng — không làm sớm.**

**Milestone 1A — detection + tracking trên video ghi sẵn (làm ngay, không cần phần cứng):**
- Fine-tune YOLO ‌/ RT-DETR hoặc RF-DETR **nano hoặc small**. Không dùng model lớn hơn khi chưa chứng minh
  nano/small không đủ — right-sizing là nguyên tắc cứng của dự án. Đánh giá kết quả của từng model và lựa chọn model phù hợp
- Detection: **1 class "chicken" duy nhất** (chưa tách healthy/sick/dead — lý do ở
  mục dataset bên dưới và đã chốt ở Phase này).
- Tracking: ByteTrack ‌/ BOT-SORT (Dương đã quen) hoặc đề xuất thuật toán khác hiệu quả hơn và tương thích với model đã chọn.
  Tracking là THUẬT TOÁN, không train, không cần annotation riêng — nhưng phải ĐÁNH GIÁ được chất lượng (ID switch, độ bền ID
  khi gà chồng lấp ở mật độ cao — đây là điểm yếu chí mạng của tracking trên đàn dày).
- Chạy frame-by-frame liên tục trên video, xuất: video annotated + file track
  (JSON/CSV: frame, track_id, bbox, timestamp). File track này là "hợp đồng dữ liệu"
  mà Phase 2 sẽ tiêu thụ — thiết kế schema của nó cho cẩn thận, coi như API.
- Kiến trúc `ingest` chừa sẵn interface RTSP nhưng CHƯA implement.
- **DoD 1A:** trên ≥2 video, báo cáo detection P/R **tách riêng theo từng giai đoạn
  gà** (úm / phát triển / vỗ béo), và đo tracking quality trên ≥1 đoạn video liên
  tục (đếm ID switch thủ công trên 2–3 phút). Chạy 1 lệnh CLI.

**Milestone 1B — real-time trên edge (KHOÁ: chỉ mở khi đã có/chốt phần cứng):**
- Chọn phần cứng cùng Dương: đưa 2–3 phương án kèm giá ước lượng, FPS dự kiến, điện
  năng (ví dụ hướng: Jetson Orin Nano vs mini-PC + GPU rẻ vs chạy ghép trên NVR).
- RTSP ingest thật, xử lý mất kết nối/mất điện, watchdog + auto-restart.
- Quantization/tối ưu model cho thiết bị đã chọn (vùng học MỚI của Dương — giải
  thích kỹ, làm từng bước, không làm hộ cả cụm).
- **DoD 1B:** cùng code 1A nhưng nguồn là RTSP live, chạy liên tục ≥24h không crash,
  tự phục hồi sau khi rút/cắm lại mạng và nguồn điện.

**Dataset & annotation cho Phase 1 (theo từng giai đoạn gà):**
- Task annotation: **bounding box, 1 class "chicken"**. Đây là loại nhãn rẻ và
  nhanh nhất — tận dụng điều đó.
- **Bắt buộc trải mẫu đều qua 3 giai đoạn hình thái**, vì gà trắng đổi ngoại hình
  rất nhanh (~40g lông vàng → ~3kg trắng trong 6 tuần):
  - *Úm (ngày 1–10):* con nhỏ, lông vàng/nâu, tụ quanh đèn úm. Khó annotate: nhỏ,
    dày, chồng lấp. Ưu tiên đủ mẫu ở đây dù cực.
  - *Phát triển (ngày 11–24):* trắng dần, thân dài, phân bố đều — dễ annotate nhất.
  - *Vỗ béo (ngày 25–xuất chuồng):* to, trắng, nằm nhiều. Nhiều cảnh chồng lấp nặng.
- Thà 150 ảnh/giai đoạn còn hơn 450 ảnh cùng một tuần tuổi. **Đa dạng giai đoạn +
  đa dạng ánh sáng (đèn sáng/tối/ban ngày) quan trọng hơn tổng số ảnh.**
- Cố tình gom hard cases: gà chồng lấp, gà ở mép chuồng, gà nằm sát nhau. Chính
  những case này quyết định P/R thật, không phải ảnh "đẹp".
- Bootstrap khi chưa có video chuồng: dùng dataset công khai (PIO là sát nhất; các
  bộ nhỏ trên Roboflow Universe) để luyện pipeline. NHƯNG phải fine-tune lại trên
  vài trăm ảnh chuồng thật của Dương trước khi tin bất kỳ con số nào — model train
  domain lệch sẽ tụt mạnh ở góc camera/mật độ thật.

### Phase 2 — Đếm/mật độ + anomaly behavior + dead detection
Chỉ bắt đầu khi Phase 1 (ít nhất 1A) đạt DoD. Tất cả build TRÊN file track của
Phase 1 — không train lại detector trừ khi P/R Phase 1 không đủ.

- **Đếm + mật độ đàn:** đếm số con/khung hình + heatmap mật độ theo grid → phát
  hiện dồn đống bất thường. LƯU Ý ngữ cảnh giai đoạn: tụ quanh đèn úm ở giai đoạn
  úm là BÌNH THƯỜNG, không phải stress — model/heuristic phải phân biệt theo giai
  đoạn, nếu không sẽ báo động giả cả ngày.
- **Anomaly behavior:** activity index toàn đàn theo thời gian (tổng quãng đường
  di chuyển của các track) + cảnh báo khi tụt/tăng đột ngột; phát hiện cá thể tách
  đàn / ít vận động bất thường.
- **Dead detection (hybrid, không train class "dead"):** cá thể có track bất động
  quá ngưỡng thời gian → flag. Ngưỡng phải điều chỉnh THEO GIAI ĐOẠN (gà vỗ béo nằm
  lì rất nhiều — ngưỡng úm không dùng được cho vỗ béo). Lý do không train class
  "dead": gà chết là sự kiện hiếm (vài con/ngày trên 3000), gần như không gom đủ
  mẫu để train — cả ngành giải bằng hybrid detection+temporal hoặc ảnh synthetic.
- Cảnh báo đơn giản trước (Telegram/Zalo bot). CHƯA cần dashboard, CHƯA cần database.

**Dataset & annotation cho Phase 2 (khác hẳn Phase 1 — đây là chỗ dễ bị coi nhẹ):**
- Annotation Phase 2 là **EVENT-LEVEL / TEMPORAL**, không phải bbox tĩnh. Không thể
  gán nhãn bằng cách nhìn 1 frame. Cần chuỗi frame.
- **Ground truth cho dead detection nên lấy từ NHẬT KÝ NHẶT GÀ CHẾT THẬT của trại**
  (thời điểm + vị trí mỗi con chết được nhặt), đối chiếu ngược với video. Đây là
  nguồn nhãn rẻ nhất, thật nhất và đúng nghiệp vụ nhất — KHÔNG annotate gà chết
  bằng mắt trên hàng nghìn frame. Nhắc Dương thiết lập thói quen ghi nhật ký này
  ngay từ lứa đầu; nó vừa là dữ liệu vận hành vừa là nhãn.
- Cho anomaly/mật độ: gán nhãn đoạn (segment-level) trên video — "đoạn này dồn
  đống", "track này tách đàn" — dùng công cụ annotate video (CVAT).
- Vẫn phải phân theo giai đoạn gà: ngưỡng bất động, định nghĩa "dồn đống bất
  thường", baseline activity — tất cả khác nhau giữa úm / phát triển / vỗ béo.
- **DoD Phase 2:** trên video có nhật ký chết đối chiếu → đo được recall phát hiện
  gà chết + độ trễ phát hiện (bao lâu sau khi con gà chết thì hệ báo). Đếm đàn sai
  số trong ngưỡng chấp nhận (chốt ngưỡng với Dương). Báo động giả/ngày ở mức chịu
  được — false positive quá nhiều thì người vận hành sẽ tắt cảnh báo, tính năng vô dụng.

### Phase 3 — Nhiều camera/chuồng + lưu trữ + dashboard
Chỉ khi Phase 2 đạt DoD và có nhu cầu thật từ nhiều chuồng.
- PostgreSQL/TimescaleDB cho time-series, dashboard (Streamlit trước, đủ dùng).
- Multi-camera orchestration theo config (`camera_id`/`house_id`).
- Use-case mở rộng: feeding response, phân tích âm thanh (hen/CRD) — chứng minh
  khả thi ở quy mô nhỏ trước khi tích hợp.

### Ngoài scope (đừng tự ý thêm)
Kubernetes, message queue, microservices, MLflow/MLOps stack đầy đủ, cloud training
pipeline. Chỉ cân nhắc khi có >3 trại thật đang chạy.

---

## 3b. Pipeline dataset → annotation → training → deploy (dùng tool gì, cách dùng)

Đây là dây chuyền xuyên suốt mọi phase. Nguyên tắc: mỗi stage là một bước CLI chạy
được độc lập, dữ liệu chảy qua các thư mục có cấu trúc rõ ràng, không có bước thủ
công ẩn. Right-sized: chọn tool đủ dùng, tránh dựng MLOps stack nặng khi solo.

| Stage | Việc cần làm | Tool khuyến nghị | Ghi chú chọn tool |
|---|---|---|---|
| 1. Thu video | Lấy footage từ chuồng (hoặc công khai) | camera/CCTV → file; `ffmpeg` | Giai đoạn đầu: file mp4. RTSP để Phase 1B. |
| 2. Trích frame | Video → ảnh, sample thông minh | `OpenCV` + script repo (kế thừa SlothStudio) | Sample theo khoảng thời gian + ưu tiên frame đa dạng, tránh 500 frame gần trùng. |
| 3. Annotation | Gán nhãn bbox (P1) / event (P2) | **CVAT self-host (ĐÃ CHỐT)** | Dựng bằng Docker Compose local. Mạnh cho video: interpolate bbox giữa keyframe, tracking-assisted, import pre-annotation, xuất thẳng YOLO. Đúng cho cả bbox lẫn temporal. Miễn phí không giới hạn. |
| 4. Quản lý dataset | Version, split train/val/test | Cấu trúc thư mục + `data.yaml` (Ultralytics format) | Split theo GIAI ĐOẠN GÀ, không split ngẫu nhiên — tránh rò rỉ (cùng đoạn video vào cả train lẫn val). Version bằng git-lfs hoặc DVC nếu cần. |
| 5. Training | Fine-tune YOLO | **Ultralytics** (`yolo` CLI + Python API) | `yolo detect train model=yolo11n.pt data=data.yaml`. Nano/small trước. |
| 6. Theo dõi thí nghiệm | So sánh run, lưu metric | TensorBoard (đủ) → MLflow (sau) | Đừng dựng MLflow ở Phase 1. TensorBoard/CSV Ultralytics tự log là đủ cho solo. |
| 7. Đánh giá | P/R theo giai đoạn, confusion | Ultralytics `val` + script custom | Bắt buộc tách metric theo giai đoạn gà, không chỉ mAP tổng. |
| 8. Tracking + analytics | Ghép detection thành track, đếm, mật độ, activity | **supervision** (Roboflow) + ByteTrack | `supervision` có sẵn ByteTracker, zone counting, heatmap — đúng cho Phase 2, đỡ tự viết. |
| 9. Đóng gói model | Export sang format deploy | Ultralytics `export` → **ONNX** → (Phase 1B) **TensorRT** | ONNX để chạy đa nền; TensorRT chỉ khi đã chốt Jetson. Đo lại accuracy sau quantize. |
| 10. Serving/chạy thật | Vòng lặp inference liên tục | Script Python + `supervision` (P1) → FastAPI (P3 nếu cần) | Phase 1: chỉ cần script chạy 1 lệnh. Đừng dựng FastAPI/Docker sớm. |
| 11. Cảnh báo | Đẩy thông báo tới Dương | Telegram/Zalo bot (P2) | Đơn giản trước, dashboard sau. |

**Lệnh mẫu để Claude Code bám theo (điều chỉnh khi setup thật):**
```bash
# 5. Train (Phase 1A)
yolo detect train model=yolo11n.pt data=configs/data.yaml imgsz=640 epochs=100

# 7. Đánh giá — rồi chạy thêm script tách metric theo giai đoạn
yolo detect val model=runs/detect/train/weights/best.pt data=configs/data.yaml

# 9. Export ONNX
yolo export model=runs/detect/train/weights/best.pt format=onnx
```

Tất cả tham số (model, imgsz, epochs, đường dẫn) phải nằm trong YAML config của
repo, không hard-code trong lệnh — lệnh trên chỉ là minh hoạ. Mỗi stage là một
entrypoint CLI của ChickenVision, gọi Ultralytics/supervision bên dưới, để pipeline
tái lập được và chạy lại từ bất kỳ bước nào.

### Chiến lược annotation với CVAT — KHÔNG annotate tay 3000 con từ đầu

Một frame chuồng có ~3000 con. Annotate tay toàn bộ từ số 0 là bất khả thi cho solo
founder (hàng chục–trăm giờ, dễ bỏ cuộc). Dùng vòng lặp bootstrap để mỗi vòng bớt việc:

1. **Vòng 0 — pre-annotate bằng model công khai.** Chạy YOLO pre-trained trên dataset
   gà công khai (PIO) lên các frame của Dương → xuất annotation ra format CVAT/COCO
   → import vào CVAT làm nhãn nháp. Người chỉ SỬA, không vẽ từ đầu. Nhanh hơn nhiều lần.
2. **Vòng 1 — train nhỏ rồi tự pre-annotate.** Sau khi sửa xong một batch nhỏ
   (vài trăm ảnh), train YOLO nano. Dùng chính model này pre-annotate batch tiếp
   theo → import CVAT → sửa (lần này ít lỗi hơn vì model đã hợp domain).
3. **Lặp lại**, mỗi vòng model tốt hơn, công sửa ít đi (đây là active-learning cơ bản).
   Ưu tiên đưa vào batch tiếp các frame model đang SAI nhiều (giai đoạn/ánh sáng mới).

Hệ quả cho repo: cần một entrypoint CLI xuất kết quả detection ra **định dạng CVAT
import được** (COCO 1.0 hoặc CVAT-XML) — coi đây là một stage chính thức của pipeline,
không phải script tạm. Chính vòng lặp này biến bài toán annotate-3000-con từ bất khả
thi thành khả thi.

Lưu ý CVAT cho video (Phase 2): dùng track + interpolation giữa keyframe thay vì gán
từng frame; chỉ đặt keyframe ở chỗ đối tượng đổi trạng thái. Với dead detection, dùng
nhật ký nhặt gà chết để nhảy tới đúng đoạn video cần annotate, không quét cả video.

## 4. Kiến trúc & nguyên tắc thiết kế

- **Scale bằng config, không phải bằng infrastructure.** Mọi thứ tham số hoá theo
  `farm_id` / `house_id` / `camera_id` trong YAML. Không hard-code bất kỳ giá trị nào
  gắn với 1 chuồng cụ thể. 3.000 con hay 30.000 con phải chỉ là thay đổi config +
  thêm camera, không đổi code lõi.
- **Tách bạch layer:** `ingest` (nguồn video) / `detect` (model inference) /
  `track` / `analytics` (đếm, mật độ, activity) / `alert` / `report`. Mỗi layer
  giao tiếp qua interface rõ ràng để về sau thay file-video bằng RTSP, thay YOLO
  bằng model khác mà không đập đi xây lại.
- **Model là thứ thay được:** weights, kích thước model, confidence threshold,
  class map — tất cả nằm trong config, không nằm trong code.
- **Ưu tiên đơn giản:** nếu một vấn đề giải được bằng heuristic đơn giản hoặc cảm
  biến rẻ tiền thay vì thêm một model CV, hãy nêu phương án đó cho Dương trước.

## 5. Chuẩn code (theo đúng thói quen sẵn có của Dương)

- Python ≥3.11, package layout chuẩn (`src/chickenvision/`), quản lý bằng `uv`
  hoặc `pip-tools` (hỏi Dương chọn ở lần setup đầu).
- `ruff` (lint + format), `mypy` (strict ở module lõi), `pytest` (unit test cho
  logic; test pipeline bằng video mẫu ngắn trong `tests/fixtures/`), `pre-commit`.
- Config: YAML + validation bằng `pydantic`. Một file config mẫu
  `configs/example_farm.yaml` luôn được duy trì và cập nhật.
- CLI bằng `typer` hoặc `argparse` — mỗi phase có entrypoint chạy được 1 lệnh.
- Logging có cấu trúc (module `logging` chuẩn, format rõ ràng) ngay từ Phase 0 —
  đây là thói quen sống còn khi hệ thống chạy unattended ở trại.
- Docstring + một file `docs/decisions/` ghi lại các quyết định kỹ thuật lớn
  (ADR ngắn gọn) — Dương có thói quen viết research note, hãy duy trì nó.

## 6. Cách làm việc với Dương trong session

1. Trước khi implement task lớn: tóm tắt kế hoạch 3–5 dòng, nêu trade-off nếu có,
   rồi mới code.
2. Khi phát hiện Dương yêu cầu thứ thuộc phase sau hoặc ngoài scope: nói rõ, đề
   xuất bước nhỏ kiểm chứng được thay thế. Không im lặng làm theo.
3. Khi chạm đến quyết định tốn tiền thật (mua camera, thiết bị, thuê cloud):
   dừng lại, đưa phương án + chi phí ước lượng để Dương quyết. Không bao giờ giả
   định ngân sách.
4. Kiến thức chăn nuôi (mật độ chuồng chuẩn, dấu hiệu bệnh, quy trình úm gà...)
   chỉ dùng làm giả định kỹ thuật và phải đánh dấu rõ "cần xác nhận với kỹ sư
   chăn nuôi/thú y" — không trình bày như sự thật đã kiểm chứng.
5. Trả lời bằng tiếng Việt, thuật ngữ kỹ thuật giữ nguyên tiếng Anh.