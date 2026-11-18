# 同梱レシピ一覧

`recipes/` フォルダに同梱されているレシピの一覧です。使うレシピは `config.json` の `recipe` に**ファイル名（拡張子なし）**で指定します。

```json
{ "recipe": "shiny1" }
```

自作レシピの作り方は [USER_RECIPE_GUIDE.md](USER_RECIPE_GUIDE.md) を参照してください。

---

## 一覧

| レシピ名 | NAME（ログ表示名） | CATEGORY | TARGETS | モード | 主に使う設定 |
|---|---|---|---|---|---|
| `shiny1` | 色違い厳選レシピ1 (節約版) | shiny | `['shiny']` | 色違い | `type`, `size` |
| `shiny2` | 色違い厳選レシピ2 (タンガのみ×8) | shiny | `['shiny']` | 色違い | `type`, `size` |
| `shiny3` | 色違い厳選レシピ3 (ほかくパワー付与レシピ) | shiny | `['shiny']` | 色違い | `type`, `size`, ほかく関連 |
| `shiny4` | 色違い厳選レシピ4 (ほかくパワー付与レシピ2 New) | shiny | `['shiny']` | 色違い | `type`, `size`, ほかく関連 |
| `recipe1` | どうぐパワー節約レシピ | tool | `['tool']` | どうぐ | `item_class` |
| `recipe2` | どうぐパワー重視レシピ/カシブx8 | tool | `['tool']` | どうぐ | `item_class` |
| `recipe3` | 節約レシピ recipe3 | tool | `['tool']` | どうぐ | `item_class` |
| `rainbow1` | レインボードーナツ どうぐパワー（バコウ1, ウタン1, ナモ4, ロゼル2） | rainbow | `['tool']` | どうぐ | `item_class` |
| `rainbow2` | バコウ1,ヨロギ1,ハバン1,ロゼル5 | rainbow | `['tool']` | どうぐ | `item_class` |
| `rainbow3` | ウタン1,ヨロギ1,ナモ4,ロゼル2 | rainbow | `['tool']` | どうぐ | `item_class` |
| `template` | — | — | — | **使用不可**（自作用の雛形。自動検出の対象外） | — |

- **モード**は `TARGETS` で決まります。`'shiny'` を含めば色違いモード、それ以外はどうぐモードです。
- `CATEGORY` は分類用のラベルで、動作には影響しません。
- rainbow 系はファイル内のコメントにあるとおり、`TARGETS = ['shiny']` に書き換えると色違いモードでも使えます。

---

## 入力操作（STEPS）

各レシピは、食材選択画面でのボタン操作の並びとして定義されています。どのステップも `pressRep`（同じボタンを `repeat` 回押す）で、押下時間は十字キー 0.05 秒・A ボタン 0.1 秒、間隔は 0.1 秒です。

表記: `↑n` = 十字キー上を n 回、`A×n` = A ボタンを n 回

| レシピ名 | 操作の並び | 食材の合計数（A の回数） |
|---|---|---|
| `shiny1` | ↑5 → A×4 → ↑3 → A×4 | 8 |
| `shiny2` | ↑8 → A×8 | 8 |
| `shiny3` | ↑5 → A×6 → ↑3 → A×2 | 8 |
| `shiny4` | ↑5 → A×6 → ↑4 → A×1 → ↑5 → A×1 | 8 |
| `recipe1` | ↑1 → A×3 → ↑2 → A×1 → ↑3 → A×4 | 8 |
| `recipe2` | ↑6 → A×8 | 8 |
| `recipe3` | ↑1 → A×1 → ↑2 → A×4 → ↑1 → A×3 | 8 |
| `rainbow1` | ↑1 → A×2 → ↑3 → A×4 → ↑5 → A×1 → ↑1 → A×1 | 8 |
| `rainbow2` | ↑1 → A×5 → ↑4 → A×1 → ↑2 → A×1 → ↑3 → A×1 | 8 |
| `rainbow3` | ↑1 → A×2 → ↑3 → A×4 → ↑3 → A×1 → ↑2 → A×1 | 8 |

> カーソルの移動量は**食材リストの並び順と所持状況**に依存します。所持していない食材があったり並び順が違ったりすると、別の食材が選ばれます。新しく使うレシピは、最初に `debug_log: true` で1回動かし、実際に選ばれる食材を目で確認してください。

---

## レシピ別の推奨設定

### 色違い厳選（shiny1〜shiny4）

```json
{
  "recipe": "shiny1",
  "type": "Dragon",
  "size": "oyabun",
  "level_size": 3,
  "level_extra": 3
}
```

shiny3 / shiny4（ほかくパワー付与レシピ）では、ほかくパワーも条件にできます。

```json
{
  "recipe": "shiny4",
  "type": "Dragon",
  "size": "oyabun",
  "enable_capture_power": true,
  "level_capture": 2,
  "capture_compromise": true
}
```

### どうぐパワー集め（recipe1〜3, rainbow1〜3）

```json
{
  "recipe": "recipe1",
  "item_class": "kinomi",
  "level_size": 3,
  "level_extra": 3
}
```

どうぐモードでは、`level_size` が**どっさりパワー**、`level_extra` が**どうぐパワー**のレベルになります。

---

## レシピの追加・差し替え

- `recipes/` に `.py` ファイルを置くだけで、次回の起動時に自動検出されます（起動ログの `[System] Available recipes:` に表示されます）。
- [ZAドーナツシミュレーター](https://zadonutsimulator.zephyr.com/) で作ったレシピファイルも、そのまま `recipes/` に置いて使えます。
- 必須の変数は `NAME` / `STEPS` / `TARGETS` です。1つでも欠けていると起動時にエラーになります。

詳細は [USER_RECIPE_GUIDE.md](USER_RECIPE_GUIDE.md) を参照してください。
