# whisper.cpp를 Vulkan(GPU 가속) 옵션으로 빌드하고 한국어 모델을 받습니다.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$vendor = Join-Path $root ".vendor\whisper.cpp"
$bin = Join-Path $root "bin"
$models = Join-Path $root "models"
$modelName = "medium"  # lec2text.py의 MODEL_NAME과 같아야 합니다.
$modelPath = Join-Path $models "ggml-$modelName.bin"
function Require-Command($name, $hint) {
    if (-not (Get-Command $name -ErrorAction SilentlyContinue)) { throw "$name 이(가) 없습니다. $hint" }
}
Require-Command git "Git 설치 후 PowerShell을 다시 열어주세요: https://git-scm.com/download/win"
Require-Command cmake "CMake 설치 후 PowerShell을 다시 열어주세요: https://cmake.org/download/"
if (-not $env:VULKAN_SDK) {
    throw "Vulkan SDK가 없습니다. `winget install LunarG.VulkanSDK` 실행 후 PowerShell을 다시 열어주세요."
}
New-Item -ItemType Directory -Force -Path $bin, $models, (Split-Path $vendor -Parent) | Out-Null
if (-not (Test-Path $vendor)) {
    Write-Host "[1/3] whisper.cpp 내려받는 중..."
    git clone --depth 1 https://github.com/ggml-org/whisper.cpp.git $vendor
} else { Write-Host "[1/3] 기존 whisper.cpp 사용" }
Write-Host "[2/3] Vulkan GPU 가속 버전 빌드 중..."
cmake -S $vendor -B "$vendor\build" -DGGML_VULKAN=1
cmake --build "$vendor\build" --config Release --target whisper-cli
$cli = Get-ChildItem "$vendor\build" -Recurse -Filter "whisper-cli.exe" | Where-Object { $_.FullName -match "Release" } | Select-Object -First 1
if (-not $cli) { throw "whisper-cli.exe 빌드 결과를 찾지 못했습니다." }
Copy-Item $cli.FullName (Join-Path $bin "whisper-cli.exe") -Force
if (-not (Test-Path $modelPath)) {
    Write-Host "[3/3] ggml-$modelName 모델 다운로드 중 (약 1.5GB)..."
    Invoke-WebRequest "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-$modelName.bin?download=true" -OutFile $modelPath
} else { Write-Host "[3/3] 기존 모델 사용" }
Write-Host "완료! 다음 명령으로 변환하세요: python lec2text.py"
