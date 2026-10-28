import atexit
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image
import streamlit as st

st.set_page_config(
    page_title="Waste Classifier - Render Console",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MODEL_PATH = "models/final/mobilenet_v2_20261028T112329/best_model.keras"
CLASS_NAMES = ["cardboard", "glass", "metal", "paper", "plastic", "trash"]

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #111827;
        background-color: #ffffff;
        margin: 0 !important;
        padding: 0 !important;
    }

    header[data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
        min-height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    div[data-testid="stDecoration"] {
        display: none !important;
    }

    div[data-testid="stToolbar"] {
        display: none !important;
    }

    footer {
        display: none !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    #MainMenu {
        visibility: hidden !important;
    }

    .stApp {
        background-color: #ffffff !important;
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: hidden !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stAppViewContainer"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    div[data-testid="stAppViewContainer"] > section.main {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    div[data-testid="stAppViewBlockContainer"] {
        padding: 0 !important;
        margin: 0 !important;
    }

    .main {
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: hidden !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    .main .block-container {
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: hidden !important;
    }

    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }

    ::-webkit-scrollbar-track {
        background: #f9fafb;
    }

    ::-webkit-scrollbar-thumb {
        background: #d1d5db;
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #9ca3af;
    }

    .top-navbar {
        height: 40px;
        min-height: 40px;
        border-bottom: 1px solid #e5e7eb;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 16px;
        background-color: #ffffff;
        box-sizing: border-box;
    }

    .nav-left {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .nav-brand {
        font-weight: 700;
        font-size: 0.825rem;
        letter-spacing: -0.01em;
        color: #111827;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .nav-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        background-color: #f3f4f6;
        color: #4b5563;
        padding: 1px 5px;
        border-radius: 4px;
        border: 1px solid #e5e7eb;
    }

    .nav-right {
        display: flex;
        align-items: center;
        gap: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.725rem;
        color: #6b7280;
    }

    .status-indicator {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        color: #059669;
        font-weight: 600;
    }

    .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #10b981;
    }

    div[data-testid="stHorizontalBlock"] {
        height: calc(100vh - 40px) !important;
        max-height: calc(100vh - 40px) !important;
        gap: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }

    div[data-testid="column"]:nth-of-type(1) {
        width: 50% !important;
        min-width: 50% !important;
        max-width: 50% !important;
        height: calc(100vh - 40px) !important;
        max-height: calc(100vh - 40px) !important;
        border-right: 1px solid #e5e7eb !important;
        padding: 16px !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        background-color: #fafafa !important;
    }

    div[data-testid="column"]:nth-of-type(2) {
        width: 50% !important;
        min-width: 50% !important;
        max-width: 50% !important;
        height: calc(100vh - 40px) !important;
        max-height: calc(100vh - 40px) !important;
        padding: 16px 20px 48px 20px !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        background-color: #ffffff !important;
    }

    div[data-testid="stFileUploader"] {
        height: 100% !important;
        display: flex !important;
        flex-direction: column !important;
    }

    div[data-testid="stFileUploader"] > section {
        flex: 1 !important;
        min-height: calc(100vh - 100px) !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: #ffffff !important;
        border: 1px dashed #d1d5db !important;
        border-radius: 4px !important;
        padding: 40px !important;
        box-sizing: border-box !important;
        transition: all 0.15s ease-in-out !important;
    }

    div[data-testid="stFileUploader"] > section:hover {
        border-color: #111827 !important;
        background-color: #f9fafb !important;
    }

    div[data-testid="stFileUploader"] [data-testid="stFileUploaderDropzoneInstructions"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        gap: 8px !important;
    }

    .preview-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 10px 14px;
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 4px 4px 0 0;
        border-bottom: none;
    }

    .preview-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 600;
        color: #374151;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .image-preview-frame {
        position: relative;
        flex: 1;
        min-height: 0;
        height: calc(100vh - 130px);
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 0 0 4px 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 16px;
        box-sizing: border-box;
        overflow: hidden;
    }

    .image-preview-frame img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        border-radius: 2px;
    }

    .panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 8px;
        margin-bottom: 10px;
    }

    .panel-title {
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: -0.01em;
        color: #111827;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }

    .box-card {
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        background-color: #ffffff;
        margin-bottom: 10px;
    }

    .box-card-header {
        background-color: #f9fafb;
        border-bottom: 1px solid #e5e7eb;
        padding: 6px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #4b5563;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .box-card-body {
        padding: 10px 14px;
    }

    .primary-result {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
    }

    .primary-name {
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: #111827;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }

    .primary-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.875rem;
        font-weight: 700;
        background-color: #ecfdf5;
        color: #065f46;
        border: 1px solid #a7f3d0;
        padding: 2px 8px;
        border-radius: 4px;
    }

    .table-container {
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        overflow: hidden;
        margin-bottom: 10px;
    }

    .table-header {
        display: grid;
        grid-template-columns: 130px 1fr 80px;
        background-color: #f9fafb;
        border-bottom: 1px solid #e5e7eb;
        padding: 6px 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.675rem;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
    }

    .table-row {
        display: grid;
        grid-template-columns: 130px 1fr 80px;
        align-items: center;
        padding: 6px 12px;
        border-bottom: 1px solid #f3f4f6;
        font-size: 0.8rem;
    }

    .table-row:last-child {
        border-bottom: none;
    }

    .table-row.active {
        background-color: #f0fdf4;
    }

    .row-name {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        font-size: 0.775rem;
        text-transform: lowercase;
        color: #111827;
    }

    .table-row.active .row-name {
        color: #065f46;
        font-weight: 700;
    }

    .row-bar-bg {
        background-color: #e5e7eb;
        height: 6px;
        border-radius: 2px;
        overflow: hidden;
        margin-right: 12px;
    }

    .row-bar-fill {
        height: 100%;
        background-color: #9ca3af;
        border-radius: 2px;
    }

    .table-row.active .row-bar-fill {
        background-color: #059669;
    }

    .row-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        text-align: right;
        color: #4b5563;
    }

    .table-row.active .row-val {
        color: #065f46;
        font-weight: 700;
    }

    .specs-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 6px;
    }

    .spec-item {
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        padding: 6px 10px;
    }

    .spec-label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #6b7280;
        text-transform: uppercase;
    }

    .spec-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.725rem;
        font-weight: 600;
        color: #111827;
        margin-top: 1px;
    }

    .empty-console {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        min-height: 380px;
        border: 1px dashed #e5e7eb;
        border-radius: 4px;
        padding: 32px;
        text-align: center;
        background-color: #fafafa;
    }

    .empty-console-title {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        font-weight: 600;
        color: #374151;
        margin-bottom: 6px;
    }

    .empty-console-sub {
        font-size: 0.8rem;
        color: #6b7280;
        max-width: 280px;
    }

    div[data-testid="stButton"] > button {
        background-color: #ffffff !important;
        color: #111827 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.775rem !important;
        font-weight: 600 !important;
        padding: 4px 10px !important;
        border-radius: 4px !important;
        border: 1px solid #d1d5db !important;
        box-shadow: none !important;
        transition: all 0.15s ease-in-out !important;
    }

    div[data-testid="stButton"] > button:hover {
        background-color: #f3f4f6 !important;
        border-color: #9ca3af !important;
    }

    @keyframes laserSweep {
        0% { top: 0%; opacity: 0; }
        15% { opacity: 1; }
        85% { opacity: 1; }
        100% { top: 98%; opacity: 0; }
    }

    .scanner-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        pointer-events: none;
        overflow: hidden;
        z-index: 10;
    }

    .scanner-laser {
        position: absolute;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent 5%, #10b981 50%, transparent 95%);
        box-shadow: 0 0 15px #10b981, 0 0 5px #34d399;
        animation: laserSweep 1.8s cubic-bezier(0.4, 0, 0.2, 1) infinite;
    }

    .scanner-grid {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: radial-gradient(circle at center, rgba(16, 185, 129, 0.08) 0%, transparent 70%);
    }

    @keyframes pulseShimmer {
        0% { opacity: 0.5; background-position: -200% 0; }
        50% { opacity: 1; }
        100% { opacity: 0.5; background-position: 200% 0; }
    }

    .loading-card {
        border: 1px solid #e5e7eb;
        border-radius: 4px;
        background-color: #ffffff;
        padding: 16px;
        margin-bottom: 12px;
    }

    .loading-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.775rem;
        font-weight: 700;
        color: #059669;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .loading-spinner-ring {
        width: 16px;
        height: 16px;
        border: 2px solid #e5e7eb;
        border-top: 2px solid #10b981;
        border-radius: 50%;
        animation: spinRing 0.8s linear infinite;
    }

    @keyframes spinRing {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .skeleton-box {
        background: linear-gradient(90deg, #f3f4f6 25%, #e5e7eb 50%, #f3f4f6 75%);
        background-size: 200% 100%;
        animation: pulseShimmer 1.5s infinite;
        border-radius: 3px;
    }

    .skeleton-title {
        height: 24px;
        width: 55%;
        margin-bottom: 8px;
    }

    .skeleton-subtitle {
        height: 12px;
        width: 30%;
        margin-bottom: 16px;
    }

    .skeleton-bar-row {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;
    }

    .skeleton-bar-label {
        width: 65px;
        height: 12px;
    }

    .skeleton-bar-track {
        flex: 1;
        height: 8px;
    }

    .skeleton-bar-val {
        width: 40px;
        height: 12px;
    }

    .scanning-banner {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        margin-bottom: 8px;
        border-radius: 4px;
        background-color: #ecfdf5;
        border: 1px solid #a7f3d0;
        color: #065f46;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.725rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }

    .scanning-pulse {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: #10b981;
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
        animation: pulseDot 1.2s infinite;
    }

    @keyframes pulseDot {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


class InferenceRunner:
    def __init__(self, model_path_str: str):
        self.model_path = Path(model_path_str).resolve()
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        self.in_process_engine = None
        self.process = None
        self._init_runner()

    def _init_runner(self):
        try:
            import tensorflow
            from src.api.inference import InferenceEngine
            self.in_process_engine = InferenceEngine(str(self.model_path))
            self.in_process_engine._ensure_loaded()
            return
        except (ImportError, Exception):
            pass

        venv_python = self._locate_venv_python()
        if not venv_python:
            raise RuntimeError("Python ML environment (venv) not found.")

        worker_code = (
            "import sys, json, cv2\n"
            "from src.api.inference import InferenceEngine\n"
            "engine = InferenceEngine(sys.argv[1])\n"
            "engine._ensure_loaded()\n"
            "print('READY', flush=True)\n"
            "for line in iter(sys.stdin.readline, ''):\n"
            "    p = line.strip()\n"
            "    if not p:\n"
            "        continue\n"
            "    img = cv2.imread(p)\n"
            "    if img is None:\n"
            "        print(json.dumps({'error': 'Could not decode image'}), flush=True)\n"
            "        continue\n"
            "    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)\n"
            "    res = engine.predict(img_rgb)\n"
            "    print(json.dumps(res.model_dump()), flush=True)\n"
        )

        try:
            self.process = subprocess.Popen(
                [str(venv_python), "-u", "-c", worker_code, str(self.model_path)],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            ready_token = self.process.stdout.readline().strip()
            if ready_token != "READY":
                self.close()
                self.process = None
            else:
                atexit.register(self.close)
        except Exception:
            self.process = None

    def _locate_venv_python(self) -> Path | None:
        base_dir = Path(__file__).resolve().parent
        candidates = [
            base_dir / "venv" / "Scripts" / "python.exe",
            base_dir / "venv" / "bin" / "python",
            Path("venv/Scripts/python.exe").resolve(),
            Path("venv/bin/python").resolve(),
        ]
        for c in candidates:
            if c.exists():
                return c
        return None

    def predict(self, image_path: str) -> dict:
        if self.in_process_engine is not None:
            import cv2
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError("Could not decode image.")
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return self.in_process_engine.predict(img_rgb).model_dump()

        if self.process is not None and self.process.poll() is None:
            try:
                self.process.stdin.write(f"{image_path}\n")
                self.process.stdin.flush()
                out = self.process.stdout.readline().strip()
                if out:
                    data = json.loads(out)
                    if "error" in data:
                        raise ValueError(data["error"])
                    return data
            except Exception:
                self.close()
                self.process = None

        return self._run_cli_predict(image_path)

    def _run_cli_predict(self, image_path: str) -> dict:
        venv_python = self._locate_venv_python()
        if not venv_python:
            raise RuntimeError("Python ML environment (venv) not found.")
        predict_script = Path(__file__).resolve().parent / "scripts" / "predict.py"
        proc = subprocess.run(
            [str(venv_python), str(predict_script), "--image", image_path, "--model", str(self.model_path)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Prediction script failed: {proc.stderr}")
        return json.loads(proc.stdout)

    def close(self):
        if self.process is not None and self.process.poll() is None:
            try:
                self.process.stdin.close()
                self.process.terminate()
                self.process.wait(timeout=2)
            except Exception:
                pass



def build_loading_html() -> str:
    return (
        '<div class="box-card loading-card">'
        '<div class="loading-header">'
        '<div class="loading-spinner-ring"></div>'
        '<span>ANALYZING IMAGE WITH MOBILENETV2...</span>'
        '</div>'
        '<div class="box-card-body" style="padding: 12px 14px;">'
        '<div class="skeleton-box skeleton-title"></div>'
        '<div class="skeleton-box skeleton-subtitle"></div>'
        '<div class="skeleton-bar-row">'
        '<div class="skeleton-box skeleton-bar-label"></div>'
        '<div class="skeleton-box skeleton-bar-track"></div>'
        '<div class="skeleton-box skeleton-bar-val"></div>'
        '</div>'
        '<div class="skeleton-bar-row">'
        '<div class="skeleton-box skeleton-bar-label"></div>'
        '<div class="skeleton-box skeleton-bar-track"></div>'
        '<div class="skeleton-box skeleton-bar-val"></div>'
        '</div>'
        '<div class="skeleton-bar-row">'
        '<div class="skeleton-box skeleton-bar-label"></div>'
        '<div class="skeleton-box skeleton-bar-track"></div>'
        '<div class="skeleton-box skeleton-bar-val"></div>'
        '</div>'
        '<div class="skeleton-bar-row">'
        '<div class="skeleton-box skeleton-bar-label"></div>'
        '<div class="skeleton-box skeleton-bar-track"></div>'
        '<div class="skeleton-box skeleton-bar-val"></div>'
        '</div>'
        '</div>'
        '</div>'
        '<div class="box-card">'
        '<div class="box-card-header">'
        '<span>Inference Status</span>'
        '<span>Active</span>'
        '</div>'
        '<div class="box-card-body">'
        '<div class="specs-grid">'
        '<div class="spec-item"><div class="spec-label">Process</div><div class="spec-val" style="color: #059669;">Forward Pass...</div></div>'
        '<div class="spec-item"><div class="spec-label">Grad-CAM</div><div class="spec-val" style="color: #059669;">Computing Map...</div></div>'
        '</div>'
        '</div>'
        '</div>'
    )


def build_result_html(res: dict) -> str:
    top_class = res.get("predicted_class", "unknown")
    confidence = float(res.get("confidence", 0.0))
    probabilities = res.get("probabilities", {})
    conf_pct_str = f"{confidence * 100:.2f}%"

    rows_html = ""
    sorted_probs = sorted(probabilities.items(), key=lambda kv: kv[1], reverse=True)
    for c_name, prob in sorted_probs:
        is_active = (c_name == top_class)
        row_cls = "table-row active" if is_active else "table-row"
        pct_val = prob * 100
        rows_html += (
            f'<div class="{row_cls}">'
            f'<div class="row-name">{c_name}</div>'
            f'<div class="row-bar-bg">'
            f'<div class="row-bar-fill" style="width: {pct_val:.2f}%;"></div>'
            f'</div>'
            f'<div class="row-val">{pct_val:.2f}%</div>'
            f'</div>'
        )

    return (
        f'<div class="box-card">'
        f'<div class="box-card-header">'
        f'<span>Classification Result</span>'
        f'<span>Argmax</span>'
        f'</div>'
        f'<div class="box-card-body">'
        f'<div class="primary-result">'
        f'<span class="primary-name">{top_class}</span>'
        f'<span class="primary-badge">{conf_pct_str}</span>'
        f'</div>'
        f'</div>'
        f'</div>'
        f'<div class="table-container">'
        f'<div class="table-header">'
        f'<span>Class</span>'
        f'<span>Distribution</span>'
        f'<span style="text-align: right;">Probability</span>'
        f'</div>'
        f'{rows_html}'
        f'</div>'
        f'<div class="box-card">'
        f'<div class="box-card-header">'
        f'<span>System Metadata</span>'
        f'<span>Runtime</span>'
        f'</div>'
        f'<div class="box-card-body">'
        f'<div class="specs-grid">'
        f'<div class="spec-item"><div class="spec-label">Model Architecture</div><div class="spec-val">MobileNetV2</div></div>'
        f'<div class="spec-item"><div class="spec-label">Input Resolution</div><div class="spec-val">224 x 224 x 3</div></div>'
        f'<div class="spec-item"><div class="spec-label">Model Format</div><div class="spec-val">Keras SavedModel</div></div>'
        f'<div class="spec-item"><div class="spec-label">Backend Worker</div><div class="spec-val">Python ML venv</div></div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )


def build_empty_html() -> str:
    return (
        '<div class="empty-console">'
        '<div class="empty-console-title">AWAITING IMAGE INPUT</div>'
        '<div class="empty-console-sub">'
        'Drop a waste image into the left console or browse from your disk to run instant classification.'
        '</div>'
        '</div>'
    )

@st.cache_resource(show_spinner=False)
def get_model_runner(path: str) -> InferenceRunner:
    return InferenceRunner(path)


runner = None
try:
    runner = get_model_runner(MODEL_PATH)
except Exception as e:
    st.error(f"Model initialization error: {e}")
    st.stop()

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "prev_file_sig" not in st.session_state:
    st.session_state.prev_file_sig = None

if "current_result" not in st.session_state:
    st.session_state.current_result = None

st.markdown(
    """
    <div class="top-navbar">
        <div class="nav-left">
            <span class="nav-brand">Render Waste Classifier</span>
            <span class="nav-tag">mobilenet_v2</span>
            <span class="nav-tag">trashnet-6</span>
        </div>
        <div class="nav-right">
            <span class="status-indicator">
                <span class="status-dot"></span>
                ACTIVE
            </span>
            <span>PORT 8501</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

left_col, right_col = st.columns(2, gap="small")

with left_col:
    upload_key = f"uploader_{st.session_state.uploader_key}"
    uploaded_file = st.file_uploader(
        "Upload Image",
        type=["jpg", "jpeg", "png"],
        key=upload_key,
        label_visibility="collapsed",
    )

    image_bytes = None
    image_is_valid = False
    filename = None
    filesize_str = ""

    if uploaded_file is not None:
        try:
            image_bytes = uploaded_file.getvalue()
            pil_img = Image.open(uploaded_file)
            pil_img.verify()
            image_is_valid = True
            filename = uploaded_file.name
            kb_size = len(image_bytes) / 1024
            filesize_str = f"{kb_size:.1f} KB" if kb_size < 1024 else f"{kb_size/1024:.2f} MB"
        except Exception:
            st.error("Invalid image format. Supported formats: JPG, JPEG, PNG.")
            image_is_valid = False

    if image_is_valid and image_bytes is not None:
        st.markdown(
            """
            <style>
                div[data-testid='stFileUploader'] {
                    margin-bottom: 8px !important;
                }
                div[data-testid='stFileUploader'] > section {
                    min-height: 44px !important;
                    height: 44px !important;
                    padding: 4px 12px !important;
                    display: flex !important;
                    flex-direction: row !important;
                    align-items: center !important;
                    justify-content: space-between !important;
                    border: 1px dashed #cbd5e1 !important;
                    background-color: #f8fafc !important;
                }
                div[data-testid='stFileUploader'] > section:hover {
                    border-color: #059669 !important;
                    background-color: #f0fdf4 !important;
                }
                div[data-testid='stFileUploader'] [data-testid='stFileUploaderDropzoneInstructions'] {
                    flex-direction: row !important;
                    gap: 8px !important;
                    font-size: 0.725rem !important;
                }
                div[data-testid='stFileUploader'] button {
                    font-size: 0.725rem !important;
                    padding: 2px 8px !important;
                }
                div[data-testid="stImage"] {
                    background-color: #ffffff !important;
                    border: 1px solid #e5e7eb !important;
                    border-radius: 4px !important;
                    padding: 12px !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                }
                div[data-testid="stImage"] img {
                    max-height: calc(100vh - 200px) !important;
                    object-fit: contain !important;
                    border-radius: 4px !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        header_c1, header_c2 = st.columns([3, 1])
        with header_c1:
            st.markdown(
                f'<div class="preview-title" style="padding-top: 6px;"><span>{filename}</span> <span style="color: #9ca3af; font-size: 0.725rem;">({filesize_str})</span></div>',
                unsafe_allow_html=True,
            )
        with header_c2:
            if st.button("✕ Clear Image", key="clear_img_btn", use_container_width=True):
                st.session_state.uploader_key += 1
                st.session_state.prev_file_sig = None
                st.session_state.current_result = None
                st.rerun()

        scan_status_placeholder = st.empty()
        st.image(image_bytes, use_container_width=True)

with right_col:
    st.markdown(
        '<div class="panel-header"><span class="panel-title">Inference Output</span><span class="nav-tag">6 Classes</span></div>',
        unsafe_allow_html=True,
    )
    right_container = st.empty()

    if image_is_valid and image_bytes is not None:
        file_sig = f"{filename}_{len(image_bytes)}"
        needs_inference = (st.session_state.prev_file_sig != file_sig)

        if needs_inference:
            scan_status_placeholder.markdown(
                '<div class="scanning-banner"><div class="scanning-pulse"></div><span>ANALYZING IMAGE WITH MOBILENETV2...</span></div>',
                unsafe_allow_html=True,
            )
            right_container.markdown(build_loading_html(), unsafe_allow_html=True)

            suffix = Path(filename).suffix.lower()
            if suffix not in [".jpg", ".jpeg", ".png"]:
                suffix = ".jpg"

            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(image_bytes)
                tmp_path = tmp.name

            try:
                result = runner.predict(tmp_path)
                st.session_state.current_result = result
                st.session_state.prev_file_sig = file_sig
            except Exception as exc:
                st.error(f"Inference failed: {exc}")
                st.session_state.current_result = None
                st.session_state.prev_file_sig = None
            finally:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass

            scan_status_placeholder.empty()

            if st.session_state.current_result is not None:
                right_container.markdown(
                    build_result_html(st.session_state.current_result),
                    unsafe_allow_html=True,
                )
        else:
            if st.session_state.current_result is not None:
                right_container.markdown(
                    build_result_html(st.session_state.current_result),
                    unsafe_allow_html=True,
                )
            else:
                right_container.markdown(build_empty_html(), unsafe_allow_html=True)
    else:
        right_container.markdown(build_empty_html(), unsafe_allow_html=True)
