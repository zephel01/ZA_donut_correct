# カスタム条件機能ガイド（donut_conditions.json）

## 概要

外部ファイル（`donut_conditions.json`）から任意の条件を定義し、その条件に一致するドーナツが出現した場合に自動的に終了する機能です。

**注意:** 詳細な設定は `USER_CONFIG_GUIDE.md` も参照してください。

---

## ファイル概要

`donut_conditions.json` は、ドーナツ作成時のパワー条件を定義するJSONファイルです。

- ファイル名: `donut_conditions.json`
- 配置場所: `ZA_donut_correct.py` と同じディレクトリ
- エンコード: UTF-8

---

## 対応するパワーテンプレート（5種類）

| テンプレート | type | 説明 |
|-------------|------|------|
| かがやきパワー | `shiny` | `attribute`でタイプを指定、`null`でタイプ不問 |
| サイズ | `size` | `size`で`oyabun`/`big`/`small`を指定 |
| ほかくパワー | `capture` | `attribute`でタイプを指定、`null`でタイプ不問 |
| どうぐパワー | `tool` | `class`で`kinomi`/`ball`/`coin`等を指定 |
| どっさりパワー | `dosari` | どっさりパワー（引数なし） |

---

## モード別の条件

### shinyモード時

- かがやきパワー × サイズパワーの組み合わせを狙う
- オヤブンLv3 × かがやき(特定タイプ)Lv3
- でかでかLv3 × かがやき(特定タイプ)Lv3
- ちびちびLv3 × かがやき(特定タイプ)Lv3
- かがやきパワー × サイズ × ほかくパワー（3パワー構造）

### toolモード時

- どうぐパワー × どっさりパワーの組み合わせを狙う
- どっさりLv3 × どうぐ(きのみ/ボール)Lv3

---

## JSON構造

```json
{
  "shiny_conditions": [
    {
      "name": "条件名",
      "_description": "条件の説明",
      "_note": "補足説明",
      "power1": { ... },
      "power2": { ... },
      "power3": { ... },  // 省略可能
      "enabled": true
    }
  ],
  "tool_conditions": [
    {
      "name": "条件名",
      "_description": "条件の説明",
      "_note": "補足説明",
      "power1": { ... },
      "power2": { ... },
      "power3": { ... },  // 省略可能
      "enabled": true
    }
  ]
}
```

### モード別条件

| セクション名 | 対応モード | 説明 |
|-------------|-----------|------|
| `shiny_conditions` | shiny系モード | 色違い厳選モード（shiny1-4）で使用 |
| `tool_conditions` | どうぐパワーモード | レシピ/レインボーモード（recipe1-3, rainbow1-3）で使用 |

### 条件の有効化

各条件には `"enabled"` フィールドがあります：
- `true`: 条件が有効になり、一致すると終了
- `false`: 条件が無効になり、チェックされない
- 省略: デフォルトで `true` として扱われる

### 複数条件の判定

カスタム条件はリスト順にチェックされ、最初に一致した条件で終了します。
- 複数の条件を有効にした場合、上から順にチェック
- 条件に優先順位を持たせたい場合は、リストの順序を調整

---

## パワーテンプレートの詳細（5種類）

### 1. かがやきパワー (shiny)

かがやきパワーのレベルとタイプを判定します。

| パラメータ | 説明 | 指定可能な値 |
|-----------|------|----------------|
| `type` | パワータイプ | `"shiny"` (固定) |
| `attribute` | タイプ指定 | `null` (タイプ不問) または タイプ名 (`"Fire"`, `"Water"`, 等) または タイプ配列 (`["Fire", "Ground"]`) |
| `min_level` | 目標レベル | `1` (妥協), `2`, `3` (厳選) |

**タイプ指定の例:**
```json
// タイプ不問
"attribute": null

// 単一タイプ
"attribute": "Fire"

// 複数タイプ
"attribute": ["Fire", "Ground"]
```

**対応タイプ一覧:**
Normal, Fire, Water, Grass, Electric, Ice, Fighting, Poison, Ground, Flying, Psychic, Bug, Rock, Ghost, Dragon, Dark, Steel, Fairy

