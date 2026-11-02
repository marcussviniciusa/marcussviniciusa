"""Gera assets/cidade.svg: o gráfico de contribuições do último ano como uma cidade à noite, um prédio por dia.

Uso: python3 tools/cidade.py
Lê tools/dados/contribuicoes.json (calendário do GraphQL: semanas > dias, com contagem e quartil).
Só biblioteca padrão. Mesma janela de terminal do terminal.svg, para os dois parecerem um sistema só.
Ideia da cidade isométrica: Giorgi Kobaidze (github.com/georgekobaidze), refeita do zero aqui.
"""
import json
import math
import random
from datetime import date
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "tools" / "dados"

LARG = 900
BARRA = 34
TW, TH = 24, 12  # losango do chão (isométrico 2:1)
ALT_MAX = 128  # altura do prédio mais alto
FONTE = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace'
MESES = "jan fev mar abr mai jun jul ago set out nov dez".split()

COR = {
    "fundo": "#0d1117", "barra": "#161b22", "borda": "#30363d", "texto": "#f0f6fc", "fraco": "#7d8590",
    "verde": "#7ee787", "azul": "#79c0ff", "ceu1": "#05070d", "ceu2": "#0b1424",
    "chao": "#0b111a", "chao_linha": "#18212e",
    "janela": "#8be3ff", "janela_quente": "#ffcf70", "janela_apagada": "#0a1525",
}
# Por quartil do GitHub (1 a 4): teto, parede esquerda, parede direita.
PREDIO = {
    1: ("#2a5591", "#10243f", "#173259"),
    2: ("#2f7fdc", "#132d52", "#1c416f"),
    3: ("#46a9f5", "#163764", "#215084"),
    4: ("#74e3ff", "#1a4478", "#275d9c"),
}
QUARTIL = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2, "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}


def milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def pts(*xy: tuple[float, float]) -> str:
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in xy)


