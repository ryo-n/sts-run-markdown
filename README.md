# sts-run-markdown

Slay the SpireのランデータファイルをMarkdown形式に変換するPythonスクリプト

## 概要

このツールは、Slay the Spireの`.run`ファイル（JSON形式）を解析して、読みやすいMarkdown形式のレポートに変換します。日本語と英語の両言語に対応しており、全キャラクター（アイアンクラッド、サイレント、ディフェクト、ウォッチャー）のカード、レリック、ポーションの翻訳データを内蔵しています。

### 主な機能

- **全キャラクター対応**: アイアンクラッド、サイレント、ディフェクト、ウォッチャーの全カード翻訳
- **多言語対応**: 日本語・英語での出力
- **詳細なレポート**: 階層ごとの戦闘、カード選択、レリック取得、イベント等を記録
- **バッチ処理**: 複数ファイルの一括変換
- **自動化対応**: GitHub Actionsでの自動処理

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
uv run python json_to_markdown.py runs --lang ja

# 出力ディレクトリを指定する場合
uv run python json_to_markdown.py runs -o markdown_output --lang ja

# デッキの詳細内容も表示する場合
uv run python json_to_markdown.py runs --lang ja --show-deck-details

# 短縮オプション
uv run python json_to_markdown.py runs -o output -l ja -d
```

## オプション

- `--lang` / `-l`: 出力言語を指定 (`en` または `ja`、デフォルト: `en`)
- `--output-dir` / `-o`: 出力ディレクトリを指定 (デフォルト: `output`)
- `--show-deck-details` / `-d`: 各階層でデッキの詳細内容を表示

## 翻訳データ

以下のデータが日本語・英語で完全翻訳されています：

### カード
- **アイアンクラッド**: 全82枚（コモン・アンコモン・レア）
- **サイレント**: 全75枚（コモン・アンコモン・レア）
- **ディフェクト**: 全75枚（コモン・アンコモン・レア）
- **ウォッチャー**: 全75枚（コモン・アンコモン・レア）
- **無色カード**: 全カード対応

### レリック
- **スターター・コモン・アンコモン・レア・ボス・ショップ・イベント**: 全レリック対応

### その他
- ポーション、敵、イベント、UI要素等も翻訳対応

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

---

# sts-run-markdown (English)

A Python script that converts Slay the Spire run data files to Markdown format

## Overview

This tool parses Slay the Spire `.run` files (JSON format) and converts them into readable Markdown reports. It supports both Japanese and English languages and includes complete translation data for all characters (Ironclad, Silent, Defect, Watcher) including their cards, relics, and potions.

### Key Features

- **All Characters Supported**: Complete translations for Ironclad, Silent, Defect, and Watcher cards
- **Multi-language Support**: Output in Japanese or English
- **Detailed Reports**: Floor-by-floor combat, card choices, relic acquisitions, events, etc.
- **Batch Processing**: Convert multiple files at once
- **Automation Ready**: GitHub Actions support for automatic processing

## Libraries Used

### click
A library for creating user-friendly command-line interfaces (CLI) in Python. It provides decorator-based intuitive CLI tool construction with argument parsing, automatic help message generation, and validation features.

### rich
A library for creating beautiful formatted output in the terminal. It enables rich console output including colorful text, tables, progress bars, syntax highlighting, and Markdown display.

## Setup

```bash
uv sync
```

## Usage

```bash
# Process single directory (English)
uv run python json_to_markdown.py IRONCLAD

# Process multiple directories
uv run python json_to_markdown.py IRONCLAD THE_SILENT

# Process runs directory recursively (auto-detect characters)
uv run python json_to_markdown.py runs

# Output in Japanese
uv run python json_to_markdown.py runs --lang ja

# Specify output directory
uv run python json_to_markdown.py runs -o markdown_output --lang ja

# Show detailed deck contents
uv run python json_to_markdown.py runs --lang ja --show-deck-details

# Short options
uv run python json_to_markdown.py runs -o output -l ja -d
```

## Options

- `--lang` / `-l`: Specify output language (`en` or `ja`, default: `en`)
- `--output-dir` / `-o`: Specify output directory (default: `output`)
- `--show-deck-details` / `-d`: Show detailed deck contents at each floor

## Translation Data

The following data is fully translated in both Japanese and English:

### Cards
- **Ironclad**: All 82 cards (Common, Uncommon, Rare)
- **Silent**: All 75 cards (Common, Uncommon, Rare)
- **Defect**: All 75 cards (Common, Uncommon, Rare)
- **Watcher**: All 75 cards (Common, Uncommon, Rare)
- **Colorless Cards**: All cards supported

### Relics
- **Starter, Common, Uncommon, Rare, Boss, Shop, Event**: All relics supported

### Other
- Potions, enemies, events, UI elements, etc. are also translated

## GitHub Actions Automation

This repository includes a GitHub Actions workflow that automatically generates Markdown files when new `.run` files are added.

### Operation

1. Automatically triggered when `.run` files are added to:
   - `runs/`
   - `IRONCLAD/`
   - `THE_SILENT/`
   
2. Executes the following command:
   ```bash
   uv run python json_to_markdown.py runs -o output --lang ja -d
   ```
   
3. Commits generated Markdown files to the `output/` directory

### Manual Execution

Manual execution is also possible via the "Run workflow" button on the GitHub Actions page.

## License

This project is open source. Please feel free to use, modify, and distribute.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests for:
- Additional translation improvements
- New features
- Bug fixes
- Documentation improvements