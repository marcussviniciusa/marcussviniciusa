"""Desenha o rosto da foto em caracteres (arte ASCII) e grava o resultado em JSON.

Uso: python3 tools/rosto.py
Entrada: tools/dados/foto.jpg e tools/dados/mascara.png (a máscara sai do tools/recorte.swift).
Saída: tools/dados/rosto.json, com as linhas e o tom de cada caractere (0 = escuro, 3 = claro).
Precisa do ImageMagick (magick) só para ler os pixels.
"""
import json
import math
import subprocess
from pathlib import Path

DADOS = Path(__file__).parent / "dados"
LADO = 460
COLUNAS = 62
CORTE = (100, 18, 360, 350)  # x0, y0, x1, y1 na foto de 460x460: cabeça, pescoço e ombros
GAMA = 1.3
REALCE = 1.7  # afasta cada célula da média dos vizinhos: olhos, sobrancelhas e barba ganham forma
TRACOS = 0.04  # fração das bordas mais fortes que vira traço (| / \ _)
# Do mais denso ao mais vazio.
RAMPA = "@%#MW&8BgN$Hm0QOdbqpkhaoZwXUYJCLzcvunxrjft/|()1{}[]?-_+~<>i!lI;:,\"^`'. "


def cinza(arq: Path) -> list[list[int]]:
    bruto = subprocess.run(
        ["magick", str(arq), "-colorspace", "Gray", "-resize", f"{LADO}x{LADO}!", "-depth", "8", "gray:-"],
        check=True, capture_output=True).stdout
    return [list(bruto[i * LADO:(i + 1) * LADO]) for i in range(LADO)]


def main() -> None:
    lum, msk = cinza(DADOS / "foto.jpg"), cinza(DADOS / "mascara.png")
    x0, y0, x1, y1 = CORTE
    cw = (x1 - x0) / COLUNAS
    ch = cw * 2.05  # a linha do terminal tem ~2x a largura do caractere
    linhas = int((y1 - y0) / ch)

    val = [[0.0] * COLUNAS for _ in range(linhas)]
    cob = [[0.0] * COLUNAS for _ in range(linhas)]
    for r in range(linhas):
        for c in range(COLUNAS):
            soma = n = m_tot = 0.0
            for y in range(int(y0 + r * ch), min(int(y0 + (r + 1) * ch), LADO)):
                for x in range(int(x0 + c * cw), min(int(x0 + (c + 1) * cw), LADO)):
                    m = msk[y][x] / 255
                    m_tot += m
                    soma += lum[y][x] * m
                    n += 1
            cob[r][c] = m_tot / max(n, 1)
            val[r][c] = soma / m_tot if m_tot > 0 else 0.0

    dentro = [(r, c) for r in range(linhas) for c in range(COLUNAS) if cob[r][c] >= 0.45]

    # Equaliza os tons só dentro da pessoa.
    tom = [[0.0] * COLUNAS for _ in range(linhas)]
    for i, (r, c) in enumerate(sorted(dentro, key=lambda rc: val[rc[0]][rc[1]])):
        tom[r][c] = (i / max(len(dentro) - 1, 1)) ** GAMA

    base = [linha[:] for linha in tom]
    for r, c in dentro:
        viz = [base[rr][cc] for rr in range(r - 1, r + 2) for cc in range(c - 2, c + 3)
               if 0 <= rr < linhas and 0 <= cc < COLUNAS and cob[rr][cc] >= 0.45]
        media = sum(viz) / len(viz)
        tom[r][c] = min(1.0, max(0.0, base[r][c] + REALCE * (base[r][c] - media)))

    traco = {}
    grads = []
    for r, c in dentro:
        if 0 < r < linhas - 1 and 0 < c < COLUNAS - 1:
            gx = (tom[r][c + 1] - tom[r][c - 1]) / 2
            gy = (tom[r + 1][c] - tom[r - 1][c]) / 2
            grads.append((math.hypot(gx, gy), r, c, gx, gy))
    grads.sort(reverse=True)
    for _, r, c, gx, gy in grads[: int(len(grads) * TRACOS)]:
        ang = math.degrees(math.atan2(gy, gx)) % 180  # a borda é perpendicular ao gradiente
        if ang < 22.5 or ang >= 157.5:
            traco[(r, c)] = "|"
        elif ang < 67.5:
            traco[(r, c)] = "\\"
        elif ang < 112.5:
            traco[(r, c)] = "_"
        else:
            traco[(r, c)] = "/"

    texto, tons = [], []
    for r in range(linhas):
        s = t = ""
        for c in range(COLUNAS):
            if cob[r][c] < 0.45:
                s, t = s + " ", t + " "
            elif (r, c) in traco:
                s, t = s + traco[(r, c)], t + "2"
            else:
                s += RAMPA[int(round((1 - tom[r][c]) * (len(RAMPA) - 2)))]  # nunca o espaço dentro da pessoa
                t += str(min(3, int(tom[r][c] * 4)))
        texto.append(s.rstrip())
        tons.append(t[: len(s.rstrip())])

    (DADOS / "rosto.json").write_text(
        json.dumps({"colunas": COLUNAS, "linhas": texto, "tons": tons}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"rosto: {COLUNAS}x{linhas}")


if __name__ == "__main__":
    main()
