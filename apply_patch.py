#!/usr/bin/env python3
"""샤이닝 소울 II 한글 패치 적용 스크립트 (파이썬 3, 외부 라이브러리 불필요)
사용: python3 apply_patch.py "Shining Soul II (Japan).gba" [패치.bps] [출력.gba]
  - 패치 파일을 생략하면 같은 폴더의 'ShiningSoul2_KO.bps' 를 씁니다.
  - 원본은 일본판(CRC32 7B39A7B2)이어야 합니다."""
import sys, os, zlib

def dec(p, i):
    n = 0; s = 1
    while True:
        x = p[i]; i += 1; n += (x & 0x7f) * s
        if x & 0x80: break
        s <<= 7; n += s
    return n, i

def apply(src, pt):
    if pt[:4] != b"BPS1": raise SystemExit("올바른 BPS 패치가 아닙니다.")
    i = 4; ss, i = dec(pt, i); ts, i = dec(pt, i); ms, i = dec(pt, i); i += ms
    need = int.from_bytes(pt[-12:-8], "little"); want = int.from_bytes(pt[-8:-4], "little")
    if len(src) != ss or zlib.crc32(src) & 0xffffffff != need:
        raise SystemExit("원본 ROM 이 맞지 않습니다. 일본판 'Shining Soul II (Japan)' (CRC32 %08X) 을 사용하세요." % need)
    out = bytearray(ts); o = 0; sro = 0; tro = 0; end = len(pt) - 12
    while i < end:
        v, i = dec(pt, i); cmd = v & 3; ln = (v >> 2) + 1
        if cmd == 0: out[o:o+ln] = src[o:o+ln]; o += ln
        elif cmd == 1: out[o:o+ln] = pt[i:i+ln]; i += ln; o += ln
        else:
            d, i = dec(pt, i); d = -(d >> 1) if d & 1 else d >> 1
            if cmd == 2: sro += d; out[o:o+ln] = src[sro:sro+ln]; sro += ln; o += ln
            else:
                tro += d
                for _ in range(ln): out[o] = out[tro]; o += 1; tro += 1
    if zlib.crc32(bytes(out)) & 0xffffffff != want: raise SystemExit("패치 결과 검증에 실패했습니다.")
    return bytes(out)

if __name__ == "__main__":
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    here = os.path.dirname(os.path.abspath(__file__))
    rom = sys.argv[1]
    bps = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "ShiningSoul2_KO.bps")
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(os.path.dirname(os.path.abspath(rom)), "Shining Soul II (Japan) 한글.gba")
    res = apply(open(rom, "rb").read(), open(bps, "rb").read())
    open(out, "wb").write(res)
    print("완료:", out, "(%d 바이트, CRC32 %08X)" % (len(res), zlib.crc32(res) & 0xffffffff))
