import os, re
import httpx
import xml.sax.saxutils as saxutils

TEXT_FILE = r"第一回：景阳冈武松打虎 潘金莲嫌夫卖风月.txt"
OUTPUT_FILE = "第一回：景阳冈武松打虎 潘金莲嫌夫卖风月_{voice}.mp3"
AZURE_KEY = "XXX"
AZURE_REGION = "eastus"
PROXY = "socks5://127.0.0.1:7890"
VOICES = [
    "zh-CN-YunxiNeural",
    "zh-CN-YunjianNeural",
    "zh-CN-YunyangNeural",
]
CHUNK_SIZE = 800  # Azure REST API 对 SSML 有限制

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

with open(TEXT_FILE, "r", encoding="utf-8") as f:
    text = f.read()

# Split text into chunks of ~CHUNK_SIZE characters, breaking at sentence boundaries
chunks = []
i = 0
while i < len(text):
    end = min(i + CHUNK_SIZE, len(text))
    if end < len(text):
        # Try to break at a sentence ending
        for sep in ["。", "？", "！", "；", "\n", "，"]:
            pos = text.rfind(sep, i, end)
            if pos > i + CHUNK_SIZE // 2:
                end = pos + 1
                break
    chunks.append(text[i:end])
    i = end

for VOICE in VOICES:
    short = VOICE.split("-")[-1].replace("Neural", "")
    out_file = OUTPUT_FILE.format(voice=short)
    print(f"\n===== {VOICE} ({short}) 共 {len(chunks)} 段 =====")

    audio_files = []
    for i, chunk in enumerate(chunks):
        fn = f"_tmp_{i:03d}.mp3"
        esc_text = saxutils.escape(chunk)
        ssml = SSML_FORMAT.format(voice=VOICE, text=esc_text)

        print(f"  第 {i+1}/{len(chunks)} 段 ({len(chunk)} 字符)...")
        resp = client.post(ENDPOINT, headers=HEADERS, content=ssml.encode("utf-8"))
        if resp.status_code != 200:
            print(f"    错误: {resp.status_code} - {resp.text[:200]}")
        else:
            with open(fn, "wb") as f:
                f.write(resp.content)
            audio_files.append(fn)

    if audio_files:
        with open(out_file, "wb") as out:
            for fn in audio_files:
                with open(fn, "rb") as f:
                    out.write(f.read())
                os.remove(fn)
        print(f"  -> {out_file}")
    else:
        print(f"  未生成任何音频文件")