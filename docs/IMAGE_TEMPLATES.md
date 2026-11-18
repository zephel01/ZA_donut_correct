# 画像テンプレート一覧（LegendsZA/）

`LegendsZA/` フォルダには、画面認識（OpenCV のテンプレートマッチング）に使う画像が入っています。どの画像がいつ読み込まれるかと、差し替え方をまとめます。

---

## 認識の仕組み

1. キャプチャ画面全体を**グレースケール**に変換します。
2. パワー名の**ラベル画像**（例: `shiny_label.png`）を探します。スコアは `threshold_label` と比べます。
3. ラベルの**右側の領域**（幅 180〜250px、上下 ±10px）で、**アイコン画像**（タイプ・どうぐ種類）を探します。スコアは `threshold_icon` と比べます。
4. 同じ領域で**レベル画像**（`lv2.png` / `lv3.png`）を探します。スコアは `threshold_level` と比べます。

したがって、テンプレートは**キャプチャ解像度と同じ縮尺**で切り出してある必要があります（同梱画像はラベルの高さが約 18px）。キャプチャ解像度が違う環境では、自分の環境で切り出し直してください。

---

## 一覧

### 共通（常に読み込まれる）

| ファイル | サイズ(px) | 用途 | 関連しきい値 |
|---|---|---|---|
| `dosari_label.png` | 115×18 | 「どっさりパワー」ラベル（どうぐモードのパワー1） | `threshold_label` |
| `lv2.png` | 40×17 | レベル表示 Lv2 | `threshold_level` |
| `lv3.png` | 40×17 | レベル表示 Lv3 | `threshold_level` |
| `result_text.png` | 282×88 | ドーナツ完成の結果画面の検知 | `threshold_result` |
| `area_all.png` | 107×32 | マップのエリア表示が「すべて」か判定（作成・移動時、しきい値 0.88 固定） | — |

`result_text.png` が無い場合は、警告を出して固定時間の待機に切り替わります。

### 色違いモード（TARGETS に `shiny`）

| ファイル | 用途 | 読み込み条件 |
|---|---|---|
| `shiny_label.png` | 「かがやきパワー」ラベル | 常に |
| `Type_All.png` | かがやきパワーのタイプ「ぜんぶ」 | 常に |
| `Type_<タイプ>.png` | `type` で指定したタイプのアイコン | `type` の各タイプ |
| `oyabun_label.png` | 「オヤブン」ラベル | 常に（`size: oyabun` で判定に使用） |
| `big2_label.png` | 「でかでか」ラベル | 常に（`size: big` で判定に使用） |
| `small2_label.png` | 「ちびちび」ラベル | 常に（`size: small` で判定に使用） |
| `capture_label.png` | 「ほかくパワー」ラベル | `enable_capture_power: true`、またはカスタム条件で `capture` を使うとき |
| `Type_All2.png` | ほかくパワーのタイプ「すべて」 | 同上 |

`Type_<タイプ>.png` は次の18種類です。

`Normal` `Fire` `Water` `Grass` `Electric` `Ice` `Fighting` `Poison` `Ground` `Flying` `Psychic` `Bug` `Rock` `Ghost` `Dragon` `Dark` `Steel` `Fairy`

> `Type_All.png`（かがやき用「ぜんぶ」）と `Type_All2.png`（ほかく用「すべて」）は別の画像です。

### どうぐモード（TARGETS に `shiny` を含まない）

| ファイル | 用途 | 読み込み条件 |
|---|---|---|
| `tool_label.png` | 「どうぐパワー」ラベル | 常に |
| `class_kinomi.png` | どうぐ種類: きのみ | `item_class: kinomi` |
| `class_ball.png` | どうぐ種類: ボール | `item_class: ball` |
| `class_coin.png` | どうぐ種類: コイン | `item_class: coin` |
| `class_treasure.png` | どうぐ種類: 宝物 | `item_class: treasure` |
| `class_special.png` | どうぐ種類: 特別 | `item_class: special` |
| `class_candy.png` | どうぐ種類: アメ | `item_class: candy` |

カスタム条件で別の `class` / `attribute` を指定した場合は、その画像も追加で読み込まれます。

### 補助スクリプト専用

| ファイル | 用途 | 使用元 |
|---|---|---|
| `time_day.png` | ゲーム内時間帯「昼」の判定 | `ZA_day_night.py` のみ |
| `time_night.png` | ゲーム内時間帯「夜」の判定 | `ZA_day_night.py` のみ |

本体（`ZA_donut_correct.py`）の昼夜切り替えは PC の時計で判断しており、この2枚は使いません。

### 同梱されていないもの

| ファイル | 影響 |
|---|---|
| `lv1.png` | レベル指定 `1` でも Lv1 が検出されない（`2` と同じ動作になる）。さらに本体の読み込み対象にも `lv1` が入っていない |

---

## 画像の差し替え・追加

認識がうまくいかない場合（キャプチャボードの解像度や色味が違う場合など）は、自分の環境のキャプチャから切り出し直します。

1. Poke-Controller で該当画面を表示し、**キャプチャ画像を保存**します（`debug_captures/BEFORE_*.png` を使っても構いません）。
2. 画像編集ソフトで、該当のラベル・アイコン・レベル表示を**余白を最小限にして**切り出します。
   - **拡大・縮小はしないでください**（キャプチャと同じ縮尺であることが必須です）。
   - ラベルはパワー名の文字部分だけを切り出します（右側のアイコンやレベルを含めないでください）。
3. **同じファイル名**の PNG で `LegendsZA/` に上書き保存します（ファイル名の大文字小文字も一致させてください）。
4. `debug_log: true` で動かし、ログのスコアを確認します。正しい画面で 0.9 前後になれば良好です。

### Lv1 を検出できるようにする

v2.0.0 では、画像を置くだけでは Lv1 を検出できません。次の2つが必要です。

1. Lv1 が表示されている結果画面から、`lv2.png` / `lv3.png` と同じ範囲を切り出して `LegendsZA/lv1.png` として保存する。
2. `ZA_donut_correct.py` の `_load_templates()` で、読み込み対象の `files` に `'lv1': 'lv1.png'` を追加する（現状は `lv2` と `lv3` だけ）。

---

## 関連ドキュメント

- [USER_CONFIG_GUIDE.md](USER_CONFIG_GUIDE.md#画像認識しきい値) - しきい値の調整
- [USER_CONDITIONS_GUIDE.md](USER_CONDITIONS_GUIDE.md) - カスタム条件で追加読み込みされる画像
- [README.md](README.md) - ドキュメント一覧
