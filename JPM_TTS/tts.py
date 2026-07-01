import os, re, glob
import httpx
import xml.sax.saxutils as saxutils

CHAPTERS_DIR = "chapters"
OUTPUT_DIR = "audio"
AZURE_KEY = "XXX"
AZURE_REGION = "eastus"
PROXY = "socks5://127.0.0.1:7890"
VOICE = "zh-CN-YunyangNeural"
CHUNK_SIZE = 800

ENDPOINT = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
client = httpx.Client(proxy=PROXY, timeout=120)

SSML_FORMAT = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <voice name="{voice}">
    {text}
  </voice>
</speak>"""

HEADERS = {
    "Ocp-Apim-Subscription-Key": AZURE_KEY,
    "Content-Type": "application/ssml+xml",
    "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
    "User-Agent": "JPM_TTS",
}

os.makedirs(OUTPUT_DIR, exist_ok=True)

chapter_files = sorted(glob.glob(os.path.join(CHAPTERS_DIR, "*.txt")))
print(f"找到 {len(chapter_files)} 个章节文件")

for chapter_file in chapter_files:
    basename = os.path.splitext(os.path.basename(chapter_file))[0]
    out_file = os.path.join(OUTPUT_DIR, f"{basename}.mp3")

    if os.path.exists(out_file):
        print(f"\n跳过已存在: {out_file}")
        continue

    with open(chapter_file, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = []
    i = 0
    while i < len(text):
        end = min(i + CHUNK_SIZE, len(text))
        if end < len(text):
            for sep in ["。", "？", "！", "；", "\n", "，"]:
                pos = text.rfind(sep, i, end)
                if pos > i + CHUNK_SIZE // 2:
                    end = pos + 1
                    break
        chunks.append(text[i:end])
        i = end

    print(f"\n===== {basename} 共 {len(chunks)} 段 =====")

    audio_files = []
    for i, chunk in enumerate(chunks):
        fn = f"_tmp_{i:03d}.mp3"
        esc_text = saxutils.escape(chunk)
        ssml = SSML_FORMAT.format(voice=VOICE, text=esc_text)

        print(f"  第 {i+1}/{len(chunks)} 段 ({len(chunk)} 字符)...")
        for attempt in range(3):
            try:
                resp = client.post(ENDPOINT, headers=HEADERS, content=ssml.encode("utf-8"))
                if resp.status_code == 200:
                    with open(fn, "wb") as f:
                        f.write(resp.content)
                    audio_files.append(fn)
                    break
                else:
                    print(f"    错误: {resp.status_code} - {resp.text[:200]}")
                    if resp.status_code >= 500 and attempt < 2:
                        import time
                        time.sleep(2)
                        continue
                    else:
                        print(f"    错误: {resp.status_code} - {resp.text[:200]}")
                        break
            except Exception as e:
                print(f"    异常: {e}")
                import time
                time.sleep(2)

    if audio_files:
        with open(out_file, "wb") as out:
            for fn in audio_files:
                with open(fn, "rb") as f:
                    out.write(f.read())
                os.remove(fn)
        print(f"  -> {out_file}")
    else:
        print(f"  未生成任何音频文件")