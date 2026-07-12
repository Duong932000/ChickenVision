# ChickenVision

Hệ thống computer vision giám sát trang trại gà thương phẩm — giảm tỷ lệ chết/hao
hụt của đàn. Roadmap và nguyên tắc thiết kế đầy đủ nằm ở [`CLAUDE.md`](CLAUDE.md).

Repo hiện đang ở **Phase 0**: khung repo + trích frame từ video ghi sẵn, chưa cần
phần cứng, chưa cần model.

## Cài đặt

Yêu cầu: Python ≥3.11 (quản lý qua `uv`), ffmpeg cài ở hệ điều hành.

### 1. Cài `uv`

- **Ubuntu / Fedora:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### 2. Cài `ffmpeg` (dùng bởi OpenCV để đọc/ghi video)

- **Ubuntu:** `sudo apt install ffmpeg`
- **Fedora:** `sudo dnf install ffmpeg`
- **Windows:** `winget install ffmpeg` (hoặc `choco install ffmpeg`)

### 3. Cài môi trường dự án

```bash
uv sync
```

`uv` tự tải đúng phiên bản Python (theo `.python-version`) và cài dependencies từ
`uv.lock` — y hệt trên cả 3 OS.

## Chạy kiểm tra chất lượng code

```bash
uv run nox            # chạy lint + format check + typecheck + tests
uv run nox -s tests    # chỉ chạy test
```

## Trích frame từ video (Phase 0 CLI)

```bash
uv run chickenvision dataset extract-frames \
  --config configs/example_farm.yaml \
  --house house_01 \
  --camera cam_01 \
  --out data/frames/house_01_cam_01 \
  --interval-seconds 2.0
```

Lệnh này đọc đường dẫn video từ config (hoặc override bằng `--video`), sample frame
theo khoảng thời gian cố định, bỏ qua khung gần-trùng, rồi ghi ảnh `.jpg` + một file
manifest CSV (`frame_index, timestamp_s, source_video, output_path`) vào thư mục
`--out`. Manifest này dùng làm dữ liệu provenance khi import batch vào CVAT.

## Cấu trúc repo

```
src/chickenvision/
├── config/    # pydantic schema + loader cho configs/*.yaml (farm/house/camera)
├── ingest/    # VideoSource: FileVideoSource (dùng ngay), RTSPVideoSource (Phase 1B)
├── dataset/   # trích frame từ video, ghi manifest
└── cli/       # typer app, entrypoint `chickenvision`
```

Quyết định kỹ thuật lớn được ghi lại ngắn gọn trong
[`docs/decisions/`](docs/decisions/).