---

### 2. サイズパワー (size)

サイズパワーの種類とレベルを判定します。

| パラメータ | 説明 | 指定可能な値 |
|-----------|------|----------------|
| `type` | パワータイプ | `"size"` (固定) |
| `size` | サイズ種類 | `"oyabun"` (オヤブン), `"big"` (でかでか), `"small"` (ちびちび) |
| `min_level` | 目標レベル | `1` (妥協), `2`, `3` (厳選) |

---

### 3. ほかくパワー (capture)

ほかくパワーのレベルとタイプを判定します。

| パラメータ | 説明 | 指定可能な値 |
|-----------|------|----------------|
| `type` | パワータイプ | `"capture"` (固定) |
| `attribute` | タイプ指定 | `null` (タイプ不問) または タイプ名 (`"Fire"`, `"Water"`, 等) または タイプ配列 (`["Fire", "Ground"]`) |
| `min_level` | 目標レベル | `1` (妥協), `2`, `3` (厳選) |

**タイプ指定の例:**
```json
// タイプ不問
"attribute": null

// 単一タイプ
"attribute": "Fire"

// 複数タイプ
"attribute": ["Fire", "Ground"]
```

---

### 4. どうぐパワー (tool)

どうぐパワーのクラスとレベルを判定します。

| パラメータ | 説明 | 指定可能な値 |
|-----------|------|----------------|
| `type` | パワータイプ | `"tool"` (固定) |
| `class` | アイテムクラス | `"kinomi"` (きのみ), `"ball"` (ボール), `"coin"` (コイン), `"treasure"` (宝物), `"special"` (特別), `"candy"` (アメ) |
| `min_level` | 目標レベル | `1` (妥協), `2`, `3` (厳選) |

---

### 5. どっさりパワー (dosari)

どっさりパワーのレベルを判定します。

| パラメータ | 説明 | 指定可能な値 |
|-----------|------|----------------|
| `type` | パワータイプ | `"dosari"` (固定) |
| `min_level` | 目標レベル | `1` (妥協), `2`, `3` (厳選) |

---

## 3パワー構造（power3の使用）

カスタム条件では、最大3つのパワーを同時に指定できます。

### 構造

```json
{
  "name": "条件名",
  "power1": { ... },  // 必須
  "power2": { ... },  // 必須
  "power3": { ... }   // 省略可能
}
```

### 使用例 (3パワー)

```json
{
  "name": "かがやき＋サイズ＋ほかく（3パワー）",
  "power1": {
    "type": "shiny",
    "attribute": null,
    "min_level": 3
  },
  "power2": {
    "type": "size",
    "size": "small",
    "min_level": 3
  },
  "power3": {
    "type": "capture",
    "attribute": null,
    "min_level": 1
  },
  "enabled": false
}
```

### 動作

- power1, power2, power3 のすべての条件を満たす場合に終了
- power3 を省略した場合、power1 と power2 のみで判定
- power3 は追加の条件として使用可能

---

## 条件の定義方法

`donut_conditions.json` ファイルを編集することで、モードごとに条件を定義できます。

### 基本的な定義例

```json
{
  "shiny_conditions": [
    {
      "name": "オヤブン×かがやき",
      "power1": {
        "type": "shiny",
        "attribute": null,
        "min_level": 3
      },
      "power2": {
        "type": "size",
        "size": "oyabun",
        "min_level": 3
      },
      "enabled": true
    }
  ],
  "tool_conditions": [
    {
      "name": "どっさり×どうぐ(きのみ)",
      "power1": {
        "type": "tool",
        "class": "kinomi",
        "min_level": 3
      },
      "power2": {
        "type": "dosari",
        "min_level": 3
      },
      "enabled": true
    }
  ]
}
```

---

## 有効化方法

### config.json で設定する場合

```json
{
  "use_custom_conditions": true,
  "conditions_file": "donut_conditions.json"
}
```

### ZA_donut_correct.py で設定する場合

