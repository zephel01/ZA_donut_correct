# スクリプトガイド（本体・補助スクリプト・Poke-Controller 連携）

このフォルダに含まれる Python スクリプトの役割と、Poke-Controller での使い方をまとめます。

---

## スクリプト一覧

| ファイル | コマンド名（Poke-Controller 上の表示） | 用途 | config.json の使用 |
|---|---|---|---|
| `ZA_donut_correct.py` | `ZA ドーナツ厳選 (…) v2.0.0` | ドーナツ厳選の本体 | ✅ 使う |
| `ZA_backupRestart.py` | `ZA_BackupRestart` | ソフトの終了→再起動→セーブデータ読み込みだけを行う | ❌ 使わない |
| `ZA_day_night.py` | `ZA_DayNightCheck` | イベールセンターへ移動してベンチに座り、ゲーム内の時間帯を画像で確認する | ❌ 使わない |

3つとも Poke-Controller の **Python コマンド**として動きます。単体で `python ZA_donut_correct.py` のように実行することはできません（`Commands.PythonCommandBase` などの Poke-Controller のモジュールが必要です）。

---

## 動作環境と配置

```
Poke-Controller-Modified-Extension/
└── SerialController/
    └── Commands/
        └── PythonCommands/
            └── ZA_donut_correct/      ← このフォルダごと配置
```

- 必要なもの: Poke-Controller Modified Extension、キャプチャボード、マイコン（Switch 操作用）
- Python ライブラリ: `opencv-python`、`numpy`（Poke-Controller の動作環境に含まれます）
- 画像の参照先・設定ファイル・レシピ・条件ファイルは、いずれも**スクリプトのあるフォルダを基準**に探します。フォルダ名を変えても動きます。
- 例外として、`debug_captures/`（判定時の画面保存先）は **Poke-Controller の実行時カレントディレクトリ**に作られます。

---

## 実行前のゲーム内状態（本体）

`ZA_donut_correct.py` は次の状態から開始してください。

1. **ドーナツを作れる場所でセーブ済み**であること（リセット時はこのセーブ地点に戻ります）
2. フィールド上でメニューを開ける状態であること
3. 使うレシピの食材を十分な数持っていること

ドーナツを作るたびにメニュー→マップを開き、エリア表示が「すべて」か（`area_all.png`）を確認します。違う場合は自動で切り替えます。

---

## 本体の処理の流れ

```
起動（config.json・レシピ・条件ファイル・画像の読み込み）
 └ ループ（最大 max_loop 回）
    ├ [day_night_interval 経過?] → リセット → イベールセンター → ベールでセーブ → 次のループへ
    ├ ドーナツ作成（メニュー → 食材選択 → レシピ入力 → 調理 → 結果画面）
    ├ 判定 ── 成功 → 画面保存 →（目標達成後ループが有効ならベールでセーブして続行／無効なら終了）
    ├ 失敗 → リトライ（retry_limit 回、リセットせずに作り直す）
    ├ [no_match_timeout_seconds 経過?] → リセット → 次のループへ
    └ リトライでも失敗 → リセット（backupRestart）
```

各処理の設定は [USER_CONFIG_GUIDE.md](USER_CONFIG_GUIDE.md) を参照してください。

---

## ZA_backupRestart.py（リセット＆復帰）

本体のリセット処理（backupRestart）だけを単独で実行するスクリプトです。ボタン操作のタイミングが自分の環境で合っているかを確かめるときに使います。

**操作内容**

| 手順 | 操作 | 待機 |
|---|---|---|
| 1 | HOME | 1.5秒 |
| 2 | Y（ソフトを終了） | 1.0秒 |
| 3 | A（終了を確定） | 3.0秒 |
| 4 | A ×6（ソフトを起動、注意画面を送る） | 0.5秒間隔 |
| 5 | タイトル画面まで待機 | 10秒 |
| 6 | ↑＋X＋B 同時押し（バックアップデータから再開） | 1.0秒 |
| 7 | A ×12（読み込みを送る） | 0.4秒間隔 |
| 8 | ゲームに戻るまで待機 | 10秒 |

