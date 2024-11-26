import os
import sys
import pygame as pg
import random
import time


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
    return x_bound, y_bound

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

    vx, vy = 5, 5
    
    clock = pg.time.Clock()
    tmr = 0
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, delta in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += delta[0]
                sum_mv[1] += delta[1]

        # こうかとんが画面外に出ていないか判定
        if not all(check_bound(kk_rct)):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 移動をキャンセル

         # 爆弾の移動
        bb_rct.move_ip(vx, vy)

        # 爆弾が画面外に出たら速度を反転
        if bb_rct.left < 0 or bb_rct.right > WIDTH:
            vx = -vx
        if bb_rct.top < 0 or bb_rct.bottom > HEIGHT:
            vy = -vy

        # 爆弾とこうかとんを描画
        screen.blit(bb_img, bb_rct)
        kk_rct.move_ip(sum_mv)
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
