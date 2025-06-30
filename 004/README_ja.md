# プロンプト自動リファクタリングツール

自然言語プロンプトを用いてコードを自動リファクタリングするツールです。TDD（テスト駆動開発）手法で実装されています。

## 特徴

- **コード解析**: コード構造を解析し、リファクタリング候補を特定
- **リファクタリングエンジン**: さまざまなリファクタリング操作を適用
- **プロンプト処理**: 自然言語プロンプトを解釈してリファクタリング内容を決定
- **コード生成**: 整形済みで読みやすいコードを出力

## 対応リファクタリング

- メソッド／関数の抽出
- 変数／関数のリネーム
- 変数／関数のインライン化
- メソッド／クラスの移動
- デッドコード削除

## 対応言語

- Python（主要サポート）
- JavaScript（基本サポート）
- TypeScript（基本サポート）

## インストール

```bash
# リポジトリをクローン
cd 004

# 仮想環境作成
python3 -m venv venv
source venv/bin/activate  # Windows の場合: venv\Scripts\activate

# 依存関係をインストール
pip install -r requirements.txt

# パッケージをインストール（編集モード）
pip install -e .
```

## 使い方

### コマンドラインインターフェース

#### プロンプトでコードをリファクタリング
```bash
# ファイルを対象
refactor -f mycode.py -p "関数 'calc' を 'calculate' にリネーム"

# 標準入力を対象
echo "def calc(x, y): return x + y" | refactor -p "関数 'calc' を 'calculate' にリネーム"

# 対話モード
refactor -i -p "検証ロジックを抽出"
```

#### コード解析
```bash
# ファイルを解析
refactor analyze -f mycode.py

# 標準入力を解析
cat mycode.py | refactor analyze
```

#### インタラクティブセッション
```bash
refactor interactive
```

### Python API

```python
from src.main import PromptAutoRefactor

tool = PromptAutoRefactor()

# コードをリファクタリング
code = """
def calc(x, y):
    return x + y
"""

result = tool.refactor_code(code, "関数 'calc' を 'calculate' にリネーム")
print(result)

# コードを解析
analysis = tool.analyze_code(code)
print(f"関数数: {analysis['structure'].functions}")
print(f"提案: {[s.description for s in analysis['suggestions']]}")
```

## プロンプト例

- "関数 'calc' を 'calculate_sum' にリネーム"
- "5〜10 行目のバリデーションロジックを 'validate_data' メソッドに抽出"
- "変数 'temp' をインライン化"
- "Calculator クラスの 'add' メソッドを MathUtils クラスに移動"
- "未使用関数 helper1, helper2 を削除"

## プロジェクト構成

```
004/
├── src/
│   ├── analyzer/          # コード解析モジュール
│   ├── refactor/          # リファクタリングエンジン
│   ├── prompt/            # プロンプト処理
│   ├── generator/         # コード生成
│   └── main.py           # CLI インターフェース
├── tests/
│   ├── test_analyzer/
│   ├── test_refactor/
│   ├── test_prompt/
│   ├── test_generator/
│   └── test_integration.py
├── requirements.txt
├── pytest.ini
├── setup.py
└── README_ja.md
```

## 開発

### テスト実行

```bash
# すべてのテストを実行
pytest

# カバレッジ付き実行
pytest --cov=src

# 特定テストモジュール
pytest tests/test_analyzer/

# 統合テスト
pytest tests/test_integration.py
```

### テストカバレッジ

本プロジェクトは全モジュールで **90% 以上** のテストカバレッジを維持しています。

- コード解析: 90%+
- リファクタリングエンジン: 94%+
- プロンプト処理: 85%+
- コード生成: 85%+
- 統合テスト: 完全ワークフロー

### TDD 実装フロー

1. **Red**: 先に失敗するテストを書く
2. **Green**: 最小限の実装でテストを通す
3. **Refactor**: テストが通ったままリファクタリング

## アーキテクチャ

1. **Analyzer**: コード解析と改善候補抽出
2. **Prompt Processor**: 自然言語プロンプトの解釈
3. **Refactoring Engine**: コード変換の実施
4. **Generator**: 整形済みコードを出力

## コントリビュート

1. TDD 原則に従いテストを先に追加
2. テストカバレッジ 90%以上を維持
3. わかりやすいコミットメッセージ
4. 機能追加時はドキュメント更新

## ライセンス

MIT License - 詳細は LICENSE ファイルを参照してください。 