# Vulkan 기반 영상 음성 텍스트 변환 도구

개인적으로 사용하기 위해 만든 영상 음성 텍스트 변환 도구입니다.

강의 영상이나 녹화 영상의 오디오를 Whisper 모델로 인식하여 일반 텍스트, 타임스탬프 텍스트, SRT 자막 파일로 저장합니다.

기존 PyTorch/CUDA 기반 Whisper 방식은 NVIDIA GPU에 적합하지만, AMD Radeon GPU에서는 CUDA를 사용할 수 없어 CPU로 처리됩니다. 이 프로젝트는 `whisper.cpp`를 Vulkan 옵션으로 빌드하여 AMD Radeon GPU에서도 음성 인식 연산을 활용할 수 있도록 구성했습니다.

## 구성 파일

| 파일명                | 설명                                                                  |
| ------------------ | ------------------------------------------------------------------- |
| `lec2text.py`      | 영상 선택, 오디오 추출, whisper.cpp 실행, 결과 저장을 담당하는 메인 파이썬 스크립트              |
| `setup_vulkan.ps1` | whisper.cpp 다운로드, Vulkan 빌드, Whisper 모델 다운로드를 자동화하는 PowerShell 스크립트 |
| `README.md`        | 설치 및 사용 방법 안내                                                       |
| `.gitignore`       | 모델, 빌드 결과, 영상 파일 등 GitHub에 올리지 않을 파일 설정                             |

## 요구 사항

* Python
* FFmpeg
* Git
* CMake
* Visual Studio Build Tools

  * `Desktop development with C++` 워크로드 필요
* Vulkan SDK
* Vulkan을 지원하는 GPU 및 그래픽 드라이버

  * AMD Radeon GPU 사용 가능

## 설치

### 1. FFmpeg 설치

Windows에서는 `winget`으로 설치할 수 있습니다.

```powershell
winget install Gyan.FFmpeg
```

설치 후 PowerShell 또는 VS Code를 완전히 종료하고 새로 열어 정상적으로 인식되는지 확인합니다.

```powershell
ffmpeg -version
```

### 2. Git과 CMake 설치

```powershell
winget install Git.Git
winget install Kitware.CMake
```

설치 후 새 PowerShell에서 아래 명령이 동작하는지 확인합니다.

```powershell
git --version
cmake --version
```

### 3. Visual Studio Build Tools 설치

Visual Studio Build Tools를 설치한 뒤, Visual Studio Installer에서 다음 워크로드를 추가합니다.

```text
Desktop development with C++
```

이 도구는 `whisper.cpp`의 C++ 코드를 `whisper-cli.exe` 실행 파일로 빌드하는 데 필요합니다.

### 4. Vulkan SDK 설치

