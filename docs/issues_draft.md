# GitHub Issues 下書き

以下の Issue を GitHub 上で作成してください。

---

## Issue #1: [TDD] Anthropic API クライアントの基盤実装

### 概要
Anthropic Claude API と通信するクライアントクラスの実装（テストファースト）

### 対応する仕様
- [ ] FR番号: 基盤機能
- [ ] テスト仕様書の該当セクション: 7. Anthropic API 統合テスト

### テストケース (Red Phase)
```python
# tests/test_llm/test_anthropic_client.py
import pytest
from src.llm.anthropic_client import AnthropicClient

@pytest.mark.llm
def test_anthropic_client_initialization():
    """APIキーでクライアントを初期化できる"""
    client = AnthropicClient(api_key="test-key")
    assert client.api_key == "test-key"

@pytest.mark.llm
def test_anthropic_client_connection():
    """APIへの接続をテストできる"""
    client = AnthropicClient()
    response = client.test_connection()
    assert response.status == "connected"

@pytest.mark.llm  
def test_anthropic_prompt_execution():
    """プロンプトを実行して応答を得られる"""
    client = AnthropicClient()
    response = client.execute_prompt("Hello, Claude")
    assert len(response.content) > 0
```

### 実装チェックリスト
- [ ] 失敗するテストを作成
- [ ] AnthropicClient クラスの最小実装
- [ ] .env.example に ANTHROPIC_API_KEY を追加
- [ ] requirements.txt に anthropic を追加
- [ ] pytest.ini に llm マーカーを追加

---

## Issue #2: [TDD] プロンプト実行エンジンの実装 (FR1)

### 概要
プロンプトを LLM に送信し、結果を評価する基本エンジンの実装

### 対応する仕様  
- [ ] FR番号: FR1 (プロンプトの反復実行)
- [ ] テスト仕様書の該当セクション: 1. 基本的なプロンプト実行テスト

### テストケース (Red Phase)
```python
# tests/test_engine/test_prompt_executor.py
import re
from src.engine.prompt_executor import PromptExecutor

def test_simple_deterministic_output():
    """単純な決定論的出力のテスト"""
    executor = PromptExecutor()
    result = executor.execute_prompt("2+2=")
    
    assert re.match(r"^4$", result.final_output)
    assert result.iterations <= 3
    assert result.success is True
```

---

## Issue #3: [TDD] 自動入力注入機能の実装 (FR2)

### 概要
LLM がユーザ入力を要求した際に自動で応答を生成する機能

### 対応する仕様
- [ ] FR番号: FR2 (自動入力注入)  
- [ ] テスト仕様書の該当セクション: 2. 自動入力注入テスト

### テストケース (Red Phase)
```python
# tests/test_engine/test_input_generator.py
from src.engine.input_generator import InputGenerator
from src.engine.interaction_detector import InteractionDetector

def test_detect_input_request():
    """入力要求を検出できる"""
    detector = InteractionDetector()
    llm_output = "あなたの名前は何ですか？"
    
    assert detector.needs_input(llm_output) is True
    assert detector.extract_prompt(llm_output) == "あなたの名前は何ですか？"

def test_generate_auto_input():
    """適切な自動入力を生成できる"""
    generator = InputGenerator()
    response = generator.generate("名前を入力してください", ["太郎"])
    
    assert response == "太郎"
```

---

## Issue #4: [TDD] Web UI の基本実装 (FR7)

### 概要
シンプルな Web インターフェースの実装（FastAPI + HTMX）

### 対応する仕様
- [ ] FR番号: FR7 (シンプル Web UI の提供)
- [ ] テスト仕様書の該当セクション: 4. Web UI テスト

### テストケース (Red Phase)
```python
# tests/test_webui/test_app.py
from fastapi.testclient import TestClient
from src.webui.app import app

def test_web_ui_basic_display():
    """基本的なUI表示"""
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    assert "プロンプト入力" in response.text
    assert "結果表示" in response.text
```

---

## Issue #5: [TDD] エージェントペルソナ生成機能 (FR9)

### 概要
タスクに応じて評価用エージェントペルソナを自動生成する機能

### 対応する仕様
- [ ] FR番号: FR9 (エージェントペルソナ自動生成による評価)
- [ ] テスト仕様書の該当セクション: 6. エージェントペルソナテスト

### テストケース (Red Phase)
```python
# tests/test_agent/test_agent_generator.py
from src.agent.agent_generator import AgentGenerator

def test_agent_persona_generation():
    """ペルソナが正しく生成される"""
    generator = AgentGenerator()
    persona = generator.generate_persona("コードの可読性を改善")
    
    assert persona.role is not None
    assert persona.mindset is not None
    assert len(persona.operating_philosophy) >= 3
    assert len(persona.self_correction_protocol) >= 3
``` 