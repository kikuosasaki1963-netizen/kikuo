# Voice Agent クイックスタート

## 設定完了後の使用方法

ターミナルを**新しく開く**か、以下を実行:
```bash
source ~/.zshrc
```

## 基本コマンド（短縮エイリアス `va`）

### 1. テキストを音声に変換
```bash
# 簡単な例
va convert 文書.txt -o 音声.mp3

# Wordファイルから
va convert 資料.docx -o output.mp3
```

### 2. 対話形式スクリプト
スクリプトファイル（例: `script.txt`）:
```
[話者A]: こんにちは
[話者B]: お元気ですか？
[話者A]: はい、元気です。
```

実行:
```bash
va dialogue script.txt -o dialogue.mp3
```

### 3. ナレーション生成
```bash
va narrate narration.md -o narration.mp3
```

### 4. 利用可能な音声を確認
```bash
# 日本語音声一覧
va voices --lang ja-JP

# 英語音声一覧
va voices --lang en-US
```

### 5. オプション指定
```bash
# 音声を指定
va convert 文書.txt -o output.mp3 --voice ja-JP-Neural2-B

# 話速を変更（0.5〜2.0）
va convert 文書.txt -o output.mp3 --speed 1.2
```

## おすすめ音声

| タイプ | 音声名 | 説明 |
|--------|--------|------|
| 女性（自然） | ja-JP-Neural2-B | 自然な女性音声 |
| 男性（自然） | ja-JP-Neural2-C | 自然な男性音声 |
| 女性（高品質） | ja-JP-Chirp3-HD-Aoede | HD品質女性音声 |
| 男性（高品質） | ja-JP-Chirp3-HD-Achird | HD品質男性音声 |

## トラブルシューティング

### コマンドが見つからない
```bash
source ~/.zshrc
```

### 認証エラー
```bash
# 認証ファイルを確認
ls ~/.config/gcloud/voice-agent-key.json
```
