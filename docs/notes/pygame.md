# pygame メモ

開発中に pygame・ゲーム開発の仕組みについて調べたこと・聞いたことのまとめ。

## 目次

- [dt（デルタタイム）](#dtデルタタイム)
- [pygame.display.set_mode と Surface](#pygamedisplayset_mode-と-surface)
- [Rect（四角形の位置と大きさ）](#rect四角形の位置と大きさ)
- [文字を描く（Font と render）](#文字を描くfont-と-render)
- [描画まわりのメソッドの整理](#描画まわりのメソッドの整理)
- [Surface の作り方いろいろ（画像ファイル・図形）](#surface-の作り方いろいろ画像ファイル図形)
- [Sprite Group（キャラをまとめる箱）](#sprite-groupキャラをまとめる箱)
- [斜め移動が速くなる問題と Vector2](#斜め移動が速くなる問題と-vector2)
- [Rect は整数しか持てない（小数の移動がズレる）](#rect-は整数しか持てない小数の移動がズレる)
- [当たり判定の形（四角・円・マスク）](#当たり判定の形四角円マスク)

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

### image と rect の分担

**Rect は「画面のどこからどこまで」という範囲。四角形を画面の上に描き表すには、大きさだけでなく位置も必要なので、4 つの数字 (x, y, 幅, 高さ) で持つ。**

| | image（Surface） | rect（Rect） |
|---|---|---|
| 持っているもの | 絵の中身（色の点の集まり）と大きさ | 位置と大きさ（数字 4 つ） |
| たとえ | 車 | 駐車場の白線の枠 |
| 使う場面 | 描くとき（何を描くか） | 描くとき（どこに描くか）・動かすとき・当たり判定 |

- 分けておくと、動かすときや当たり判定は数字 4 つの rect だけで済み、重い絵には触らなくていい
- 大きさは普通 `image.get_rect()` で image に合わせるが、別物なので位置は rect にしかない

**image を rect に貼るのではない。** rect は絵を持てない（ただの数字）。`screen.blit(image, rect)` は、image を**画面に直接**貼り、貼る位置として rect の左上だけを使う。rect の大きさは描画では使われない（わざと 5×5 の Rect を渡しても、40×30 の絵がそのまま描かれる。pygame 2.6.1 で確認）。

```
screen（画用紙） ← image（シール）を貼る
                    ↑ 貼る場所は rect の左上 (x, y) を見て決める
```

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

### get_rect() で位置を指定する

`surface.get_rect(場所の名前=値)` で、「四角形のその場所」を「その値」に合わせて作る。大きさは画像から自動で決まるので、書くのは位置だけ。何も書かないと左上 (0, 0) に置かれる。

**get_rect は「情報を取るだけ」ではなく、呼ぶたびに新しい Rect を作って返す。** Surface 自体は位置を持っていない。位置を持つのは返ってきた Rect なので、`self.rect` に入れて覚えておく（pygame 2.6.1 で確認）：

```python
a = img.get_rect(left=100, bottom=0)  # (100, -30, 40, 30)  新しい Rect
a.x = 500                             # a だけが動く
img.get_rect()                        # (0, 0, 40, 30)  img は何も覚えていない
```

| 場所の名前 | 種類 | 渡す値 |
|---|---|---|
| `left` `right` `centerx` | 縦の線（x だけ） | 数字 1 つ |
| `top` `bottom` `centery` | 横の線（y だけ） | 数字 1 つ |
| `center` `midtop` `midbottom` `topleft` など | 点 | `(x, y)` のタプル |

- 点：四角形の 1 か所（角・辺の真ん中・中心）。縦横両方が要るので `(x, y)`
- 線：辺 1 本。`bottom` は横に伸びた辺なので y だけ、`left` は縦に伸びた辺なので x だけで決まる

```
  topleft     midtop     topright
     ●──────────●──────────●   ← top
     │                     │
 left│        center       │right
     ●          ●          ●
     │                     │
     ●──────────●──────────●   ← bottom
 bottomleft  midbottom  bottomright
```

x を決める名前と y を決める名前を 1 つずつ書けば組み合わせられる。40×30 の画像の場合（pygame 2.6.1 で確認）：

```python
image.get_rect()                       # (0, 0, 40, 30)
image.get_rect(center=(100, 100))      # (80, 85, 40, 30)
image.get_rect(left=50, bottom=0)      # (50, -30, 40, 30)  画面の上の外に置ける
```

**Rect を表示すると `(left, top, width, height)` の順で出る。** 下端（bottom）を指定しても、表示されるのは上端（top）。`bottom=0` で高さ 30 なら、top = 0 − 30 = **−30**。y は上に行くほど小さいので、マイナスは画面より上（外）を意味する。

### `center=screen_rect.center` のように名前が 2 回出てくる理由

**`=` の左は「新しく作る四角形のどこを」、右は「どこに合わせるか（値）」。同じ名前になるのは「自分の真ん中を、画面の真ん中に」と同じ場所どうしを合わせたいときだけ。**

```python
text.get_rect(center=self.screen.get_rect().center)
#             ~~~~~~ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#             文字の真ん中を   画面の真ん中 (300, 400) に合わせる
```

| 書き方 | 左（自分のどこ） | 右（どこに） | 結果 |
|---|---|---|---|
| `text.get_rect(center=screen_rect.center)` | 文字の真ん中 | 画面の真ん中 | 画面の中央に置く |
| `image.get_rect(bottom=bounds.top)`（敵） | 敵の下端 | 画面の上端 | 画面のすぐ上の外に置く |

- 左はキーワード引数の名前（決まった名前しか書けない）、右はただの値。`center=(300, 400)` と数字で書いても同じ
- 名前が同じなのはたまたま。敵のように左右で違う名前になることも多い

**Surface が決めるのは大きさだけで、位置は決めない。** だから登場人物が 2 人いる。

| 登場人物 | 決めること |
|---|---|
| `text`（文字の Surface） | 四角形の大きさ（303×49） |
| `self.screen`（画面） | 四角形を置く場所（真ん中 = (300, 400)） |

1 行の書き方は、次の 2 行をまとめたもの（pygame 2.6.1 で同じ結果を確認）：

```python
text_rect = text.get_rect()                       # (0, 0, 303, 49)    大きさだけ決まる。位置は左上
text_rect.center = self.screen.get_rect().center  # (149, 376, 303, 49) 真ん中へ動かす
```

---

## 文字を描く（Font と render）

**`font.render(...)` は、文字を描いた Surface（画像）を返す。あとは自機の image と同じように blit する。**

| 書き方 | 返すもの | たとえ |
|---|---|---|
| `pygame.font.Font(None, 72)` | `Font` | はんこ（文字の形と大きさ） |
| `font.render("GAME OVER", True, 色)` | `Surface`（大きさは文字に合わせて自動。72 なら 303×49） | はんこを押した紙 |

```python
text = self.game_over_font.render("GAME OVER", True, GAME_OVER_COLOR)  # この時点で text は Surface
self.screen.blit(text, text_rect)
```

- 2 つ目の `True` はアンチエイリアス（文字のふちをなめらかにする）
- Font は `__init__` で 1 回作る。render は文字が変わるなら毎フレーム呼ぶ（スコアなど）

### `Font(None, 36)` の None

**1 つ目の引数はフォントファイルの場所。`None` は「ファイルは指定しない。pygame に入っている標準フォント（freesansbold.ttf）を使う」という意味。** 2 つ目は文字の大きさ。

| 書き方 | 使うフォント |
|---|---|
| `pygame.font.Font(None, 36)` | pygame の標準フォント |
| `pygame.font.Font("assets/xxx.ttf", 36)` | 自分で用意したフォントファイル |
| `pygame.font.SysFont("meiryo", 36)` | PC に入っているフォントを名前で探す |

- 標準フォントは英数字だけ。**日本語は表示できない**（「あ」を render すると幅 10 の小さな絵になり、文字にならない。pygame 2.6.1 で確認）
- 日本語を出したいときは、日本語の入ったフォントファイルか SysFont を使う

---

## 描画まわりのメソッドの整理

**描画は「絵を作る → 塗る → 画面に貼る → 見せる」の 4 段階。メソッドが多いのは、段階ごとに担当が分かれているから。**

| 段階 | メソッド | 誰のメソッド | やること |
|---|---|---|---|
| 作る | `pygame.Surface((幅, 高さ))` | pygame | 白紙の絵を作る |
| 作る | `font.render(文字, True, 色)` | Font | 文字を描いた絵を作る |
| 塗る | `surface.fill(色)` | Surface | 絵全体を 1 色で塗る（画面なら背景を塗って前のフレームを消す） |
| 場所 | `surface.get_rect(...)` | Surface | 貼る場所と大きさの Rect を作る |
| 貼る | `screen.blit(絵, 場所)` | Surface | 絵を 1 枚、画面に貼る |
| 貼る | `group.draw(screen)` | Group | 中の全員を blit する（for で blit を回すのと同じ） |
| 見せる | `pygame.display.flip()` | pygame | 裏で描いた画面を、まとめて表に出す |

```python
def draw(self):
    self.screen.fill(BG_COLOR)                 # 塗る：前のフレームを消す
    self.all_sprites.draw(self.screen)         # 貼る：キャラ全員
    score_image = self.font.render(...)        # 作る：文字の絵
    self.screen.blit(score_image, SCORE_POS)   # 貼る：文字
    pygame.display.flip()                      # 見せる
```

- Game の `draw()`（自分で作ったメソッド）と Group の `draw()`（pygame のメソッド）は、名前が同じだけの別物
- 後から貼ったものが上に重なる。だから 背景 → キャラ → 文字 の順

---

## Surface の作り方いろいろ（画像ファイル・図形）

**image は Surface でさえあればよい。白紙を塗る以外に、画像ファイルを読み込んだり、図形を描いたりして作れる。rect・blit・当たり判定はそのまま使える。**

| 作り方 | 書き方 | 大きさ |
|---|---|---|
| 白紙を 1 色で塗る（今のやり方） | `pygame.Surface((40, 40))` → `.fill(色)` | 自分で指定 |
| 画像ファイルを読む | `pygame.image.load("assets/player.png").convert_alpha()` | 画像ファイルの大きさ |
| 図形を描く | 透明な Surface に `pygame.draw.circle(surface, 色, 中心, 半径)` など | 自分で指定 |
| 文字 | `font.render(...)` | 文字に合わせて自動 |

```python
self.image = pygame.image.load("assets/player.png").convert_alpha()
self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))  # 大きさをそろえる
self.rect = self.image.get_rect(midbottom=...)   # ここから下は今までと同じ
```

- `convert_alpha()` は、画面に貼りやすい形に変換して描画を速くする（透明も保つ）。**`set_mode` の後でないとエラー**（`No video mode has been set`。pygame 2.6.1 で確認）
- 読み込みは `__init__` で 1 回。毎フレーム load すると重い。同じ絵の敵がたくさん出るなら、1 回読んだ絵を使い回すとよい
- `transform.scale` で大きさを変えられる（64×48 の画像 → 40×30 を確認）

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

---

## 当たり判定の形（四角・円・マスク）

**`spritecollideany` や `groupcollide` は、ふつう rect（四角）どうしが重なったかで判定する。絵が丸や変な形でも、当たり判定は四角になる。**

透明な部分（絵のすき間）に触れただけでも当たりになる。形に合わせたいときは、関数の最後に判定のしかたを渡す。

| 渡すもの | 判定の形 | 特徴 |
|---|---|---|
| なし（ふつう） | rect の四角 | 速い。今の色付き四角ならこれで十分 |
| `pygame.sprite.collide_circle` | 円 | 両方を円とみなす（rect から半径を決める）。丸いキャラ向け |
| `pygame.sprite.collide_mask` | 絵の形そのもの | 透明でない点が重なったときだけ当たり。正確だが重い |

```python
pygame.sprite.spritecollideany(self.player, self.enemies, pygame.sprite.collide_mask)
```

丸い敵（40×40 の円）と四角い自機の角だけが重なる配置で試した結果（pygame 2.6.1）：rect → 当たり、collide_mask → 当たらない。

- collide_mask を使うには、image を透明が使える形（`pygame.Surface(大きさ, pygame.SRCALPHA)`）で作る
- シューティングでは、わざと当たり判定を絵より小さくすることも多い（自機がぎりぎりで避けられて気持ちいい）。`rect.inflate(-10, -10)` で上下左右を 5 ずつ縮めた四角が作れる
