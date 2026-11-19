# pygame メモ

開発中に pygame・ゲーム開発の仕組みについて調べたこと・聞いたことのまとめ。

## 目次

- [dt（デルタタイム）](#dtデルタタイム)
- [pygame.display.set_mode と Surface](#pygamedisplayset_mode-と-surface)
- [Rect（四角形の位置と大きさ）](#rect四角形の位置と大きさ)
- [Sprite Group（キャラをまとめる箱）](#sprite-groupキャラをまとめる箱)
- [斜め移動が速くなる問題と Vector2](#斜め移動が速くなる問題と-vector2)
- [Rect は整数しか持てない（小数の移動がズレる）](#rect-は整数しか持てない小数の移動がズレる)

---

## dt（デルタタイム）

**前のフレームから今までに経過した時間（秒）。**

### なぜ必要か

FPS は目標値で、実際の 1 秒あたりの更新回数は PC の性能や処理の重さで変わる。
「1 フレームに 5px 進む」と書くと、更新回数が少ない PC ではゲーム全体が遅くなる（処理落ち）。

| 書き方 | 速い PC（60 回/秒） | 遅い PC（30 回/秒） |
|---|---|---|
| `x += 5`（1 フレームあたり） | 300px/秒 | 150px/秒 ← 遅くなる |
| `x += 300 * dt`（1 秒あたり） | 300px/秒 | 300px/秒 ← 同じ |

dt を掛けると、更新回数が少ないときは 1 回に大きく進むので、1 秒あたりの距離が揃う。

### pygame での取り方

```python
dt = self.clock.tick(FPS) / 1000   # tick() はミリ秒を返すので秒に直す
```

`clock.tick(FPS)` は「FPS を超えないように待つ」と「前回からの経過ミリ秒を返す」を同時にやってくれる。

---

## pygame.display.set_mode と Surface

**ウィンドウを作り、そこに描くための画用紙（Surface）を返す。描いたものは `flip()` で初めて画面に出る。**

```python
self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # タプル 1 つで渡す
```

- `pygame.init()` の後に 1 回だけ呼び、戻り値を使い回す
- `set_mode(600, 800)` はエラー。`set_mode((600, 800))` とカッコが二重になる

### Surface（画用紙）

- 絵を描ける板。画面も自機の `image` も同じ Surface
- 自機の小さい画用紙を、画面の大きい画用紙に貼り付けて描いている

### 描く → flip で見せる

| 処理 | たとえ |
|---|---|
| `fill` / `draw` | 舞台裏で準備する |
| `pygame.display.flip()` | 幕を開けて見せる |

描きかけの絵が見えないので、チラつかない。

### 座標

左上が (0, 0)。x は右、**y は下**に行くほど大きい。上に動く = y を減らす。

---

## Rect（四角形の位置と大きさ）

**位置と大きさを持った四角形。四角形のいろいろな場所を名前で読み書きでき、代入すると四角形ごと動く。**

- `surface.get_rect()` で、その Surface と同じ大きさの Rect が取れる（画面なら `self.screen.get_rect()`）
- Sprite の `self.rect` も Rect

### よく使う名前（600×800 の画面の場合）

| 名前 | 意味 | 値 |
|---|---|---|
| `left` / `right` | 左端 / 右端の x | 0 / 600 |
| `top` / `bottom` | 上端 / 下端の y | 0 / 800 |
| `centerx` / `centery` | 真ん中の x / y | 300 / 400 |
| `center` | 真ん中 `(x, y)` | (300, 400) |
| `midbottom` | 下辺の真ん中 `(x, y)` | (300, 800) |
| `width` / `height` | 幅 / 高さ | 600 / 800 |

### 代入すると動く

```python
self.rect = self.image.get_rect(midbottom=(300, 760))  # 作るときに位置を指定
self.rect.left = 0                                      # 左端が 0 になるように移動（大きさはそのまま）
```

---

## Sprite Group（キャラをまとめる箱）

**Sprite をまとめて入れる箱。中の全員に update や描画を 1 行でやらせられる。**

```python
self.all_sprites = pygame.sprite.Group()   # 空の箱
self.all_sprites.add(self.player)          # 入れる
self.all_sprites.update(dt)                # 全員の update(dt) を呼ぶ
self.all_sprites.draw(self.screen)         # 全員の image を rect の位置に描く
```

たとえ：Group はクラス、Sprite は生徒。先生（Game）が「みんな動いて」と言えば、生徒は自分のやり方で動く。先生は動き方を知らなくていい。

### よく使うもの

| 書き方 | やること |
|---|---|
| `group.add(sprite)` | 箱に入れる |
| `group.update(dt)` | 全員の `update(dt)` を呼ぶ |
| `group.draw(surface)` | 全員を描く（`image` と `rect` を使うので名前は変えない） |
| `sprite.kill()` | 入っている**全部の**箱から取り出す |
| `len(group)` | 何個入っているか |

### 1 つの Sprite を複数の箱に入れられる

敵は「全員用の箱」と「敵だけの箱」の両方に入れておくと、まとめて描きつつ、当たり判定では敵だけを調べられる。`kill()` で両方から一度に消える。

---

## 斜め移動が速くなる問題と Vector2

**縦横の向きをそのまま足すと、斜めは √2 倍（約 1.41 倍）速くなる。向きの長さを 1 にそろえる（正規化する）と直る。**

### なぜ √2 倍か

→↑ で `dx = 1, dy = -1`。進む距離は三角形の斜辺なので √(1² + 1²) = √2。

| キー | 向き | 長さ | 正規化後 |
|---|---|---|---|
| → | (1, 0) | 1 | (1, 0) |
| →↑ | (1, -1) | √2 | (0.707, -0.707) |

### pygame.math.Vector2

| 書き方 | 意味 |
|---|---|
| `pygame.math.Vector2(dx, dy)` | 向きをまとめる |
| `v.length()` | 長さ |
| `v.normalize()` | 長さを 1 にした新しいベクトルを返す |
| `v.x` / `v.y` | 中身 |

- `pygame.math` は pygame に入っているベクトル用のモジュール（`Vector2`, `Vector3`）
- `pygame.Vector2` と書いても同じもの（近道）
- Python 標準の `import math`（`sqrt`, `pi` など）とは別物

**長さ 0 のベクトルは normalize できない**（`ValueError`）。何も押していないときは正規化しない。

```python
direction = pygame.math.Vector2(1, -1)
if direction.length() > 0:
    direction = direction.normalize()   # (0.707, -0.707)
```

---

## Rect は整数しか持てない（小数の移動がズレる）

**`rect.x += 小数` は毎回四捨五入される（pygame 2.6.1）。端数が積み重なって速さがズレる。位置は小数で別に持ち、rect には写すだけにする。**

### 何が起きるか

1 フレームの移動量 = 速さ × dt（60 FPS で dt ≒ 0.016〜0.017）。1 秒動かした実測：

| 速さ | 本当は | 実際 |
|---|---|---|
| 300 | 300 | 300 |
| 100 | 100 | 120 |
| 20 | 20 | 0（0.33 px が毎回 0 に丸められて動かない） |

正規化した斜め移動のように、1 フレームの移動量が小数になるとズレやすい。

### 直し方：小数の位置を別に持つ

| 役割 | 使うもの |
|---|---|
| 本当の位置（計算用、小数） | `self.pos`（`Vector2`） |
| 描画・当たり判定用（整数） | `self.rect` |

```python
# __init__（rect を作った後）
self.pos = pygame.math.Vector2(self.rect.center)

# update
self.pos += direction * SPEED * dt
self.rect.center = self.pos           # ここで初めて丸められる
before = self.rect.center
self.rect.clamp_ip(self.bounds)
if self.rect.center != before:        # 押し戻されたときだけ
    self.pos = pygame.math.Vector2(self.rect.center)
```

- 押し戻したのに pos を直さないと、pos だけ画面外へ進み続け、反対のキーを押してもしばらく戻らない
- 逆に、**毎フレーム** pos を rect から作り直すと、小数が毎回捨てられて元の問題に戻る（実測：速さ 100 で 120px/秒、速さ 20 で動かない）
