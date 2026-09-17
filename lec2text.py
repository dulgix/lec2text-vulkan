"""whisper.cpp(Vulkan) 기반 영상 음성 텍스트 변환기."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MODEL_NAME = "medium"
LANGUAGE = "ko"
SUPPORTED_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm"}
ROOT_DIR = Path(__file__).resolve().parent
WHISPER_CLI = ROOT_DIR / "bin" / "whisper-cli.exe"
MODEL_PATH = ROOT_DIR / "models" / f"ggml-{MODEL_NAME}.bin"


def require_command(command, label):
    if shutil.which(command) is None:
        print(f"❌ {label}를 찾을 수 없습니다.")
        print(f"   새 PowerShell을 열고 `{command} -version`으로 다시 확인해주세요.")
        sys.exit(1)


def check_requirements():
    require_command("ffmpeg", "FFmpeg")
    if not WHISPER_CLI.is_file():
        print("❌ Vulkan용 whisper.cpp 실행 파일을 찾을 수 없습니다.")
        print("   PowerShell에서 .\\setup_vulkan.ps1 을 먼저 실행해주세요.")
        sys.exit(1)
    if not MODEL_PATH.is_file():
        print(f"❌ 모델 파일을 찾을 수 없습니다: {MODEL_PATH.name}")
        print("   PowerShell에서 .\\setup_vulkan.ps1 을 다시 실행해주세요.")
        sys.exit(1)


def choose_video_file(files):
    if not files:
        print("❌ 현재 폴더에 변환할 영상 파일이 없습니다.")
        sys.exit(1)
    print("변환할 영상 파일을 선택하세요:")
    for i, file in enumerate(files, 1):
        print(f"{i}. {file}")
    while True:
        try:
            choice = int(input("번호 입력: ").strip())
            if 1 <= choice <= len(files):
                return files[choice - 1]
            print("❌ 목록에 있는 번호를 입력해주세요.")
        except ValueError:
            print("❌ 숫자를 입력해주세요.")


def choose_progress_mode():
    print("\n진행 표시 방식을 선택하세요:")
    print("1. 진행률 표시 (권장)")
    print("2. 인식된 세그먼트 텍스트를 콘솔에 출력")
    while True:
        mode = input("번호 입력: ").strip()
        if mode in {"1", "2"}:
            return mode
        print("❌ 1 또는 2를 입력해주세요.")


def extract_wav(video_path, wav_path):
    command = ["ffmpeg", "-y", "-i", str(video_path), "-vn", "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", str(wav_path)]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def run_whisper(wav_path, output_base, progress_mode):
    command = [str(WHISPER_CLI), "-m", str(MODEL_PATH), "-f", str(wav_path), "-l", LANGUAGE, "-otxt", "-osrt", "-of", str(output_base)]
    if progress_mode == "1":
        command.append("-pp")
    completed = subprocess.run(
    command,
    text=True,
    encoding="utf-8",
    errors="replace",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT
)
    if progress_mode == "2" and completed.stdout:
        print(completed.stdout)
    if completed.returncode != 0:
        raise RuntimeError(completed.stdout.strip() or "알 수 없는 오류")


def srt_to_segment_text(srt_path, output_path):
    blocks = [block.strip() for block in srt_path.read_text(encoding="utf-8").split("\n\n") if block.strip()]
    with output_path.open("w", encoding="utf-8") as output:
        for index, block in enumerate(blocks, 1):
            lines = block.splitlines()
            if len(lines) < 3 or " --> " not in lines[1]:
                continue
            start, end = lines[1].split(" --> ", 1)
            output.write(f"[{index}] {start.replace(',', '.')} ~ {end.replace(',', '.')}\n")
            output.write("\n".join(lines[2:]).strip() + "\n\n")


def main():
    check_requirements()
    files = sorted(f for f in os.listdir() if Path(f).suffix.lower() in SUPPORTED_EXTENSIONS)
    input_video = Path(choose_video_file(files)).resolve()
    progress_mode = choose_progress_mode()
    base_name = input_video.stem
    save_dir = Path("result") / base_name
    save_dir.mkdir(parents=True, exist_ok=True)
    output_txt = save_dir / f"{base_name}.txt"
    output_srt = save_dir / f"{base_name}.srt"
    output_segment_txt = save_dir / f"{base_name}_segments.txt"
    print("\n🧠 whisper.cpp Vulkan 변환 준비 중...")
    print(f"   모델: {MODEL_NAME}\n   언어: {LANGUAGE}\n   장치: Vulkan (AMD Radeon 포함 GPU 가속)")
    try:
        with tempfile.TemporaryDirectory(prefix="lec2text_") as temp_dir:
            temp_dir = Path(temp_dir)
            wav_path, output_base = temp_dir / "audio.wav", temp_dir / "transcript"
            print(f"\n🎧 '{input_video.name}'에서 오디오 추출 중...")
            extract_wav(input_video, wav_path)
            print("📝 음성 인식 중...")
            run_whisper(wav_path, output_base, progress_mode)
            generated_txt, generated_srt = output_base.with_suffix(".txt"), output_base.with_suffix(".srt")
            if not generated_txt.exists() or not generated_srt.exists():
                raise RuntimeError("whisper.cpp가 TXT 또는 SRT 파일을 만들지 못했습니다.")
            shutil.copy2(generated_txt, output_txt)
            shutil.copy2(generated_srt, output_srt)
            srt_to_segment_text(output_srt, output_segment_txt)
    except (subprocess.CalledProcessError, RuntimeError) as error:
        print(f"❌ 변환 중 오류가 발생했습니다:\n{error}")
        sys.exit(1)
    print("\n✅ 변환 완료!")
    print(f"📄 일반 텍스트: {output_txt}\n🕒 타임스탬프 텍스트: {output_segment_txt}\n🎬 SRT 자막: {output_srt}")


if __name__ == "__main__":
    main()
