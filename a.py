import whisper

model = whisper.load_model("medium")

result = model.transcribe("week2-3.mp3", language="ko", verbose=True, fp16=False)

with open("week2-3.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])

print("변환 완료.")