[Vulkan SDK 공식 다운로드 페이지](https://vulkan.lunarg.com/sdk/home)에서 Windows용 Vulkan SDK를 설치합니다.

설치 후 PowerShell을 새로 열고 아래 명령을 입력합니다.

```powershell
$env:VULKAN_SDK
```

Vulkan SDK 설치 경로가 출력되면 정상입니다.

### 5. whisper.cpp Vulkan 버전 및 모델 설치

프로젝트 폴더에서 PowerShell을 열고 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup_vulkan.ps1
```

스크립트는 다음 작업을 자동으로 수행합니다.

1. `whisper.cpp` 소스코드 다운로드
2. Vulkan GPU 가속 옵션으로 빌드
3. `whisper-cli.exe` 생성
4. Whisper `medium` 모델 다운로드

`medium` 모델은 약 1.5GB입니다.

빌드 후 Vulkan 관련 DLL 파일을 실행 파일 폴더로 복사합니다.

```powershell
Copy-Item ".vendor\whisper.cpp\build\bin\Release\*.dll" ".\bin\" -Force
```

## 사용법

현재 프로젝트 폴더에 변환할 영상 파일을 넣은 뒤 실행합니다.

```powershell
python lec2text.py
```

지원하는 영상 확장자:

* `.mp4`
* `.mkv`
* `.mov`
* `.avi`
* `.webm`

실행하면 현재 폴더에 있는 영상 파일 목록이 출력됩니다.

```text
변환할 영상 파일을 선택하세요:
1. lecture.mp4
2. interview.mp4

번호 입력: 1
```

이후 진행 표시 방식을 선택할 수 있습니다.

```text
진행 표시 방식을 선택하세요:
1. 진행률 표시 (권장)
2. 인식된 세그먼트 텍스트를 콘솔에 출력
```

### 진행률 표시

Whisper가 음성 인식을 처리하는 진행 상황을 확인할 수 있습니다.

긴 영상이 정상적으로 처리 중인지 확인할 때 편리합니다.

### 세그먼트 출력

Whisper가 인식한 문장과 타임스탬프를 콘솔에 출력합니다.

```text
[00:00.000 --> 00:05.420] 안녕하세요.
[00:05.420 --> 00:11.830] 오늘은 운영체제에 대해서 알아보겠습니다.
```

## 동작 방식

```text
영상 파일 선택
→ FFmpeg로 영상에서 오디오 추출
→ 16kHz 모노 WAV로 임시 변환
→ whisper.cpp 실행
→ Vulkan을 통해 GPU 음성 인식
→ TXT / 타임스탬프 TXT / SRT 저장
→ 임시 WAV 파일 자동 삭제
```

파이썬은 파일 선택, FFmpeg 실행, 결과 저장을 담당합니다.

실제 음성 인식은 Vulkan 옵션으로 빌드된 `whisper-cli.exe`가 수행합니다.

```text
Python
→ FFmpeg
→ whisper-cli.exe
→ Vulkan
→ AMD Radeon GPU
```

## 출력

변환 결과는 다음 경로에 저장됩니다.

```text
result/영상파일명/
```

예를 들어 `lecture.mp4`를 변환하면 다음과 같이 생성됩니다.

```text
result/
└─ lecture/
   ├─ lecture.txt
   ├─ lecture_segments.txt
   └─ lecture.srt
```

각 파일의 용도는 다음과 같습니다.

| 파일                     | 설명                      |
| ---------------------- | ----------------------- |
| `lecture.txt`          | 전체 음성을 일반 텍스트로 저장       |
| `lecture_segments.txt` | 각 음성 구간의 타임스탬프와 텍스트 저장  |
| `lecture.srt`          | 영상에서 사용할 수 있는 SRT 자막 파일 |

### 타임스탬프 텍스트 예시

```text
[1] 00:00:00 ~ 00:00:05
안녕하세요.

[2] 00:00:05 ~ 00:00:11
오늘은 Whisper에 대해서 알아보겠습니다.
```

## 기본 설정

기본 Whisper 모델:

```python
MODEL_NAME = "medium"
```

기본 인식 언어:

```python
LANGUAGE = "ko"
```

VRAM 부족 등의 문제가 발생하면 `lec2text.py`와 `setup_vulkan.ps1`의 모델 이름을 모두 `small`로 변경할 수 있습니다. `small` 모델은 더 가볍지만 인식 정확도가 다소 낮아질 수 있습니다.

## GitHub 업로드 시 제외할 파일

아래 파일과 폴더는 용량이 크거나 실행 중 자동 생성되므로 GitHub에 올리지 않습니다.

```text
bin/
models/
.vendor/
result/
__pycache__/
*.mp4
*.mkv
*.mov
*.avi
*.webm
*.wav
```

## 참고 자료

* 기존 PyTorch/CUDA 기반 버전: [jyaniee/lec2text](https://github.com/jyaniee/lec2text)
* [whisper.cpp](https://github.com/ggml-org/whisper.cpp)
* [Vulkan SDK](https://vulkan.lunarg.com/sdk/home)