```python
SETTING_USE_CUSTOM_CONDITIONS = True
SETTING_CONDITIONS_FILE = "donut_conditions.json"
```

---

## 設定例

### 例1: かがやきパワー(Fire)Lv3 × オヤブンLv3 を狙う場合

```json
{
  "shiny_conditions": [
    {
      "name": "かがやき(Fire)Lv3 × オヤブンLv3",
      "power1": {
        "type": "shiny",
        "attribute": "Fire",
        "min_level": 3
      },
      "power2": {
        "type": "size",
        "size": "oyabun",
        "min_level": 3
      },
      "enabled": true
    }
  ],
  "tool_conditions": []
}
```

---

### 例2: かがやきパワー(Fire/Ground)Lv3 × オヤブンLv3 を狙う場合（複数タイプ指定）

```json
{
  "shiny_conditions": [
    {
      "name": "かがやき(Fire/Ground)Lv3 × オヤブンLv3",
      "power1": {
        "type": "shiny",
        "attribute": ["Fire", "Ground"],
        "min_level": 3
      },
      "power2": {
        "type": "size",
        "size": "oyabun",
        "min_level": 3
      },
      "enabled": true
    }
  ],
  "tool_conditions": []
}
```

---

### 例3: すべてのかがやきパワーLv3 × すべてのサイズLv3 を狙う場合

```json
{
  "shiny_conditions": [
    {
      "name": "オヤブン×かがやき",
      "power1": { "type": "shiny", "attribute": null, "min_level": 3 },
      "power2": { "type": "size", "size": "oyabun", "min_level": 3 },
      "enabled": true
    },
    {
      "name": "でかでか×かがやき",
      "power1": { "type": "shiny", "attribute": null, "min_level": 3 },
      "power2": { "type": "size", "size": "big", "min_level": 3 },
      "enabled": true
    },
    {
      "name": "ちびちび×かがやき",
      "power1": { "type": "shiny", "attribute": null, "min_level": 3 },
      "power2": { "type": "size", "size": "small", "min_level": 3 },
      "enabled": true
    }
  ],
  "tool_conditions": []
}
```

---

### 例4: かがやきパワー × サイズ × ほかくパワー（3パワー）を狙う場合

```json
{
  "shiny_conditions": [
    {
      "name": "かがやき＋サイズ＋ほかく（3パワー）",
      "power1": {
        "type": "shiny",
        "attribute": null,
        "min_level": 3
      },
      "power2": {
        "type": "size",
        "size": "small",
        "min_level": 3
      },
      "power3": {
        "type": "capture",
        "attribute": null,
        "min_level": 1
      },
      "enabled": true
    }
  ],
  "tool_conditions": []
}
```

---

### 例5: どっさりLv3 × どうぐ(きのみ)Lv3 を狙う場合

```json
{
  "shiny_conditions": [],
  "tool_conditions": [
    {
      "name": "どっさり×どうぐ(きのみ)",
      "power1": { "type": "tool", "class": "kinomi", "min_level": 3 },
      "power2": { "type": "dosari", "min_level": 3 },
      "enabled": true
    }
  ]
}
```

---

## 注意点

1. **エンコーディング**: ファイルは必ず UTF-8 で保存してください
2. **JSON構文**: JSON構文が正しいことを確認してください（カンマ、括弧など）
3. **タイプ名**: タイプ名は大文字小文字を区別し、正しい綴りで指定してください
4. **レベル指定**: `min_level` は `1`, `2`, `3` のいずれかを指定してください
5. **enabledフラグ**: テストする条件のみ `enabled: true` に設定してください
6. **モード別条件**: shinyモードでは `shiny_conditions`、toolモードでは `tool_conditions` が使用されます
7. **優先順位**: 複数の条件を有効にした場合、リストの上から順にチェックされます

---

## 関連ドキュメント

- `USER_CONFIG_GUIDE.md` - カスタム条件の有効化設定や環境変数について
- `USER_RECIPE_GUIDE.md` - レシピの作成方法について
- `README.md` - メインの使用方法について
