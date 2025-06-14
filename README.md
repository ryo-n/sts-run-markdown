# json-to-markdown

JSONファイルを解析してMarkdown形式に変換するPythonスクリプト

## 使用ライブラリ

### click
Pythonで使いやすいコマンドラインインターフェース（CLI）を作成するためのライブラリです。デコレータベースで直感的にCLIツールを構築でき、引数解析、ヘルプメッセージ自動生成、バリデーション機能などを提供します。

### rich
ターミナルで美しいフォーマットされた出力を作成するライブラリです。カラフルなテキスト、テーブル、プログレスバー、シンタックスハイライト、Markdown表示など、リッチなコンソール出力を簡単に実現できます。

## セットアップ

```bash
uv sync
```

## 使い方

```bash
# 単一ディレクトリを処理（英語）
uv run python json_to_markdown.py IRONCLAD

# 複数ディレクトリを同時処理
uv run python json_to_markdown.py IRONCLAD THE_SILENT

# runsディレクトリを再帰的に処理（キャラクター自動判定）
uv run python json_to_markdown.py runs

# 日本語で出力する場合
uv run python json_to_markdown.py IRONCLAD THE_SILENT --lang ja

# 出力ディレクトリを指定する場合
uv run python json_to_markdown.py IRONCLAD THE_SILENT -o markdown_output --lang ja

# 短縮オプション
uv run python json_to_markdown.py IRONCLAD THE_SILENT -o output -l ja
```

## オプション

- `--lang` / `-l`: 出力言語を指定 (`en` または `ja`、デフォルト: `en`)
- `--output-dir` / `-o`: 出力ディレクトリを指定 (デフォルト: `output`)
- `--show-deck-details` / `-d`: 各階層でデッキの詳細内容を表示

## GitHub Actions 自動化

このリポジトリには、新しい`.run`ファイルが追加された際に自動的にMarkdownファイルを生成するGitHub Actionsワークフローが含まれています。

### 動作

1. 以下のディレクトリに`.run`ファイルが追加されると自動実行:
   - `runs/`
   - `IRONCLAD/`
   - `THE_SILENT/`
   
2. 以下のコマンドを実行:
   ```bash
   uv run python json_to_markdown.py runs -o output --lang ja -d
   ```
   
3. 生成されたMarkdownファイルを`output/`ディレクトリにコミット

### 手動実行

GitHub Actionsページから「Run workflow」ボタンで手動実行も可能です。