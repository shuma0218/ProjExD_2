import os
import sys
import pygame as pg
import random
import time
import math


WIDTH, HEIGHT = 1100, 650
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check_bound(rect):
    """オブジェクトが画面内か画面外かを判定する関数
    Args:
        rect (pg.Rect): 判定するRectオブジェクト
    Returns:
        tuple[bool, bool]: 横方向, 縦方向の真理値タプル (True: 画面内, False: 画面外)
    """
    x_bound = 0 <= rect.left and rect.right <= WIDTH
    y_bound = 0 <= rect.top and rect.bottom <= HEIGHT
    return [x_bound, y_bound]

def game_over(screen: pg.Surface) -> None:
    """ゲームオーバー時の画面を表示する関数
    Args:
        screen (pg.Surface): ゲーム画面のSurfaceオブジェクト
    """
    # 画面をブラックアウト
    overlay = pg.Surface((WIDTH, HEIGHT))  # 全画面サイズのSurface
    overlay.fill((0, 0, 0))  # 黒色で塗りつぶし
    overlay.set_alpha(128)  # 半透明設定
    screen.blit(overlay, (0, 0))  # 画面に適用

    # 泣いているこうかとん画像
    crying_img = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)  # 画像を0.9倍に拡大
    crying_rect_r = crying_img.get_rect(center=(WIDTH // 2 + 200, HEIGHT // 2))
    crying_rect_l = crying_img.get_rect(center=(WIDTH // 2 - 200, HEIGHT // 2))  # 画面中央付近に配置
    screen.blit(crying_img, crying_rect_r)
    screen.blit(crying_img, crying_rect_l)  # 画面に貼り付け

    # 「Game Over」の文字
    font = pg.font.Font(None, 80)  # フォントサイズを80に設定
    text = font.render("Game Over", True, (255, 255, 255))  # 白色で文字作成
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # 中央より少し上に配置
    screen.blit(text, text_rect)  # 画面に貼り付け
    
    pg.display.update()  # 画面更新
    time.sleep(5)  # 5秒間表示

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """サイズの異なる爆弾Surfaceのリストと加速度リストを生成する関数
    Returns:
        tuple[list[pg.Surface], list[int]]: 爆弾Surfaceリストと加速度リスト
    """
    bb_imgs = []  # 爆弾Surfaceのリスト
    bb_accs = [a for a in range(1, 11)]  # 加速度リスト（1～10）

    for r in range(1, 11):  # 半径を1倍～10倍に拡大
        bb_img = pg.Surface((20 * r, 20 * r), pg.SRCALPHA)
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)  # 爆弾を描画
        bb_imgs.append(bb_img)  # リストに追加

    return bb_imgs, bb_accs

def get_kk_img(sum_mv: tuple[int, int]) -> pg.Surface:
    """
    移動量の合計値タプルに対応する向きのこうかとん画像Surfaceを返す関数。

    Args:
        sum_mv (tuple[int, int]): 移動量の合計値タプル (dx, dy)

    Returns:
        pg.Surface: 移動量に対応する向きの画像Surface
    """
    # こうかとん画像の辞書を準備
    kk_imgs = {
        (0, 0): pg.image.load("fig/3.png"),  # 静止画像
        (5, 0): pg.transform.flip(pg.image.load("fig/3.png"), True, False),  # 右向き
        (-5, 0): pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 1.0),  # 左向き
        (0, 5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 90, 1.0),  # 下向き
        (0, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -90, 1.0),  # 上向き
        (5, 5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -135, 1.0),  # 右下
        (5, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), -45, 1.0),  # 右上
        (-5, 5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 135, 1.0),  # 左下
        (-5, -5): pg.transform.rotozoom(pg.image.load("fig/3.png"), 45, 1.0),  # 左上
    }

    # 合計移動量が辞書にない場合は静止画像を返す
    return kk_imgs.get(sum_mv, kk_imgs[(0, 0)])

def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float]) -> tuple[float, float]:
    """
    爆弾から見てこうかとんの位置を計算し、方向ベクトルを正規化して返す。

    Args:
        org (pg.Rect): 爆弾のRectオブジェクト（起点）
        dst (pg.Rect): こうかとんのRectオブジェクト（目標）
        current_xy (tuple[float, float]): 現在の爆弾の速度ベクトル (vx, vy)

    Returns:
        tuple[float, float]: 次の移動速度ベクトル (vx, vy)
    """
    # 爆弾（org）からこうかとん（dst）への差ベクトルを計算
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery

    # ノルム（ベクトルの長さ）を計算
    norm = math.sqrt(dx**2 + dy**2)

    # こうかとんとの距離が300以上の場合のみ方向を更新
    if norm >= 300:
        # ノルムが0ではない場合、方向を正規化して速度を計算
        if norm != 0:
            dx /= norm
            dy /= norm

        # ベクトルの長さを√50に調整
        dx *= math.sqrt(50)
        dy *= math.sqrt(50)

        return dx, dy
    else:
        # 距離が300未満の場合は慣性を保持
        return current_xy

def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")
    bg_img = pg.transform.scale(bg_img, (WIDTH, HEIGHT))    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200
    DELTA = {
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, 5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (5, 0),
    }

    bb_img = pg.Surface((20, 20))  # 爆弾のサイズ (20x20)
    bb_img.set_colorkey((0, 0, 0))  # 黒い部分を透明に
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)  # 赤い円を描画
    bb_rct = bb_img.get_rect()
    bb_rct.topleft = (random.randint(0, WIDTH-20), random.randint(0, HEIGHT-20))

    # 爆弾画像と加速度リストの初期化
    bb_imgs, bb_accs = init_bb_imgs()
    bb_rct = bb_imgs[0].get_rect(center=(WIDTH // 2, HEIGHT // 2))
    vx, vy = 5, 5  # 初期速度

    
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        #こうかとん移動
        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, delta in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += delta[0]
                sum_mv[1] += delta[1]
        
        kk_img = get_kk_img(tuple(sum_mv))
        kk_rct.move_ip(sum_mv)

        # こうかとんが画面外に出ていないか判定
        if not all(check_bound(kk_rct)):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 移動をキャンセル

        # 爆弾の画像と速度の更新
        current_stage = min(tmr // 500, 9)  # tmr に応じて段階を0~9
        bb_img = bb_imgs[current_stage]
        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))
        avx = vx * bb_accs[current_stage]
        avy = vy * bb_accs[current_stage]

        bb_rct.move_ip(avx, avy)  # 爆弾の移動
        # 爆弾が画面外に出たら速度を反転
        if bb_rct.left < 0 or bb_rct.right > WIDTH:
            vx = -vx
        if bb_rct.top < 0 or bb_rct.bottom > HEIGHT:
            vy = -vy

        # 爆弾とこうかとんを描画
        screen.blit(bb_img, bb_rct)
        screen.blit(kk_img, kk_rct)

        # 衝突判定
        if kk_rct.colliderect(bb_rct):
            game_over(screen)
            return    # 衝突した場合、main関数を終了
        pg.display.update()
        tmr += 1
        clock.tick(50)


if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
