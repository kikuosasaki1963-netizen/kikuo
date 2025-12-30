# Voice Generation Agent

ドキュメントからナレーション音声を生成し、動画用音声トラックを作成するCLIエージェント。

## 機能

- **ドキュメント変換**: Word (.docx) / テキストファイルから音声を生成
- **Google Docs対応**: GoogleドキュメントIDから直接音声を生成
- **対話形式生成**: 複数話者によるスクリプトから対話音声を生成
- **ナレーション生成**: マークダウン/テキストから章ごとにナレーション生成
- **音声トラック作成**: BGM付きの動画用音声トラックを作成

## 必要条件

- Python 3.9以上
- FFmpeg
- Google Cloud アカウント（Text-to-Speech API有効化済み）

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd voice-generation-agent
```

### 2. Python仮想環境の作成（推奨）

```bash
# 仮想環境を作成
python3 -m venv venv

# 仮想環境を有効化
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 3. 依存関係のインストール

```bash
# pipでインストール
pip install -r requirements.txt

# または、パッケージとしてインストール
pip install .
```

### 4. FFmpegのインストール

音声処理（pydub）にFFmpegが必要です。

```bash
# macOS (Homebrew)
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg

# Windows (winget)
winget install ffmpeg
```

### 5. Google Cloud 認証設定

#### Text-to-Speech API（必須）

1. [Google Cloud Console](https://console.cloud.google.com/) でプロジェクトを作成
2. 「APIとサービス」→「ライブラリ」から「Cloud Text-to-Speech API」を有効化
3. 「APIとサービス」→「認証情報」→「サービスアカウントを作成」
4. サービスアカウントのキー（JSON）をダウンロード
5. ダウンロードしたJSONファイルを安全な場所に保存

#### Google Docs API（オプション）

Googleドキュメントから直接読み取る場合に必要：

1. Google Cloud Consoleで「Google Docs API」を有効化
2. OAuth 2.0 認証情報を作成
3. リフレッシュトークンを取得

### 6. 環境変数の設定

```bash
# .env.exampleを.envにコピー
cp .env.example .env
```

`.env` ファイルを編集:

```env
# 必須: Google Cloud Text-to-Speech
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-service-account.json

# オプション: Google Docs API
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REFRESH_TOKEN=your-refresh-token

# オプション: デフォルト設定
DEFAULT_VOICE=ja-JP-Neural2-B
DEFAULT_LANGUAGE=ja-JP
DEFAULT_SPEED=1.0
```

### 7. 動作確認

```bash
# バージョン確認
voice-agent version

# 利用可能な音声一覧（API接続テスト）
voice-agent voices --lang ja-JP
```

## 使用方法

### ドキュメント変換

```bash
# Wordファイルを音声に変換
voice-agent convert document.docx -o output.mp3

# テキストファイルを変換（オプション指定）
voice-agent convert document.txt -o output.mp3 --voice ja-JP-Neural2-B --speed 1.2
```

### Google Docs変換

```bash
# ドキュメントIDはURLの/d/以降の部分
voice-agent google-doc <document-id> -o output.mp3
```

### 対話形式生成

スクリプト形式（`script.txt`）:
```
[話者A]: こんにちは
[話者B]: お元気ですか？
[話者A]: はい、元気です。
```

実行:
```bash
voice-agent dialogue script.txt -o dialogue.mp3
```

### ナレーション生成

```bash
# 単一ファイル出力
voice-agent narrate narration.md -o narration.mp3

# 章ごとに分割出力
voice-agent narrate narration.md -o narration.mp3 --split-chapters
```

### 音声トラック作成

```bash
# BGMなし
voice-agent track script.txt -o track.mp3

# BGM付き
voice-agent track script.txt -o track.mp3 --bgm background.mp3 --bgm-volume -15
```

### 利用可能な音声一覧

```bash
# 全音声
voice-agent voices

# 日本語のみ
voice-agent voices --lang ja-JP
```

## スクリプト形式

### 対話形式

以下の形式に対応:
```
[話者名]: セリフ
【話者名】: セリフ
話者名: セリフ
```

### ナレーション形式（マークダウン）

```markdown
## セクション1
テキスト...

## セクション2
テキスト...
```

## トラブルシューティング

### FFmpegが見つからない

```
RuntimeWarning: Couldn't find ffmpeg or avconv
```

→ FFmpegをインストールしてください（上記セットアップ手順4を参照）

### 認証エラー

```
google.auth.exceptions.DefaultCredentialsError
```

→ `GOOGLE_APPLICATION_CREDENTIALS` 環境変数が正しく設定されているか確認

### Python バージョンエラー

```
requires a different Python
```

→ Python 3.9以上を使用してください

## ライセンス

MIT License
