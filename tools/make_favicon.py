#!/usr/bin/env python3
"""生成站点 favicon：透明底 + 纯黑标志。

几何与 δ 全部照搬品牌规范 logo/make_assets.py，不在这里另定数值 ——
否则站上的图标会和规范漂开。

用法：
    python3 tools/make_favicon.py            # 用默认比例
    python3 tools/make_favicon.py 0.90       # 指定墨迹宽占比

输出到 assets/favicon-black-{16,32,48}.png 和 assets/favicon-black.ico，
页面（index.html）直接引用这几个文件。

━━━ 两个踩过的坑，改之前先看这段 ━━━

1. ratio 是「墨迹**宽**占图标宽的比例」，不是包围盒占比。
   标志宽高比 1.07:1，方形图标里高度方向天然更空。曾经按宽度对齐到 88%
   时，32px 的高度只占 78%，看上去仍然偏小。所以这个值要按视觉定，
   不要指望它同时把高度也填满。

2. ratio 有上限，超过会触边被切。
   实测 0.96 时 16px 的墨迹宽达到 100%（贴边），32px 也触边；
   0.90 是安全上限。调大后务必跑 --check 看是否触边。

已知取舍：δ=0.4 的缝在任何 favicon 尺寸下都是亚像素
（16px 约 0.27px，48px 约 0.82px），所以 16px 的三层结构必然粘连，
只剩 C 的外形。这是规范 δ 值决定的，不是渲染 bug —— 见品牌规范
GEOMETRY.md 第 6 节「δ 变换」。要保住 16px 的三层就得加大 δ，
那就不符合规范了，目前选择不这么做。
"""
import os
import struct
import sys
import zlib

import numpy as np

# ── 几何（照搬 logo/make_assets.py）────────────────────────────────────
A_PTS = [(2, 7.5), (12, 2), (22, 7.5), (18.363636, 9.5), (12, 6), (5.636364, 9.5)]
B_PTS = [(2, 11.5), (5.636364, 9.5), (12, 13), (14.727273, 11.5), (18.363636, 13.5), (12, 17)]


def c_pts(d):
    """底面 C 区域，整体下移 δ 后左右两边锚回原构造直线。"""
    t, h = d / 1.1, d / 2
    xr = (20.2 + d) / 1.1
    return [(62 / 11 - t, 13.5 + h), (12, 17 + d), (xr, 0.55 * xr + 3.4),
            (22 + t, 15.5 + h), (12, 21 + d), (2 - t, 15.5 + h)]


D_MONO = 0.40                    # 单色标准，规范规定不能比这更细
MARK_W = 20 + 2 * (D_MONO / 1.1)  # 标志墨迹宽度（24 单位画布里）
DEFAULT_RATIO = 0.90             # 墨迹宽占图标宽的比例，上限约 0.90
SIZES = (16, 32, 48)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets")


def raster(size, ratio, ss=16):
    """把标志按「墨迹宽 = size × ratio」居中渲染成 RGBA 数组。

    ss = 超采样倍数，先在高分辨率下判定覆盖再降采样，得到抗锯齿的 alpha。
    """
    big = size * ss
    k = size * ratio / MARK_W * ss        # 单位 → 大图像素
    # 标志在 24 单位画布里的包围盒中心
    cx = (1.636364 + 22.363636) / 2.0
    cy = (2.0 + 21.4) / 2.0
    axis = np.arange(big) + 0.5
    gx, gy = np.meshgrid(axis, axis)
    ux = (gx - big / 2) / k + cx          # 换算回标志自身坐标系
    uy = (gy - big / 2) / k + cy

    cov = np.zeros((big, big), dtype=bool)
    for pts in (A_PTS, B_PTS, c_pts(D_MONO)):
        n = len(pts)
        m = np.zeros((big, big), dtype=bool)
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            cond = (y1 > uy) != (y2 > uy)
            with np.errstate(divide="ignore", invalid="ignore"):
                xi = (x2 - x1) * (uy - y1) / (y2 - y1) + x1
            m ^= cond & (ux < xi)
        cov |= m

    cov = cov.reshape(size, ss, size, ss).mean(axis=(1, 3))
    out = np.zeros((size, size, 4), dtype=np.uint8)
    out[:, :, 3] = np.clip(cov * 255, 0, 255).astype(np.uint8)   # 黑色，只填 alpha
    return out


def write_png(path, rgba):
    h, w = rgba.shape[:2]
    raw = b"".join(b"\x00" + rgba[y].tobytes() for y in range(h))

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data
                + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
                + chunk(b"IDAT", zlib.compress(raw, 9))
                + chunk(b"IEND", b""))


def write_ico(path, ratio):
    """多尺寸 ICO，内嵌 PNG（Vista 起支持）。"""
    imgs = []
    for s in SIZES:
        tmp = os.path.join(OUT, f".tmp-{s}.png")
        write_png(tmp, raster(s, ratio))
        with open(tmp, "rb") as f:
            imgs.append((s, f.read()))
        os.remove(tmp)
    hdr = struct.pack("<HHH", 0, 1, len(imgs))
    dirs, blobs, off = b"", b"", 6 + 16 * len(imgs)
    for s, data in imgs:
        dirs += struct.pack("<BBBBHHII", s % 256, s % 256, 0, 0, 1, 32, len(data), off)
        blobs += data
        off += len(data)
    with open(path, "wb") as f:
        f.write(hdr + dirs + blobs)


def measure(ratio):
    """返回每个尺寸的墨迹包围盒，并检查是否触边。"""
    out = []
    for s in SIZES:
        a = raster(s, ratio)
        ys, xs = np.nonzero(a[:, :, 3] > 10)
        if len(xs) == 0:
            raise SystemExit(f"{s}px 渲染为空，ratio 可能是 0")
        w, h = xs.max() - xs.min() + 1, ys.max() - ys.min() + 1
        touches = xs.min() == 0 or ys.min() == 0 or xs.max() == s - 1 or ys.max() == s - 1
        out.append((s, w, h, touches))
    return out


def check(ratio):
    print(f"ratio = {ratio}")
    bad = False
    for s, w, h, touches in measure(ratio):
        flag = "触边，会被切！" if touches else ""
        if touches:
            bad = True
        print(f"  {s:2d}px  墨迹 {w:2d}x{h:2d}  宽 {w / s * 100:3.0f}%  高 {h / s * 100:3.0f}%  {flag}")
    if bad:
        print("\n比例过大，把 ratio 调小（上限约 0.90）")
    return not bad


def main():
    args = [a for a in sys.argv[1:] if a != "--check"]
    ratio = float(args[0]) if args else DEFAULT_RATIO
    ok = check(ratio)
    if "--check" in sys.argv:
        raise SystemExit(0 if ok else 1)
    if not ok:
        raise SystemExit("拒绝写入：比例会触边，先调小 ratio")

    os.makedirs(OUT, exist_ok=True)
    for s in SIZES:
        write_png(os.path.join(OUT, f"favicon-black-{s}.png"), raster(s, ratio))
    write_ico(os.path.join(OUT, "favicon-black.ico"), ratio)
    print(f"\n已写入 assets/favicon-black-{{16,32,48}}.png 和 favicon-black.ico")


if __name__ == "__main__":
    main()
