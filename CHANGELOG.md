# 更新履歴

このファイルの書き方は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) に、バージョンの付け方は [セマンティック バージョニング](https://semver.org/lang/ja/) に従います。

新しい変更は、まず「Unreleased」に書いてください。`python tools/bump_version.py <新しいバージョン>` を実行すると、「Unreleased」の内容が新しいバージョンの見出しの下に移ります。

## [Unreleased]

### Added

- レシピ `rainbow4`〜`rainbow8`、`sour1`・`sour2`

### Changed

- 同梱レシピを更新。全レシピの先頭にシミュレーター形式のコメント（ドーナツの種類・付く可能性のあるパワー、きのみと数）を記載
- 全レシピの `NAME` を「ドーナツの種類 きのみと数」に変更（例: `サワードーナツ ロゼル4,カシブ4`）
- `recipe1` の材料を変更（いじげんロゼル3・リリバ1・カシブ4 → いじげんロゼル4・カシブ4）
- ドキュメントのレシピ一覧（README、RECIPES_LIST、USER_CONFIG_GUIDE、USER_RECIPE_GUIDE、USER_CONDITIONS_GUIDE）を更新

## [2.1.0] - 2026-11-20

### Added

- 開始前の設定画面。Start を押すと開き、config.json の項目（レシピ、タイプ、サイズ、レベル、ほかくパワー、回数・リセット、タイミング、カスタム条件、しきい値）を選んでから実行する。選んだ内容は config.json に保存できる
- 予約・モニターからの開始用に、一定時間操作がなければ表示中の設定で自動的に開始する
- 設定項目 `show_settings_ui`、`settings_ui_timeout_seconds`
- `tools/bump_version.py`（バージョンの一括更新とずれのチェック）と、PR でずれを確認する GitHub Actions
- `CHANGELOG.md`（更新履歴を README から移動）

### Changed

- Poke-Controller Modified Extension 0.2.0 に対応（プレビューを受け取る、キャンセル時の後処理、Web 版・実行リストでは画面を出さない、テーマの色に合わせる）
- コマンド名を「ZA ドーナツ厳選 v2.1.0」に固定（設定によって名前が変わらない）
- 設定の読み込みを `apply_config()` にまとめ、開始時にテンプレート画像を読み直す
- README の見出しからバージョンを外し、バッジと版表示（自動更新）に変更
- ドキュメント: config.json の選択肢一覧（タイプの日本語名など）、設定画面の章を追加

### Fixed

- PCME 0.2.0 でコマンド一覧に表示されない問題（`NAME` を f 文字列から文字列リテラルに変更）
- どうぐ＋どっさりのとき、`enable_capture_power: true` だと成立しない問題（どうぐモードではほかくパワーを判定に使わない。ほかくパワーを含む tool_conditions も外す）
- PCME の標準テーマで、Windows 以外では設定画面の色名がエラーになる問題

## [2.0.0]

### Added

- 設定ファイル外部化機能
  - 全ての設定を `config.json` で管理可能に
  - メインロジック更新時の設定上書きを防止
  - 環境変数、config.json、デフォルト値の優先順位で設定を適用
- 昼夜切り替え機能
  - 指定時間間隔で自動的に昼夜を切り替え
  - イベールセンターへ移動して昼夜変更（現在時刻で自動判定）
  - backup_restart → 昼夜変更 → ベールへ移動 → ドーナツ作成再開のフローを実装
  - 設定項目 `day_night_interval` を追加（分単位）
- 設定ガイド `USER_CONFIG_GUIDE.md`（全設定項目の詳細説明と選択肢）

## [1.9.6]

### Added

- 連続マッチなし時のバックアップ再開機能
  - 指定秒数以上連続してドーナツの画像比較で引っかからない状態が続いたら、backup restartから再開
  - 設定項目 `SETTING_NO_MATCH_TIMEOUT_SECONDS`、環境変数 `NO_MATCH_TIMEOUT_SECONDS`
  - 0秒に設定すると機能を無効化

## [1.9.5]

### Added

- テンプレートの追加（`donut_conditions.json`）

## [1.9.4]

### Removed

- 重複機能の削除

## [1.9.3]

### Added

- 目標達成後ループ機能
  - 目標達成後にポケモンセンター（ベール）へ移動してセーブ
  - 最大ループ回数の設定（`SETTING_LOOP_AFTER_SUCCESS_MAX`）
  - 環境変数 `ENABLE_LOOP_AFTER_SUCCESS`、`LOOP_AFTER_SUCCESS_MAX`
- カスタム条件機能の拡張
  - 3パワー構造（power1, power2, power3）に対応
  - ほかくパワー（capture）、どうぐパワー（tool）、どっさりパワー（dosari）のテンプレートを追加
  - カスタム条件のテンプレート前提を明記（5種類）

### Removed

- カスタム条件へ移行した既存機能
  - タイプ不問オヤブン終了オプション（`SETTING_STOP_ON_ANY_TYPE_OYABUN`）
  - サイズ相互互換（`SETTING_CROSS_SIZE_OYABUN`, `SETTING_CROSS_SIZE_BIG`, `SETTING_CROSS_SIZE_SMALL`）
  - 道具クラス相互互換（`SETTING_CROSS_MATCH`）
  - どうぐパワー単独終了オプション（`SETTING_STOP_ON_TOOL_ONLY`）

### Fixed

- ほかくパワーのタイプチェック範囲の不整合（かがやきがAllの場合の挙動）
- カスタム条件で `attribute: null` の場合、全タイプをチェックするように修正

## [1.9.2]

### Fixed

- カスタム条件で `attribute: null` の場合、`Type_All` を優先的にチェックするように修正
- 複数の「かがやきパワー」がある場合、全てのマッチング位置をチェックするように修正

### Added

- カスタム条件チェック中のデバッグログ

## [1.9.1]

### Added

- カスタム条件機能（外部JSONファイルから条件を読み込んでドーナツを確保）
- モード別条件対応（shinyモードではかがやき×サイズ、toolモードではどうぐ×どっさり）
- 複数タイプ指定（`attribute: ["Fire", "Ground"]` 配列形式）
- `donut_conditions.json`

## [1.9.0]

### Added

- レシピの外部ファイル化（`recipes/` ディレクトリ内の `.py` ファイルから読み込み）
- ユーザー独自レシピの作成機能、レシピの自動検出
- `TARGETS` フィールド（レシピが対象とするもの: 色違い・どうぐパワー）
- `USER_RECIPE_GUIDE.md`

## [1.8.14] 以前

- 色違い厳選レシピ4 (shiny4) を追加
- recipe3レシピを追加
- デバッグ機能の修正
- エリア判定を追加

[Unreleased]: https://github.com/zephel01/ZA_donut_correct/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/zephel01/ZA_donut_correct/releases/tag/v2.1.0