- このスクリプトの待機時間は**本体の `timing_mode: switch2` と同じ**です。本体を `switch1` で使う場合は、手順5と手順8の待機がそれぞれ 17秒・15秒に延びます。
- config.json は読み込みません。待機時間を変えたいときはスクリプトを直接編集してください。

---

## ZA_day_night.py（イベールセンター移動＋時間帯確認）

イベールセンターへ移動してベンチに座り、その後の**ゲーム内の時間帯（昼/夜）を画像で判定**するスクリプトです。昼夜切り替えの移動ルートと、`time_day.png` / `time_night.png` の認識精度を確かめるために使います。

**処理内容**

1. メニュー → マップ → 移動先を選んでイベールセンターへ移動
2. 左・上に移動してベンチに座る（A ×6）
3. 画面を `time_day.png` / `time_night.png` と照合し、スコアが高い方を現在の時間帯として表示

**ログの例**

```
昼スコア: 0.912
夜スコア: 0.431
★★★ 昼と判定しました
★★★ ゲーム内時間帯: 昼 ★★★
```

**注意**

- 2つの画像が無い場合、そのスコアは 0 になります。両方とも無いと必ず「昼」と判定されます。
- スクリプト内には目標の時間帯になるまで座り直す関数（`smooth_day_night_change`）もありますが、`do()` からは呼ばれていません（確認のみ）。
- 本体の昼夜切り替えは、ベンチに座る操作のあと**画像で確認しません**。本体とこのスクリプトでは、移動直後の待機時間も違います（本体 4.0秒、このスクリプト 2.5秒）。

---

## Poke-Controller のコマンド名（NAME）

Poke-Controller は、各スクリプトのクラス変数 `NAME` をコマンド一覧に表示します。

| スクリプト | NAME の書き方 | 一覧への表示 |
|---|---|---|
| `ZA_backupRestart.py` | `"ZA_BackupRestart"`（文字列リテラル） | ✅ |
| `ZA_day_night.py` | `"ZA_DayNightCheck"`（文字列リテラル） | ✅ |
| `ZA_donut_correct.py` | `f"ZA ドーナツ厳選 {CMD_NAME_SUFFIX} v{VERSION}"`（f 文字列） | ⚠️ バージョンによって表示されない |

**Poke-Controller Modified Extension 0.2.0 以降**の `CommandLoader.py` は、コードを実行せずに構文解析だけで `NAME` を読み取ります。f 文字列のように実行しないと値が決まらない書き方は「not a literal」として無視され、**コマンド一覧に表示されません**。

0.2.0 以降で使う場合は、`ZA_donut_correct.py` の `NAME` を文字列リテラルに書き換えてください。

```python
class ZA_DonutV188(ImageProcPythonCommand):
    # Poke-Controller Modified Extension 0.2.0 以降は NAME をソースから静的に読むため、文字列リテラルにする
    # (レシピ・タイプ等の情報は起動時のログに表示)
    NAME = "ZA ドーナツ厳選 v2.0.0"
```

書き換えた場合の注意:

- コマンド一覧にレシピやタイプが表示されなくなります。現在の設定は、起動時のログ（`[System] Recipe:` / `[System] Target:`）で確認してください。
- バージョンが `VERSION = '2.0.0'` と `NAME` の2か所に書かれることになります。**バージョンを上げるときは両方を更新**してください。

---

## 関連ドキュメント

- [README.md](README.md) - ドキュメント一覧
- [USER_CONFIG_GUIDE.md](USER_CONFIG_GUIDE.md) - config.json の全設定項目
- [IMAGE_TEMPLATES.md](IMAGE_TEMPLATES.md) - 画像テンプレート
