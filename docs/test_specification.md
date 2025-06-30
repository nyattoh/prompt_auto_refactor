# プロンプト自動リファクタリングツール テスト仕様書

## 概要
本書は `specification.yaml` で定義された機能要件(FR)に対応するテスト仕様を定義します。
TDD原則に従い、実装前にテストケースを明確化します。

## テスト環境
- LLM API: Anthropic Claude API
- テストフレームワーク: pytest
- モック/録画: pytest-vcr または responses
- CI: GitHub Actions

## テストケース一覧

### 1. 基本的なプロンプト実行テスト (FR1)

#### TEST-BASIC-01: 単純な決定論的出力
```python
def test_simple_deterministic_output():
    """
    仕様: specification.yaml TEST-01
    目的: FR1 (プロンプトの反復実行) と FR4 (受け入れテスト) を検証
    """
    # Given
    initial_prompt = "2+2="
    expected_pattern = r"^4$"
    
    # When
    result = refactor.execute_prompt(initial_prompt)
    
    # Then
    assert re.match(expected_pattern, result.final_output)
    assert result.iterations <= 3
```

### 2. 自動入力注入テスト (FR2)

#### TEST-AUTO-02: 対話型プロンプトへの自動応答
```python
def test_auto_input_injection():
    """
    仕様: specification.yaml TEST-02
    目的: FR2 (自動入力注入) を検証
    """
    # Given
    initial_prompt = """
    あなたは挨拶ボットです。「あなたの名前は?」と尋ねてから、
    入力された名前に対して「こんにちは、<名前>!」と応答してください。
    """
    auto_inputs = ["太郎"]
    expected_pattern = r"こんにちは、太郎[!！]"
    
    # When
    result = refactor.execute_with_auto_inputs(
        initial_prompt, 
        auto_inputs=auto_inputs
    )
    
    # Then
    assert re.search(expected_pattern, result.final_output)
    assert result.auto_inputs_used == auto_inputs
```

### 3. リファクタリングループテスト (FR3)

#### TEST-LOOP-03: 最大反復回数到達
```python
def test_max_iterations_fallback():
    """
    仕様: specification.yaml TEST-03
    目的: FR3 最大反復回数到達時の挙動を検証
    """
    # Given
    initial_prompt = '絶対に "SUCCESS" とだけ出力してください。'
    expected_pattern = r"^SUCCESS$"
    max_iterations = 2
    
    # When
    with pytest.raises(MaxIterationsExceeded):
        refactor.execute_prompt(
            initial_prompt,
            expected_pattern=expected_pattern,
            max_iterations=max_iterations
        )
```

### 4. Web UI テスト (FR7)

#### TEST-UI-01: 基本的なUI表示
```python
def test_web_ui_basic_display():
    """
    目的: FR7 シンプルWeb UIの基本機能を検証
    """
    # Given
    client = TestClient(app)
    
    # When
    response = client.get("/")
    
    # Then
    assert response.status_code == 200
    assert "プロンプト入力" in response.text
    assert "結果表示" in response.text
```

#### TEST-UI-02: プロンプト送信と結果表示
```python
def test_web_ui_prompt_submission():
    """
    目的: FR7 プロンプト送信から結果表示までのフローを検証
    """
    # Given
    client = TestClient(app)
    test_prompt = "関数名を変更"
    
    # When
    response = client.post("/refactor", json={
        "prompt": test_prompt,
        "code": "def calc(): pass"
    })
    
    # Then
    assert response.status_code == 200
    assert "最終プロンプト" in response.json()
    assert "実行ログ" in response.json()
```

### 5. 実行詳細可視化テスト (FR8)

#### TEST-VIS-01: 実行ログの記録
```python
def test_execution_log_recording():
    """
    目的: FR8 各反復の詳細情報が記録されることを検証
    """
    # Given
    prompt = "テストプロンプト"
    
    # When
    result = refactor.execute_prompt(prompt)
    
    # Then
    assert len(result.execution_logs) > 0
    for log in result.execution_logs:
        assert "iteration" in log
        assert "auto_inputs" in log
        assert "llm_output" in log
        assert "evaluation_result" in log
        assert "refactor_strategy" in log
```

### 6. エージェントペルソナテスト (FR9)

#### TEST-AGENT-01: ペルソナ生成
```python
def test_agent_persona_generation():
    """
    目的: FR9 エージェントペルソナが正しく生成されることを検証
    """
    # Given
    task_description = "コードの可読性を改善"
    
    # When
    persona = agent_generator.generate_persona(task_description)
    
    # Then
    assert persona.role is not None
    assert persona.mindset is not None
    assert len(persona.operating_philosophy) >= 3
    assert len(persona.self_correction_protocol) >= 3
```

#### TEST-AGENT-02: ペルソナによる評価
```python
def test_agent_persona_evaluation():
    """
    目的: FR9 生成されたペルソナが評価を実行できることを検証
    """
    # Given
    persona = agent_generator.generate_persona("品質評価")
    output = "def calculate(): return 42"
    
    # When
    evaluation = persona.evaluate(output)
    
    # Then
    assert evaluation.score is not None
    assert evaluation.feedback is not None
    assert evaluation.improvement_suggestions is not None
```

### 7. Anthropic API 統合テスト

#### TEST-ANTHROPIC-01: API接続確認
```python
@pytest.mark.llm
def test_anthropic_api_connection():
    """
    目的: Anthropic APIへの接続を確認
    """
    # Given
    client = AnthropicClient()
    
    # When
    response = client.test_connection()
    
    # Then
    assert response.status == "connected"
```

#### TEST-ANTHROPIC-02: プロンプト実行
```python
@pytest.mark.llm
def test_anthropic_prompt_execution():
    """
    目的: Anthropic APIでプロンプトが実行できることを確認
    """
    # Given
    prompt = "Hello, Claude"
    
    # When
    response = client.execute_prompt(prompt)
    
    # Then
    assert len(response.content) > 0
```

## テスト実行計画

### Phase 1: ユニットテスト
```bash
pytest -m "not llm" --cov=src
```

### Phase 2: LLMテスト（録画モード）
```bash
pytest -m llm --vcr-record=once
```

### Phase 3: 統合テスト
```bash
pytest tests/test_integration.py
```

## CI/CD 設定

### GitHub Actions ワークフロー
```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: pytest -m "not llm"
  
  llm-tests:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Run LLM tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: pytest -m llm
```

## 受け入れ基準

各テストケースは以下の基準を満たすこと：
1. 明確な Given-When-Then 構造
2. 単一の機能/振る舞いをテスト
3. 独立して実行可能
4. 決定論的な結果（LLMテストは録画で対応） 