"""Voice Generator Web App - Streamlit (No pydub)"""
import os
import re
import wave
import tempfile
import struct
import streamlit as st
from google import genai
from google.genai import types
from docx import Document
import io
import subprocess

# ページ設定
st.set_page_config(
    page_title="Voice Generator",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ Voice Generator")
st.write("対話スクリプトから感情豊かな音声を生成します")

# APIキー設定（Secretsから取得）
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

if not GEMINI_API_KEY:
    st.error("APIキーが設定されていません。Streamlit CloudのSecretsにGEMINI_API_KEYを設定してください。")
    st.stop()

# クライアント初期化
@st.cache_resource
def get_client():
    return genai.Client(api_key=GEMINI_API_KEY)

client = get_client()

# スクリプト解析
def parse_dialogue(content):
    segments = []

    # 様々な形式を統一フォーマットに変換
    # Speaker 1/2 → 話者1/2
    content = content.replace('Speaker 1:', '[話者1]:')
    content = content.replace('Speaker 2:', '[話者2]:')

    # （話者1）や（話者２）→ [話者1]
    content = re.sub(r'（(話者\d+)）[:：]?\s*', r'[\1]: ', content)
    content = re.sub(r'\((話者\d+)\)[:：]?\s*', r'[\1]: ', content)

    # 全角数字を半角に変換
    content = content.replace('１', '1').replace('２', '2').replace('３', '3')
    content = content.replace('４', '4').replace('５', '5')

    # 話者1: や 話者2: （括弧なし）→ [話者1]:
    content = re.sub(r'(?<!\[)(話者\d+)[:：]\s*', r'[\1]: ', content)

    # A: B: などのアルファベット話者
    content = re.sub(r'^([A-Za-z])[:：]\s*', r'[\1]: ', content, flags=re.MULTILINE)

    # 複数のパターンに対応
    pattern = r'\[(話者\d+|[^\]]+)\][:：]?\s*(.+)'
    for match in re.finditer(pattern, content):
        speaker = match.group(1).strip()
        text = match.group(2).strip()
        if text:
            segments.append({"speaker": speaker, "text": text})
    return segments

# Wordファイル読み込み
def read_word_file(uploaded_file):
    doc = Document(io.BytesIO(uploaded_file.read()))
    text = '\n'.join([p.text for p in doc.paragraphs])

    # Speaker 1/2 を 話者1/2 に変換
    text = text.replace('Speaker 1:', '[話者1]:')
    text = text.replace('Speaker 2:', '[話者2]:')

    # 複数行のセリフを1行にまとめる
    lines = text.split('\n')
    result = []
    current_speaker = None
    current_text = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = re.match(r'\[(話者\d+)\]:\s*(.*)', line)
        if match:
            if current_speaker and current_text:
                combined = ' '.join(current_text)
                combined = re.sub(r'\*\*', '', combined)
                combined = re.sub(r'\([^)]*\)', '', combined)
                result.append(f'[{current_speaker}]: {combined}')

            current_speaker = match.group(1)
            current_text = [match.group(2)] if match.group(2) else []
        elif current_speaker:
            if not line.startswith('(') and not line.startswith('■') and not line.startswith('【'):
                current_text.append(line)

    if current_speaker and current_text:
        combined = ' '.join(current_text)
        combined = re.sub(r'\*\*', '', combined)
        result.append(f'[{current_speaker}]: {combined}')

    return '\n'.join(result)

# WAVファイル結合（pydub不要）
def combine_wav_files(wav_files, output_path):
    """Combine multiple WAV files into one."""
    if not wav_files:
        return

    # 最初のファイルからパラメータを取得
    with wave.open(wav_files[0], 'rb') as first:
        params = first.getparams()

    # 無音データ（300ms）
    silence_frames = int(params.framerate * 0.3) * params.nchannels * params.sampwidth
    silence = b'\x00' * silence_frames

    # 全ファイルを結合
    with wave.open(output_path, 'wb') as output:
        output.setparams(params)
        for wav_file in wav_files:
            with wave.open(wav_file, 'rb') as w:
                output.writeframes(w.readframes(w.getnframes()))
            output.writeframes(silence)

# WAVをMP3に変換
def wav_to_mp3(wav_path, mp3_path):
    """Convert WAV to MP3 using ffmpeg."""
    try:
        subprocess.run(
            ['ffmpeg', '-y', '-i', wav_path, '-codec:a', 'libmp3lame', '-q:a', '2', mp3_path],
            capture_output=True,
            check=True
        )
        return True
    except:
        return False

# 音声生成
def generate_audio(segments, progress_bar, status_text):
    speakers = list(set(seg["speaker"] for seg in segments))
    female_voices = ["Aoede", "Kore", "Leda", "Zephyr"]
    male_voices = ["Charon", "Puck", "Orus", "Fenrir"]

    speaker_voices = {}
    speaker_styles = {}

    for i, speaker in enumerate(sorted(speakers)):
        if i % 2 == 0:
            speaker_voices[speaker] = female_voices[i // 2 % len(female_voices)]
            speaker_styles[speaker] = "as an expressive young woman speaking Japanese"
        else:
            speaker_voices[speaker] = male_voices[i // 2 % len(male_voices)]
            speaker_styles[speaker] = "as a calm knowledgeable expert speaking Japanese"

    temp_files = []
    temp_dir = tempfile.mkdtemp()

    for i, segment in enumerate(segments):
        speaker = segment["speaker"]
        text = segment["text"]
        voice = speaker_voices.get(speaker, "Kore")
        style = speaker_styles.get(speaker, "")

        prompt = f"Say {style}: {text}" if style else text

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-preview-tts",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice,
                            )
                        )
                    ),
                ),
            )

            audio_data = response.candidates[0].content.parts[0].inline_data.data
            temp_path = os.path.join(temp_dir, f"segment_{i}.wav")

            with wave.open(temp_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(24000)
                wf.writeframes(audio_data)

            temp_files.append(temp_path)

            progress_bar.progress((i + 1) / len(segments))
            status_text.text(f"生成中: {i+1}/{len(segments)} - {speaker}: {text[:30]}...")

        except Exception as e:
            st.error(f"エラー: {e}")

    # 音声を結合
    status_text.text("音声を結合中...")
    combined_wav = os.path.join(temp_dir, "combined.wav")
    combine_wav_files(temp_files, combined_wav)

    # MP3に変換
    combined_mp3 = os.path.join(temp_dir, "output.mp3")
    if wav_to_mp3(combined_wav, combined_mp3):
        with open(combined_mp3, 'rb') as f:
            output_buffer = io.BytesIO(f.read())
    else:
        # MP3変換失敗時はWAVを返す
        with open(combined_wav, 'rb') as f:
            output_buffer = io.BytesIO(f.read())

    output_buffer.seek(0)

    # 長さを計算
    with wave.open(combined_wav, 'rb') as w:
        duration = w.getnframes() / w.getframerate()

    # 一時ファイル削除
    for f in temp_files:
        try:
            os.remove(f)
        except:
            pass
    try:
        os.remove(combined_wav)
        os.remove(combined_mp3)
        os.rmdir(temp_dir)
    except:
        pass

    return output_buffer, duration

# 入力方法選択
st.subheader("📝 スクリプト入力")
input_method = st.radio(
    "入力方法を選択",
    ["テキスト直接入力", "Wordファイルアップロード"],
    horizontal=True
)

script = ""

if input_method == "Wordファイルアップロード":
    uploaded_file = st.file_uploader("Wordファイル (.docx)", type=["docx"])
    if uploaded_file:
        script = read_word_file(uploaded_file)
        st.success(f"ファイル読み込み完了!")
        with st.expander("読み込んだスクリプト"):
            st.text(script[:1000] + "..." if len(script) > 1000 else script)
else:
    script = st.text_area(
        "スクリプトを入力",
        height=200,
        placeholder="""[話者1]: こんにちは
[話者2]: お元気ですか？
[話者1]: はい、元気です"""
    )

# 生成ボタン
if st.button("🎙️ 音声を生成", type="primary", use_container_width=True):
    if not script:
        st.error("スクリプトを入力してください")
    else:
        segments = parse_dialogue(script)

        if not segments:
            st.error("対話が見つかりません。形式を確認してください。")
            st.info("形式: [話者1]: セリフ")
        else:
            st.info(f"セグメント数: {len(segments)}")

            progress_bar = st.progress(0)
            status_text = st.empty()

            audio_buffer, duration = generate_audio(segments, progress_bar, status_text)

            status_text.text("")
            st.success(f"✅ 完了! (長さ: {int(duration // 60)}分{int(duration % 60)}秒)")

            # 再生
            st.audio(audio_buffer, format="audio/mp3")

            # ダウンロード
            st.download_button(
                label="📥 ダウンロード",
                data=audio_buffer,
                file_name="output.mp3",
                mime="audio/mp3",
                use_container_width=True
            )
