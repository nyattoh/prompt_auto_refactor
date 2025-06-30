# Prompt Auto Refactor

## 概要

このプロジェクトは、LLM（大規模言語モデル）の応答を自律的に評価しながらプロンプトを自動リファクタリングし、必要に応じて自動入力を生成して最終ゴールの出力を得るまで繰り返すシステムです。

- 仕様: `specification.yaml` 参照
- テスト仕様: `docs/test_specification.md` 参照
- 日本語README: `README_ja.md`

## ディレクトリ構成

```
project_root/
├── src/                 # ソースコード
│   └── llm/             # LLMクライアント等
├── tests/               # テストコード
│   └── test_llm/        # LLMクライアントのテスト
├── docs/                # ドキュメント
├── env.example          # 環境変数サンプル
├── requirements.txt     # Python依存パッケージ
├── pytest.ini           # pytest設定
├── README.md            # 英語README
├── README_ja.md         # 日本語README
├── specification.yaml   # 仕様書
└── ...
```

## セットアップ

1. Python 3.10+ をインストール
2. 仮想環境の作成・有効化
   ```sh
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. 依存パッケージのインストール
   ```sh
   pip install -r requirements.txt
   ```
4. `.env` ファイルを作成し、Anthropic APIキー等を設定
   ```sh
   cp env.example .env
   # .envを編集して ANTHROPIC_API_KEY などを記入
   ```

## Anthropic API キーの設定

`.env` または環境変数で以下を設定してください:

```
ANTHROPIC_API_KEY=sk-xxxxxxx
ANTHROPIC_MODEL=claude-3-sonnet-20240229  # 任意
ANTHROPIC_MAX_TOKENS=4096                # 任意
```

## テスト実行

```sh
pytest -v
# LLM実APIテストを除外: pytest -v -m "not llm"
# カバレッジ計測: pytest --cov=src --cov-report=term-missing
```

## CI/CD (GitHub Actions)

`.github/workflows/python.yml` を作成し、以下の内容でCIを有効化できます:

```yaml
name: Python package

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest -v -m "not llm"
    - name: Report coverage
      run: |
        pytest --cov=src --cov-report=term-missing -m "not llm"
```

- LLM実APIテスト（`@pytest.mark.llm`）はCIでは除外しています。
- Secretsに `ANTHROPIC_API_KEY` を登録すれば、実APIテストも可能です。

## Issueテンプレート

`.github/ISSUE_TEMPLATE/tdd-task.md` を利用してTDDタスク管理ができます。

---

## License
MIT