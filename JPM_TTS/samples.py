import os
import httpx
import xml.sax.saxutils as saxutils

AZURE_KEY = open("AZURE_KEY").read()
AZURE_REGION = "eastus"
PROXY = "socks5://127.0.0.1:7890"
SAMPLE_TEXT = "话说大宋徽宗皇帝政和年间，朝中宠信高杨童蔡四个奸臣，以致天下大乱，黎民失业，百姓倒悬。"

VOICES = [
    "zh-CN-XiaoxiaoNeural",
    "zh-CN-YunxiNeural",
    "zh-CN-YunjianNeural",
    "zh-CN-XiaoyiNeural",
    "zh-CN-YunyangNeural",
    "zh-CN-XiaochenNeural",
    "zh-CN-XiaohanNeural",
]

ENDPOINT = f"https://{AZURE_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
HEADERS = {
    "Ocp-Apim-Subscription-Key": AZURE_KEY,
    "Content-Type": "application/ssml+xml",
    "X-Microsoft-OutputFormat": "audio-16khz-128kbitrate-mono-mp3",
    "User-Agent": "JPM_TTS",
}

SSML_FORMAT = """<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xml:lang="zh-CN">
  <voice name="{voice}">
    {text}
  </voice>
</speak>"""

client = httpx.Client(proxy=PROXY, timeout=60)

for voice in VOICES:
    short = voice.split("-")[-1].replace("Neural", "")
    fn = f"sample_{short}.mp3"
    print(f"生成 {voice} ...")
    esc = saxutils.escape(SAMPLE_TEXT)
    ssml = SSML_FORMAT.format(voice=voice, text=esc)
    resp = client.post(ENDPOINT, headers=HEADERS, content=ssml.encode("utf-8"))
    if resp.status_code == 200:
        with open(fn, "wb") as f:
            f.write(resp.content)
        print(f"  -> {fn}")
    else:
        print(f"  错误: {resp.status_code}")

print("全部完成")