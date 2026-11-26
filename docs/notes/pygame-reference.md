# pygame 逆引きリファレンス

このプロジェクト（縦スクロールシューティング）で使った pygame のクラス・関数・メソッドだけをまとめた辞典。
次のゲームを作るときに「あれ、どう書くんだっけ？」を引くためのもの。

- 確認した環境：pygame 2.6.1 / Python 3.12。返り値はすべて実際に動かして確かめた
- 仕組みの説明（なぜそうなるか）は [pygame.md](pygame.md) にある。こちらは「書き方・引数・返り値・いつ使うか」だけ
- 「例」のリンクは、このプロジェクトで実際に使っている場所

## 目次

- [早見表](#早見表)
- [ゲームの骨組み](#ゲームの骨組み)
- [1. 起動と終了](#1-起動と終了)
- [2. 時間（Clock）](#2-時間clock)
- [3. 入力（イベントとキー）](#3-入力イベントとキー)
- [4. Surface（絵）と描画](#4-surface絵と描画)
- [5. 文字（Font）](#5-文字font)
- [6. Rect（位置と大きさ）](#6-rect位置と大きさ)
- [7. Vector2（向きと小数の位置）](#7-vector2向きと小数の位置)
- [8. Sprite（キャラ）](#8-spriteキャラ)
- [9. Group（キャラの箱）](#9-groupキャラの箱)
- [10. 当たり判定](#10-当たり判定)
- [よくあるまちがい](#よくあるまちがい)

---

## 早見表

| やりたいこと | 書き方 | 返り値 |
|---|---|---|
| pygame を使い始める | `pygame.init()` | （使わない） |
| ウィンドウを作る | `pygame.display.set_mode((幅, 高さ))` | 画面の `Surface` |
| ウィンドウの題名 | `pygame.display.set_caption("題名")` | `None` |
| フレームの速さをそろえる・dt を取る | `clock.tick(FPS)` | 前回からのミリ秒（`int`） |
| 入力を全部取り出す | `pygame.event.get()` | `Event` のリスト |
| 押しっぱなしのキーを調べる | `pygame.key.get_pressed()` | キーごとの True/False |
| 白紙の絵を作る | `pygame.Surface((幅, 高さ))` | `Surface` |
| 絵を 1 色で塗る | `surface.fill(色)` | 塗った範囲の `Rect`（使わない） |
| 絵を画面に貼る | `screen.blit(絵, 位置)` | 貼った範囲の `Rect`（使わない） |
| 絵の位置と大きさを作る | `surface.get_rect(場所=値)` | 新しい `Rect` |
| 描いた画面を表に出す | `pygame.display.flip()` | `None` |
| 文字の絵を作る | `font.render(文字, True, 色)` | `Surface` |
| 四角を枠の中に収める | `rect.clamp_ip(枠)` | `None`（rect 自身が動く） |
| 向きの長さを 1 にする | `vector.normalize()` | 新しい `Vector2` |
| キャラを全部の箱から消す | `sprite.kill()` | `None` |
| 箱の全員を動かす | `group.update(dt)` | `None` |
| 箱の全員を描く | `group.draw(screen)` | （使わない） |
| 箱と箱の当たり判定 | `pygame.sprite.groupcollide(箱1, 箱2, 消す1, 消す2)` | 当たった組の辞書 |
| 1 体と箱の当たり判定 | `pygame.sprite.spritecollideany(キャラ, 箱)` | 当たった 1 体 か `None` |
| pygame を終える | `pygame.quit()` | `None` |

---

## ゲームの骨組み

次のゲームもこの形から始められる。どの API がどこで使われるかの地図。

```python
import pygame

class Game:
    def __init__(self):
        pygame.init()                                   # 1. 起動
        pygame.display.set_caption("タイトル")
        self.screen = pygame.display.set_mode((600, 800))
        self.clock = pygame.time.Clock()                # 2. 時間
        self.running = True
        self.scene = PlayScene(self)

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000             # 秒に直す
            for event in pygame.event.get():            # 3. 入力
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene.handle_event(event)
            self.scene.update(dt)                       # 更新
            self.scene.draw(self.screen)                # 4. 描画（fill → group.draw → blit）
            pygame.display.flip()                       # 表に出す
        pygame.quit()                                   # 1. 終了
```

---

## 1. 起動と終了

### `pygame.init()`

| | |
|---|---|
| いつ使う | プログラムの最初に 1 回。ほかの pygame の機能を使う前 |
| 引数 | なし |
| 返り値 | `(成功した数, 失敗した数)` のタプル（例：`(5, 0)`）。ふつうは使わない |
| 例 | [game.py:16](../../src/shooter/game.py#L16) |

### `pygame.display.set_mode(size)`

| | |
|---|---|
| いつ使う | ウィンドウを作るとき。`init()` の後に 1 回 |
| 引数 | `size`：`(幅, 高さ)` の**タプル 1 つ** |
| 返り値 | 画面の `Surface`。ここに描く。`self.screen` などに入れて使い回す |
| 例 | [game.py:18](../../src/shooter/game.py#L18) |

- `set_mode(600, 800)` はエラー。`set_mode((600, 800))` とカッコが二重
- `convert_alpha()`（画像の読み込み）など、画面ができてからでないと使えない機能がある

### `pygame.display.set_caption(title)`

| | |
|---|---|
| いつ使う | ウィンドウの上に出る題名を決めるとき |
| 引数 | `title`：文字列 |
| 返り値 | `None` |
| 例 | [game.py:17](../../src/shooter/game.py#L17) |

### `pygame.quit()`

| | |
|---|---|
| いつ使う | ゲームループを抜けた後に 1 回。ウィンドウを閉じて後片づけする |
| 引数 | なし |
| 返り値 | `None` |
| 例 | [game.py:33](../../src/shooter/game.py#L33) |

---

## 2. 時間（Clock）

### `pygame.time.Clock()`

| | |
|---|---|
| いつ使う | フレームの速さを管理したいとき。`__init__` で 1 回作る |
| 引数 | なし |
| 返り値 | `Clock` |
| 例 | [game.py:19](../../src/shooter/game.py#L19) |

### `clock.tick(framerate)`

| | |
|---|---|
| いつ使う | ゲームループの**最初に毎フレーム 1 回** |
| 引数 | `framerate`：1 秒あたりの最大フレーム数（例：`60`） |
| 返り値 | 前回の `tick` からの経過**ミリ秒**（`int`） |
| 例 | [game.py:28](../../src/shooter/game.py#L28) |

- 2 つの仕事を同時にする：①速すぎるときは待って 60 FPS を超えないようにする ②経過時間を返す
- `/ 1000` で秒に直して `dt` にする。移動は `速さ × dt`（[pygame.md の dt](pygame.md#dtデルタタイム)）

---

## 3. 入力（イベントとキー）

**単発の操作（撃つ・決定・リトライ）はイベント、押しっぱなしの操作（移動）は `get_pressed`。**

| | `pygame.event.get()` のイベント | `pygame.key.get_pressed()` |
|---|---|---|
| わかること | 「今押された」「今離された」 | 「今押されている」 |
| 1 回押すと | 1 回だけ届く | 押している間ずっと True |
| 向いている操作 | 弾を撃つ、R でリトライ、ESC で終了 | 矢印キーで移動 |

### `pygame.event.get()`

| | |
|---|---|
| いつ使う | ゲームループで**毎フレーム必ず 1 回**。たまった入力を全部取り出す |
| 引数 | なし |
| 返り値 | `Event` のリスト。取り出した分は消える |
| 例 | [game.py:36](../../src/shooter/game.py#L36) |

- 呼ばないと入力がたまり続け、ウィンドウが「応答なし」になる
- 1 フレームに 2 回呼ぶと、1 回目で取り出された入力は 2 回目には来ない。`for` で 1 回だけ回して、各場面に配る

### `Event`（イベント 1 つ）

| 属性 | 中身 |
|---|---|
| `event.type` | 種類。下の定数と `==` で比べる |
| `event.key` | どのキーか（`type` が `KEYDOWN` / `KEYUP` のときだけある） |

| 定数 | 意味 |
|---|---|
| `pygame.QUIT` | ウィンドウの × が押された |
| `pygame.KEYDOWN` | キーが押された（押した瞬間に 1 回） |
| `pygame.KEYUP` | キーが離された |

```python
if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
    self.shoot()
```

例：[scenes.py:47](../../src/shooter/scenes.py#L47)（スペースで撃つ）、[scenes.py:85](../../src/shooter/scenes.py#L85)（R でリトライ）

### キーの定数 `pygame.K_...`

| 定数 | キー |
|---|---|
| `K_LEFT` `K_RIGHT` `K_UP` `K_DOWN` | 矢印キー |
| `K_SPACE` | スペース |
| `K_ESCAPE` | Esc |
| `K_RETURN` | Enter |
| `K_a` 〜 `K_z` | 英字（小文字で書く。例：`K_r`） |

### `pygame.key.get_pressed()`

| | |
|---|---|
| いつ使う | 押しっぱなしで動かしたいとき。`update` の中で毎フレーム |
| 引数 | なし |
| 返り値 | 全キーの状態。`keys[pygame.K_LEFT]` のように引くと True / False |
| 例 | [player.py:26](../../src/shooter/player.py#L26) |

```python
keys = pygame.key.get_pressed()
if keys[pygame.K_LEFT]:
    direction.x -= 1
```

---

## 4. Surface（絵）と描画

**描画は「作る → 塗る → 貼る → 表に出す」の順。後から貼ったものが上に重なる。**（[pygame.md の描画まわり](pygame.md#描画まわりのメソッドの整理)）

### `pygame.Surface(size)`

| | |
|---|---|
| いつ使う | キャラの絵（白紙）を作るとき。`__init__` で 1 回 |
| 引数 | `size`：`(幅, 高さ)`。透明を使いたいときは `pygame.Surface(size, pygame.SRCALPHA)` |
| 返り値 | `Surface`（最初は黒） |
| 例 | [player.py:17](../../src/shooter/player.py#L17) |

- Surface は絵の中身と大きさだけを持つ。**位置は持たない**（位置は Rect）
- 画像ファイルから作るなら `pygame.image.load("x.png").convert_alpha()`（[pygame.md](pygame.md#surface-の作り方いろいろ画像ファイル図形)）

### `surface.fill(color)`

| | |
|---|---|
| いつ使う | ①画面を背景色で塗って前のフレームを消す（毎フレーム、描画の最初） ②キャラの絵に色をつける（`__init__` で 1 回） |
| 引数 | `color`：`(R, G, B)`。各 0〜255 |
| 返り値 | 塗った範囲の `Rect`。ふつうは使わない |
| 例 | [scenes.py:72](../../src/shooter/scenes.py#L72)（背景）、[player.py:18](../../src/shooter/player.py#L18)（キャラ） |

### `screen.blit(source, dest)`

| | |
|---|---|
| いつ使う | 絵を 1 枚、画面（など別の Surface）に貼るとき |
| 引数 | `source`：貼る絵（Surface）／`dest`：貼る位置。`(x, y)` か `Rect` |
| 返り値 | 実際に貼った範囲の `Rect`。ふつうは使わない |
| 例 | [scenes.py:75](../../src/shooter/scenes.py#L75)、[scenes.py:92](../../src/shooter/scenes.py#L92) |

- 位置は絵の**左上**。`Rect` を渡したときも左上だけを見る（Rect の大きさは無視され、絵はそのままの大きさで貼られる）
- 真ん中に置きたいときは、`get_rect(center=...)` で Rect を作って渡す

### `surface.get_rect(**場所)`

| | |
|---|---|
| いつ使う | 絵と同じ大きさの Rect を、好きな位置に作るとき |
| 引数 | なし、または `場所の名前=値`（`center=(x, y)`、`midbottom=(x, y)`、`left=x`、`bottom=y` など） |
| 返り値 | **新しい** `Rect`。呼ぶたびに別のものが作られる |
| 例 | [bullet.py:13](../../src/shooter/bullet.py#L13)、[enemy.py:21](../../src/shooter/enemy.py#L21)、[scenes.py:91](../../src/shooter/scenes.py#L91) |

```python
image.get_rect()                          # (0, 0, 40, 30)  左上に置く
image.get_rect(center=(100, 100))         # (80, 85, 40, 30)
text.get_rect(center=screen.get_rect().center)  # 画面の真ん中
```

- `=` の左は「新しい四角の**どこを**」、右は「**どこに**合わせるか」（[pygame.md](pygame.md#centerscreen_rectcenter-のように名前が-2-回出てくる理由)）
- 画面の大きさがほしいときは `screen.get_rect()`（例：`Player(screen.get_rect())` で画面の枠を渡す）

### `pygame.display.flip()`

| | |
|---|---|
| いつ使う | 毎フレーム、**全部描き終わった最後に 1 回** |
| 引数 | なし |
| 返り値 | `None` |
| 例 | [game.py:32](../../src/shooter/game.py#L32) |

- それまでの描画は裏で行われていて、flip で初めて表に出る。描きかけが見えないのでチラつかない
- 1 フレームに 2 回呼ぶと、描きかけの画面が一瞬見えてチカチカする。場面の `draw` には書かず、Game に 1 回だけ

---

## 5. 文字（Font）

### `pygame.font.Font(file, size)`

| | |
|---|---|
| いつ使う | 文字を出したいとき。`__init__` で 1 回作って使い回す |
| 引数 | `file`：フォントファイルの場所。`None` なら pygame の標準フォント／`size`：文字の大きさ |
| 返り値 | `Font` |
| 例 | [scenes.py:37](../../src/shooter/scenes.py#L37) |

- 標準フォント（`None`）は**日本語が出ない**。日本語は `pygame.font.SysFont("meiryo", size)` か日本語フォントのファイルを使う
- `pygame.init()` の後で作る

### `font.render(text, antialias, color)`

| | |
|---|---|
| いつ使う | 文字の絵を作るとき。中身が変わる文字（スコアなど）は毎フレーム |
| 引数 | `text`：文字列／`antialias`：`True` でふちがなめらか／`color`：`(R, G, B)` |
| 返り値 | 文字が描かれた `Surface`。大きさは文字に合わせて自動（72 の "GAME OVER" で 303×49） |
| 例 | [scenes.py:74](../../src/shooter/scenes.py#L74)、[scenes.py:90](../../src/shooter/scenes.py#L90) |

```python
text = self.font.render(f"SCORE: {self.score}", True, (255, 255, 255))
screen.blit(text, (10, 10))
```

---

## 6. Rect（位置と大きさ）

**画面のどこからどこまでかを、数字 4 つ `(x, y, 幅, 高さ)` で持つ。** 表示は `(left, top, width, height)` の順。

### 読み書きできる名前

| 名前 | 中身 | 種類 |
|---|---|---|
| `x` `y` | 左上の座標 | 数字 |
| `left` `right` `centerx` | 左端 / 右端 / 真ん中の x | 数字 |
| `top` `bottom` `centery` | 上端 / 下端 / 真ん中の y | 数字 |
| `width` `height` | 幅 / 高さ | 数字 |
| `center` `midtop` `midbottom` `topleft` など | 点の `(x, y)` | タプル |

- **代入すると四角ごと動く**（大きさはそのまま）。例：`rect.center = pos`
- **整数しか持てない**。小数を入れると丸められる。小数の位置は Vector2 で別に持つ（[pygame.md](pygame.md#rect-は整数しか持てない小数の移動がズレる)）
- 例：[enemy.py:28](../../src/shooter/enemy.py#L28)（`rect.top` で画面の外に出たか）、[bullet.py:19](../../src/shooter/bullet.py#L19)（`rect.bottom`）

### `rect.clamp_ip(枠)`

| | |
|---|---|
| いつ使う | キャラが画面の外に出ないように押し戻すとき |
| 引数 | `枠`：収めたい範囲の Rect（ふつうは `screen.get_rect()`） |
| 返り値 | `None`。**rect 自身が動く**（`_ip` は「その場で」の意味） |
| 例 | [player.py:41](../../src/shooter/player.py#L41) |

- 自分は変えずに、動かした新しい Rect がほしいときは `rect.clamp(枠)`（新しい Rect を返す）
- 例：幅 40 の四角を x=590 に置いて clamp すると x=560 に戻る

---

## 7. Vector2（向きと小数の位置）

### `pygame.Vector2(x, y)`

| | |
|---|---|
| いつ使う | ①移動の向きをまとめる ②小数の位置を持つ |
| 引数 | `x, y`、またはタプル（`pygame.Vector2(self.rect.center)`） |
| 返り値 | `Vector2`。`pygame.math.Vector2` と同じもの |
| 例 | [player.py:22](../../src/shooter/player.py#L22)、[player.py:27](../../src/shooter/player.py#L27) |

| 書き方 | 意味 |
|---|---|
| `v.x` / `v.y` | 中身 |
| `v1 + v2`、`v += v2` | 足し算 |
| `v * 数` | 長さを何倍かにする（`direction * SPEED * dt`） |
| `rect.center = v` | Rect に写す（ここで整数に丸められる） |

### `vector.length()`

| | |
|---|---|
| いつ使う | 長さを知りたいとき（何かキーが押されているか、など） |
| 引数 | なし |
| 返り値 | 長さ（`float`）。`Vector2(3, 4).length()` → `5.0` |
| 例 | [player.py:36](../../src/shooter/player.py#L36) |

### `vector.normalize()`

| | |
|---|---|
| いつ使う | 向きだけ残して長さを 1 にそろえたいとき（斜め移動が速くならないように） |
| 引数 | なし |
| 返り値 | **新しい** `Vector2`。元のベクトルは変わらない。`Vector2(3, 4).normalize()` → `[0.6, 0.8]` |
| 例 | [player.py:37](../../src/shooter/player.py#L37) |

- **長さ 0 だと `ValueError`**。`if v.length() > 0:` で確かめてから呼ぶ

---

## 8. Sprite（キャラ）

### `pygame.sprite.Sprite`（継承して使う）

| | |
|---|---|
| いつ使う | 動くもの・当たり判定するもの（自機・敵・弾）を作るとき |
| 必ず書くもの | `super().__init__()`、`self.image`（Surface）、`self.rect`（Rect） |
| 自分で書くもの | `update(self, dt)`：1 フレームぶんの動き |
| 例 | [player.py:14](../../src/shooter/player.py#L14)、[enemy.py:15](../../src/shooter/enemy.py#L15)、[bullet.py:8](../../src/shooter/bullet.py#L8) |

```python
class Enemy(pygame.sprite.Sprite):
    def __init__(self, bounds):
        super().__init__()
        self.image = pygame.Surface((40, 30))
        self.image.fill((255, 80, 80))
        self.rect = self.image.get_rect(left=x, bottom=bounds.top)

    def update(self, dt):
        ...
```

- `image` と `rect` は**この名前でないとだめ**。`group.draw` や当たり判定がこの名前を使う
- `super().__init__()` を忘れると Group に入れられない（`AttributeError: ... '_Sprite__g'`）

### `sprite.kill()`

| | |
|---|---|
| いつ使う | 画面の外に出た・倒されたキャラを消すとき |
| 引数 | なし |
| 返り値 | `None` |
| 例 | [enemy.py:29](../../src/shooter/enemy.py#L29)、[bullet.py:20](../../src/shooter/bullet.py#L20) |

- 入っている**全部の** Group から一度に取り出される
- まだどこかの Group に入っているかは `sprite.alive()`（True / False）

---

## 9. Group（キャラの箱）

### `pygame.sprite.Group()`

| | |
|---|---|
| いつ使う | キャラをまとめて動かす・描く・当たり判定するとき |
| 引数 | なし（最初から入れたいキャラを渡すこともできる） |
| 返り値 | 空の `Group` |
| 例 | [scenes.py:38](../../src/shooter/scenes.py#L38) |

- 1 体を複数の箱に入れてよい。「全員用」と「種類別（当たり判定用）」に分けるのが定番

| 箱 | 用途 |
|---|---|
| `all_sprites` | 全員。まとめて update・draw |
| `bullets` / `enemies` | 種類ごと。当たり判定用 |

### `group.add(*sprites)`

| | |
|---|---|
| いつ使う | キャラを作ったとき |
| 引数 | 入れたい Sprite（いくつでも） |
| 返り値 | `None` |
| 例 | [scenes.py:52](../../src/shooter/scenes.py#L52)、[scenes.py:53](../../src/shooter/scenes.py#L53) |

### `group.update(*args)`

| | |
|---|---|
| いつ使う | 毎フレーム、全員を動かすとき |
| 引数 | 渡したものが、そのまま全員の `update` に渡される（`group.update(dt)` → 各自の `update(dt)`） |
| 返り値 | `None` |
| 例 | [scenes.py:65](../../src/shooter/scenes.py#L65) |

### `group.draw(surface)`

| | |
|---|---|
| いつ使う | 毎フレーム、全員を描くとき |
| 引数 | `surface`：描く先（ふつうは画面） |
| 返り値 | ふつうは使わない |
| 例 | [scenes.py:73](../../src/shooter/scenes.py#L73) |

- 中で全員に `surface.blit(sprite.image, sprite.rect)` をしている

### そのほか

| 書き方 | やること |
|---|---|
| `len(group)` | 何体入っているか |
| `group.empty()` | 全員を箱から出す（Sprite 自体は消えない） |

---

## 10. 当たり判定

**どれも rect（四角）どうしが重なっているかで判定する。** 絵が丸くても判定は四角（形に合わせる方法は [pygame.md](pygame.md#当たり判定の形四角円マスク)）。

| 調べたい組み合わせ | 使うもの |
|---|---|
| 箱 × 箱（弾 × 敵） | `groupcollide` |
| 1 体 × 箱（自機 × 敵） | `spritecollideany` |

### `pygame.sprite.groupcollide(group1, group2, dokill1, dokill2)`

| | |
|---|---|
| いつ使う | 2 つの箱の中で、当たった組を全部探すとき |
| 引数 | `group1`・`group2`：調べる箱／`dokill1`・`dokill2`：`True` なら、当たったものをその箱から自動で `kill()` する |
| 返り値 | 辞書 `{group1 のキャラ: [当たった group2 のキャラのリスト]}`。当たりがなければ空の辞書 |
| 例 | [scenes.py:66](../../src/shooter/scenes.py#L66) |

```python
hits = pygame.sprite.groupcollide(self.enemies, self.bullets, True, True)
self.score += len(hits) * ENEMY_SCORE   # 倒した敵の数 × 点数
```

- `len(hits)` は当たった **group1 側**の数（ここでは倒した敵の数）

### `pygame.sprite.spritecollideany(sprite, group)`

| | |
|---|---|
| いつ使う | 1 体が箱の中の誰かに当たったかだけ知りたいとき |
| 引数 | `sprite`：調べる 1 体／`group`：相手の箱／（3 つ目に判定の形を渡せる：`pygame.sprite.collide_mask` など） |
| 返り値 | 当たった相手を **1 体**。誰にも当たっていなければ `None` |
| 例 | [scenes.py:68](../../src/shooter/scenes.py#L68) |

```python
if pygame.sprite.spritecollideany(self.player, self.enemies):
    ...  # ぶつかった
```

- `None` は `if` で偽になるので、そのまま `if` に入れてよい
- 何も消さない

---

## よくあるまちがい

| 症状・エラー | 原因 | 直し方 |
|---|---|---|
| `set_mode` で `TypeError` | `set_mode(600, 800)` | `set_mode((600, 800))` |
| ウィンドウが「応答なし」 | `pygame.event.get()` を毎フレーム呼んでいない | ループの中で毎回呼ぶ |
| 何も表示されない | `flip()` を呼んでいない | 描画の最後に `pygame.display.flip()` |
| 画面がチカチカする | `flip()` を 1 フレームに 2 回呼んでいる | Game で 1 回だけ |
| 前のフレームの絵が残って線になる | 背景を `fill` していない | 描画の最初に `screen.fill(BG_COLOR)` |
| ゆっくり動かしたいのに動かない・速さがズレる | Rect に小数を足している | 位置は Vector2 で持ち、Rect には写すだけ |
| 斜めだけ速い | 向きを正規化していない | `length() > 0` なら `normalize()` |
| `normalize` で `ValueError` | 長さ 0 のベクトル | `if v.length() > 0:` で確かめる |
| `Group.draw` で `AttributeError` | Sprite に `image` か `rect` がない、名前がちがう | `self.image` と `self.rect` を作る |
| Group に入れると `AttributeError: ... '_Sprite__g'` | `super().__init__()` を忘れている | `__init__` の最初で呼ぶ |
| 日本語が □ や小さい点になる | 標準フォント（`None`）を使っている | `SysFont("meiryo", size)` などを使う |
| `get_rect` で `NameError` | `get_rect(...)` だけを書いている | `絵.get_rect(...)` と、どの絵のものか書く |
