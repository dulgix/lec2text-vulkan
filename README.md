# Radeon(Vulkan) 기반 영상 음성 텍스트 변환 도구

Windows에서 **whisper.cpp + Vulkan**으로 영상을 한국어 텍스트와 자막으로 변환하는 파이썬 프로그램입니다. 파이썬이 파일 선택·FFmpeg 오디오 추출·결과 정리를, whisper.cpp가 Radeon GPU를 이용한 음성 인식을 담당합니다.

## 처음 한 번만 설치

### 1. FFmpeg

```powershell
winget install Gyan.FFmpeg
```

PowerShell과 VS Code를 완전히 닫고 다시 연 뒤 아래가 동작하는지 확인합니다.

```powershell
ffmpeg -version
```

### 2. Git과 CMake

```powershell
winget install Git.Git
winget install Kitware.CMake
winget install LunarG.VulkanSDK
```

설치 후 PowerShell을 새로 열고, AMD Adrenalin 그래픽 드라이버도 최신인지 확인하세요. Vulkan SDK는 **빌드할 때만** 필요하고, 실제 변환은 AMD 드라이버의 Vulkan 기능을 사용합니다.

### 3. Vulkan whisper.cpp와 모델 설치

프로젝트 폴더에서 실행합니다.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup_vulkan.ps1
```

처음에는 엔진을 빌드하고 `medium` 모델(약 1.5GB)을 받습니다. 완료되면 `bin/whisper-cli.exe`와 `models/ggml-medium.bin`이 생성됩니다.

## 사용

변환할 영상을 이 폴더에 넣고 실행합니다.

```powershell
python lec2text.py
```

지원 형식: `.mp4`, `.mkv`, `.mov`, `.avi`, `.webm`

결과는 `result/영상이름/`에 TXT, 타임스탬프 TXT, SRT로 저장됩니다.

## 문제 해결

- `ffmpeg`, `git`, `cmake`를 찾지 못함: 설치 후 터미널/VS Code를 완전히 재시작하세요.
- CMake 빌드 오류: Visual Studio Build Tools에서 **Desktop development with C++**를 설치해야 할 수 있습니다.
- VRAM 부족: `lec2text.py`의 `MODEL_NAME`과 `setup_vulkan.ps1`의 `$modelName`을 모두 `small`로 바꾼 뒤 설치 스크립트를 다시 실행하세요.
- `testcuda.py`는 이름만 남겼습니다. 이 버전은 CUDA/PyTorch를 사용하지 않습니다.
