import shutil
import torch
from pipeline.exceptions import PipelineError


def check_ffmpeg():
    """Verify ffmpeg is installed and accessible on PATH."""
    if not shutil.which("ffmpeg"):
        raise PipelineError(
            "ffmpeg is not installed or not found on PATH.\n"
            "Install ffmpeg and ensure it is accessible before running the pipeline.\n"
            "  Windows: https://ffmpeg.org/download.html\n"
            "  Linux:   sudo apt install ffmpeg\n"
            "  macOS:   brew install ffmpeg"
        )


def check_cuda():
    """Verify a CUDA-capable GPU is available."""
    if not torch.cuda.is_available():
        raise PipelineError(
            "CUDA is not available. This pipeline requires a CUDA-capable GPU.\n"
            "Ensure your GPU drivers and CUDA toolkit are installed correctly."
        )
    device_name = torch.cuda.get_device_name(0)
    print(f"[preflight] CUDA OK — {device_name}")


def run_preflight_checks():
    """Run all pre-flight validation checks before starting the pipeline."""
    print("[preflight] Checking ffmpeg...")
    check_ffmpeg()
    print("[preflight] ffmpeg OK")

    print("[preflight] Checking CUDA...")
    check_cuda()
