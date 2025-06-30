---
name: TDD Task
about: Test-Driven Development task template
title: "[TDD] "
labels: enhancement, test
assignees: ''

---

## 概要
<!-- このタスクで実装する機能の簡潔な説明 -->

## 対応する仕様
- [ ] FR番号: 
- [ ] テスト仕様書の該当セクション: 

## テストケース (Red Phase)
```python
# ここに失敗するテストコードを記載
```

## 期待される振る舞い
<!-- テストが通るために必要な機能の詳細 -->

## 実装チェックリスト
- [ ] 失敗するテストを作成
- [ ] 最小限の実装でテストを通す
- [ ] リファクタリング
- [ ] ドキュメント更新
- [ ] PR作成

## 受け入れ基準
- [ ] テストカバレッジ 90% 以上
- [ ] pytest 全体が green
- [ ] CI/CD パイプラインが通る 