def main() -> None:
    cal = json.loads((DADOS / "contribuicoes.json").read_text(encoding="utf-8"))
    cal = cal["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    semanas = cal["weeks"]
    dias = [(w, d["weekday"], d) for w, s in enumerate(semanas) for d in s["contributionDays"]]
    contagens = sorted(d["contributionCount"] for _, _, d in dias if d["contributionCount"] > 0)
    teto = contagens[int(len(contagens) * 0.98)]  # o recorde não achata a cidade
    recorde = max(dias, key=lambda t: t[2]["contributionCount"])

    n_sem = len(semanas)
    # Posição de tela da célula (semana w, dia da semana d): w desce para a direita, d desce para a esquerda.
    x_min, x_max = -6 * TW / 2, (n_sem - 1) * TW / 2
    ox = LARG / 2 - (x_min + x_max) / 2
    oy = BARRA + 64 + ALT_MAX
    alt = int(oy + (n_sem - 1 + 6) * TH / 2 + TH + 74)

    def tela(w: float, d: float) -> tuple[float, float]:
        return ox + (w - d) * TW / 2, oy + (w + d) * TH / 2

    rnd = random.Random(2025)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{LARG}" height="{alt}" viewBox="0 0 {LARG} {alt}" '
        f'role="img" aria-labelledby="t d">',
        '<title id="t">qos cidade: as contribuições do último ano como uma cidade</title>',
        f'<desc id="d">Cidade isométrica com um prédio por dia do último ano; a altura é a quantidade de '
        f'contribuições. {milhar(cal["totalContributions"])} contribuições em 365 dias.</desc>',
        "<defs>",
        f'<linearGradient id="ceu" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{COR["ceu1"]}"/>'
        f'<stop offset="1" stop-color="{COR["ceu2"]}"/></linearGradient>',
        '<radialGradient id="halo"><stop offset="0" stop-color="#dbe9ff" stop-opacity=".35"/>'
        '<stop offset="1" stop-color="#dbe9ff" stop-opacity="0"/></radialGradient>',
        f'<clipPath id="tela"><rect x="1" y="{BARRA + 1}" width="{LARG - 2}" height="{alt - BARRA - 2}" rx="11"/>'
        "</clipPath>",
        "</defs>",
        "<style>",
        f"text {{ font-family: {FONTE}; white-space: pre; }}",
        ".pr { transform: scaleY(0); animation: sobe .7s cubic-bezier(.2,.8,.2,1) forwards; }",
        "@keyframes sobe { to { transform: scaleY(1); } }",
        ".lz { opacity: 0; animation: acende .5s ease-out forwards; }",
        "@keyframes acende { to { opacity: 1; } }",
        ".pisca { animation: falha 3.7s steps(1) infinite; }",
        "@keyframes falha { 0%, 62%, 70%, 100% { opacity: 1; } 64%, 68% { opacity: .15; } }",
        ".estrela { animation: brilha 3s ease-in-out infinite; }",
        "@keyframes brilha { 0%, 100% { opacity: .25; } 50% { opacity: 1; } }",
        ".aviao { animation: voa 26s linear infinite; }",
        f"@keyframes voa {{ from {{ transform: translate(-60px, 0); }} to {{ transform: translate({LARG + 60}px, -26px); }} }}",
        ".farol { animation: farol 1.1s steps(1) infinite; }",
        "@keyframes farol { 0%, 100% { opacity: 1; } 50% { opacity: 0; } }",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{LARG - 1}" height="{alt - 1}" rx="12" fill="{COR["fundo"]}" '
        f'stroke="{COR["borda"]}"/>',
        f'<g clip-path="url(#tela)"><rect x="0" y="{BARRA}" width="{LARG}" height="{alt - BARRA}" fill="url(#ceu)"/>',
    ]

    # Estrelas no céu (atrás de tudo), lua com halo e o avião cruzando.
    for _ in range(70):
        x, y = rnd.uniform(20, LARG - 20), rnd.uniform(BARRA + 50, oy + 40)
        out.append(f'<circle class="estrela" cx="{x:.1f}" cy="{y:.1f}" r="{rnd.choice((0.6, 0.8, 1.1)):.1f}" '
                   f'fill="#cfe3ff" style="animation-delay:-{rnd.uniform(0, 3):.2f}s"/>')
    lua_x, lua_y = LARG - 92, BARRA + 86
    out.append(f'<circle cx="{lua_x}" cy="{lua_y}" r="46" fill="url(#halo)"/>')
    out.append(f'<circle cx="{lua_x}" cy="{lua_y}" r="15" fill="#eef4ff"/>')
    out.append(f'<circle cx="{lua_x + 7}" cy="{lua_y - 5}" r="13" fill="{COR["ceu1"]}"/>')
    out.append(f'<g class="aviao"><g transform="translate(0 {BARRA + 132})">'
               '<rect x="-7" y="-1" width="14" height="2" rx="1" fill="#1f2937"/>'
               '<circle class="farol" cx="-7" cy="0" r="1.3" fill="#ff5f57"/>'
               '<circle class="farol" cx="7" cy="0" r="1.3" fill="#ffffff" style="animation-delay:-.55s"/></g></g>')

    # Chão: todos os dias, inclusive os vazios (terrenos baldios).
    for w, d, _ in dias:
        cx, cy = tela(w, d)
        out.append(f'<polygon points="{pts((cx, cy - TH / 2), (cx + TW / 2, cy), (cx, cy + TH / 2), (cx - TW / 2, cy))}" '
                   f'fill="{COR["chao"]}" stroke="{COR["chao_linha"]}" stroke-width=".6"/>')

    # Prédios, de trás para a frente (algoritmo do pintor).
    for w, d, dia in sorted(dias, key=lambda t: (t[0] + t[1], t[1])):
        c = dia["contributionCount"]
        if c == 0:
            continue
        q = max(1, QUARTIL.get(dia["contributionLevel"], 1))
        h = 6 + (ALT_MAX - 6) * math.sqrt(min(c, teto) / teto)
        teto_c, esq_c, dir_c = PREDIO[q]
        cx, cy = tela(w, d)
        m = 0.8  # recuo para os prédios não grudarem
        L, B, R, T = (cx - TW / 2 + m, cy), (cx, cy + TH / 2 - m / 2), (cx + TW / 2 - m, cy), (cx, cy - TH / 2 + m / 2)
        up = lambda p: (p[0], p[1] - h)  # noqa: E731
        atraso = 0.25 + w * 0.032 + rnd.uniform(0, 0.12)
        g = [f'<g class="pr" style="animation-delay:{atraso:.2f}s;transform-origin:{cx:.1f}px {B[1]:.1f}px">',
             f'<polygon points="{pts(L, B, up(B), up(L))}" fill="{esq_c}"/>',
             f'<polygon points="{pts(B, R, up(R), up(B))}" fill="{dir_c}"/>',
             f'<polygon points="{pts(up(L), up(T), up(R), up(B))}" fill="{teto_c}"/>']
        # Janelas: linhas a cada 7 px nas duas paredes; a maioria acesa, algumas quentes, poucas piscando.
        acesas, quentes, apagadas, piscam = [], [], [], []
        for a, b in ((L, B), (B, R)):
            for f in (0.3, 0.7):
                bx, by = a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1])
                y = by - 6
                while y - 4 > by - h + 3:
                    rect = f"M{bx - 1.3:.1f} {y - 3.4:.1f}h2.6v3.4h-2.6z"
                    sorte = rnd.random()
                    if sorte < 0.04:
                        piscam.append(rect)
                    elif sorte < 0.12:
                        quentes.append(rect)
                    elif sorte < 0.62:
                        acesas.append(rect)
                    else:
                        apagadas.append(rect)
                    y -= 7
        if apagadas:
            g.append(f'<path d="{"".join(apagadas)}" fill="{COR["janela_apagada"]}"/>')
        luz = atraso + 0.55 + rnd.uniform(0, 0.6)
        for lista, cor, extra in ((acesas, COR["janela"], ""), (quentes, COR["janela_quente"], ""),
                                  (piscam, COR["janela"], " pisca")):
            if lista:
                g.append(f'<g class="lz" style="animation-delay:{luz:.2f}s"><path class="{extra.strip()}" '
                         f'd="{"".join(lista)}" fill="{cor}"/></g>' if extra else
                         f'<path class="lz" style="animation-delay:{luz:.2f}s" d="{"".join(lista)}" fill="{cor}"/>')
        if (w, d) == (recorde[0], recorde[1]):
            # O recorde ganha antena com luz de aviação.
            topo = up(T)
            g.append(f'<line x1="{cx:.1f}" y1="{topo[1] + TH / 2:.1f}" x2="{cx:.1f}" y2="{topo[1] - 10:.1f}" '
                     f'stroke="#9fb3c8" stroke-width="1"/>')
            g.append(f'<circle class="farol" cx="{cx:.1f}" cy="{topo[1] - 11:.1f}" r="2" fill="#ff5f57"/>')
        g.append("</g>")
        out.extend(g)
    out.append("</g>")

    # Barra da janela e textos.
    out.append(f'<path d="M0.5 12.5a12 12 0 0 1 12-12h{LARG - 25}a12 12 0 0 1 12 12v{BARRA - 12}h-{LARG - 1}z" '
               f'fill="{COR["barra"]}"/>')
    out.append(f'<line x1="0.5" y1="{BARRA + .5}" x2="{LARG - .5}" y2="{BARRA + .5}" stroke="{COR["borda"]}"/>')
    for i, cor in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        out.append(f'<circle cx="{22 + i * 20}" cy="{BARRA / 2 + .5}" r="6" fill="{cor}"/>')
    out.append(f'<text x="{LARG / 2}" y="{BARRA / 2 + 5}" text-anchor="middle" font-size="12.5" '
               f'fill="{COR["fraco"]}">marcus@quantiumcode: ~ — zsh</text>')
    out.append(f'<text x="26" y="{BARRA + 28}" font-size="12.5"><tspan fill="{COR["verde"]}">marcus@quantiumcode'
               f'</tspan><tspan fill="{COR["texto"]}">:</tspan><tspan fill="{COR["azul"]}">~</tspan><tspan '
               f'fill="{COR["texto"]}">$ qos cidade --365d </tspan><tspan fill="{COR["fraco"]}"># um prédio por dia'
               f'</tspan></text>')

    dr = date.fromisoformat(recorde[2]["date"])
    ativos = sum(1 for _, _, d in dias if d["contributionCount"] > 0)
    infos = [
        [(milhar(cal["totalContributions"]), COR["azul"]), (" contribuições · últimos 365 dias", COR["fraco"])],
        [("dia mais cheio ", COR["fraco"]), (f"{dr.day} {MESES[dr.month - 1]}", COR["texto"]),
         (" · ", COR["fraco"]), (str(recorde[2]["contributionCount"]), COR["texto"])],
        [(str(ativos), COR["texto"]), (" dias ativos", COR["fraco"])],
    ]
    for i, partes in enumerate(infos):
        spans = "".join(f'<tspan fill="{cor}">{escape(t)}</tspan>' for t, cor in partes)
        out.append(f'<text x="{LARG - 26}" y="{oy - 30 + i * 18}" text-anchor="end" font-size="12">{spans}</text>')

    # Legenda.
    ly = alt - 24
    out.append(f'<text x="26" y="{ly + 4}" font-size="11" fill="{COR["fraco"]}">quieto</text>')
    for i, cor in enumerate([COR["chao"]] + [PREDIO[q][0] for q in (1, 2, 3, 4)]):
        out.append(f'<rect x="{78 + i * 13}" y="{ly - 5}" width="10" height="10" rx="2" fill="{cor}" '
                   f'stroke="{COR["chao_linha"]}"/>')
    out.append(f'<text x="{78 + 5 * 13 + 4}" y="{ly + 4}" font-size="11" fill="{COR["fraco"]}">arranha-céu</text>')
    out.append("</svg>")

    (RAIZ / "assets" / "cidade.svg").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"cidade.svg: {LARG}x{alt}, {ativos} prédios, teto da escala {teto}, recorde {recorde[2]['date']}")


if __name__ == "__main__":
    main()
