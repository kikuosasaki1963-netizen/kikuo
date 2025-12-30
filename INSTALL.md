# Voice Generator インストール手順

## 必要なもの
- Python 3.11
- ffmpeg
- Gemini APIキー

---

## Windows

### 1. Python 3.11 インストール
https://www.python.org/downloads/release/python-3119/
から「Windows installer (64-bit)」をダウンロードしてインストール

**重要:** インストール時に「Add Python to PATH」にチェック

### 2. ffmpeg インストール
https://www.gyan.dev/ffmpeg/builds/
から「ffmpeg-release-essentials.zip」をダウンロード

1. 解凍して `C:\ffmpeg` に配置
2. 環境変数PATHに `C:\ffmpeg\bin` を追加

### 3. プロジェクト取得
```cmd
git clone https://github.com/kikuosasaki1963-netizen/kikuo.git
cd kikuo
```

または、GitHubからZIPダウンロードして解凍

### 4. 依存関係インストール
```cmd
pip install -r requirements.txt
```

### 5. APIキー設定
1. https://aistudio.google.com/app/apikey でAPIキーを取得
2. `.env.example` を `.env` にコピー
3. `.env` を編集してAPIキーを設定:
```
GEMINI_API_KEY=あなたのAPIキー
```

### 6. 実行
```cmd
streamlit run app.py
```

ブラウザで http://localhost:8501 が開きます

---

## Mac

### 1. Homebrew インストール（未導入の場合）
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Python と ffmpeg インストール
```bash
brew install python@3.11 ffmpeg
```

### 3. プロジェクト取得
```bash
git clone https://github.com/kikuosasaki1963-netizen/kikuo.git
cd kikuo
```

### 4. 依存関係インストール
```bash
pip3 install -r requirements.txt
```

### 5. APIキー設定
1. https://aistudio.google.com/app/apikey でAPIキーを取得
2. `.env.example` を `.env` にコピー:
```bash
cp .env.example .env
```
3. `.env` を編集してAPIキーを設定

### 6. 実行
```bash
streamlit run app.py
```

---

## 使い方

1. ブラウザで http://localhost:8501 を開く
2. テキスト入力またはWordファイルをアップロード
3. 「音声を生成」ボタンをクリック
4. 完了後、再生またはダウンロード

### 対応フォーマット
```
speaker1: こんにちは
speaker2: お元気ですか？

話者1: こんにちは
話者2: お元気ですか？

[話者1]: こんにちは
[話者2]: お元気ですか？
```

---

## トラブルシューティング

### 「APIキーが設定されていません」
→ `.env` ファイルが正しく作成されているか確認

### ffmpeg not found
→ ffmpegがPATHに含まれているか確認
```cmd
ffmpeg -version
```

### ModuleNotFoundError
→ 依存関係を再インストール
```cmd
pip install -r requirements.txt
```
