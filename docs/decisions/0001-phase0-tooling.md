# ADR 0001 — Phase 0 tooling choices

Status: accepted (2026-07-13)

## Context

Phase 0 dựng khung repo phải chạy y hệt trên Windows/Ubuntu/Fedora, chưa cần phần
cứng hay model (CLAUDE.md, Phase 0). Vài lựa chọn tool có trade-off đáng ghi lại để
không phải tranh luận lại sau này.

## Quyết định

1. **Task runner: `nox` (không phải Makefile/bash script).** `make` không có sẵn
   trên Windows; nox là Python nên chạy giống hệt trên cả 3 OS. Nox dùng
   `venv_backend="uv"` để tận dụng tốc độ của uv thay vì `virtualenv` mặc định.

2. **ffmpeg cài ở hệ điều hành, không bundle qua pip.** `FileVideoSource` dùng
   `cv2.VideoCapture(..., cv2.CAP_FFMPEG)` và trông cậy vào ffmpeg cài sẵn trên máy
   (README có hướng dẫn `apt`/`dnf`/winget-choco theo từng OS). Có cân nhắc gói
   `imageio-ffmpeg`/`ffmpeg-python` (bundle binary qua pip, không cần cài tay) — ít
   lỗi "quên cài ffmpeg" hơn, nhưng thêm một binary lạ vào venv và lệch khỏi hướng
   dẫn per-OS trong CLAUDE.md mục 3b. Giữ nguyên cài hệ thống; nếu việc này gây phiền
   thực tế cho Dương, đây là chỗ dễ đổi sang bundled.

3. **`opencv-python-headless` thay vì `opencv-python`.** Mất `cv2.imshow()` để xem
   trực tiếp lúc debug cục bộ, đổi lại tránh phụ thuộc GUI/Qt hay lỗi trên CI runner
   headless (Windows/Linux). Đúng tinh thần "chạy unattended" của dự án. Có thể thêm
   `opencv-python` như một extra riêng sau nếu cần xem trực quan lúc dev.

4. **CI matrix chỉ có `ubuntu-latest` + `windows-latest`, không có Fedora.**
   GitHub-hosted runner không có Fedora sẵn. Tính tương thích Fedora do Dương tự xác
   nhận cục bộ (máy dev chính là Fedora). Có thể thêm job container `fedora:latest`
   chạy trên `ubuntu-latest` sau này nếu cần CI hoá — chưa làm ở Phase 0.

5. **Fixture video test là synthetic, không phải video chuồng thật.**
   `tests/conftest.py::synthetic_video` sinh một clip ngắn bằng `cv2.VideoWriter`
   ngay lúc test chạy, không commit file `.mp4`/`.avi` nào vào `tests/fixtures/`.
   CLAUDE.md mục 5 kỳ vọng "video mẫu ngắn trong `tests/fixtures/`" — video synthetic
   không thay thế hoàn toàn video thật (khác nén, khác artefact, khác mật độ gà thật).
   **Việc còn nợ:** khi có 1 đoạn video chuồng thật ngắn (vài giây, ẩn danh nếu cần),
   thay fixture synthetic bằng file thật trong `tests/fixtures/`.

## Hệ quả

- Phase 0 không kéo `torch`/`ultralytics` vào dependency — thêm ở đầu Phase 1 khi
  thật sự train/infer.
- `RTSPVideoSource` tồn tại trong `ingest/` nhưng luôn raise `NotImplementedError` —
  interface đã chừa chỗ, chưa cắm logic thật (khoá tới Milestone 1B).
