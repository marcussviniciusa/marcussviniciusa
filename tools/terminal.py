"""Gera assets/terminal.svg: uma janela de terminal que roda `qos fetch` e mostra o rosto em ASCII e a ficha.

Uso: python3 tools/terminal.py
Lê tools/dados/rosto.json (do tools/rosto.py) e tools/dados/contribuicoes.json (calendário do GraphQL).
Só biblioteca padrão. As animações são CSS dentro do SVG, a única forma que o GitHub deixa rodar num README.
"""
import json
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "tools" / "dados"

REPOSITORIOS, PRIVADOS = 224, 222  # gh api 'user/repos?affiliation=owner' em 02/11/2026, já com este repositório

FICHA = [
    ("Host", "QuantiumCode"),
    ("Cargo", "fundador e desenvolvedor"),
    ("Uptime", "no ar desde mar/2024"),
    ("OS", "macOS, iOS, Android, Linux"),
    ("Shell", "zsh, Claude Code"),
    None,
    ("Faço.Web", "sistemas web sob medida, SaaS"),
    ("Faço.Mobile", "apps iOS e Android"),
    ("Faço.IA", "agentes de IA, automações de WhatsApp"),
    None,
    ("Stack.Back", "Go, Node, NestJS, PostgreSQL"),
    ("Stack.Front", "Next.js, React, TypeScript"),
    ("Stack.Mobile", "Swift, Kotlin"),
    ("Stack.Infra", "Docker, LiveKit, Tauri"),
]
CONTATO = [
    ("Site", "quantiumcode.com"),
    ("LinkedIn", "in/marcussviniciusa"),
    ("E-mail", "contato@quantiumcode.com"),
]
DESTAQUE = {"QuantiumCode"}  # valores na cor da marca

# Medidas (px). A largura de cada linha é travada com textLength, então qualquer fonte monoespaçada alinha.
LARG = 900
BARRA = 34
MARGEM = 26
ARTE_FONTE, ARTE_CW, ARTE_LH = 11, 6.6, 13.6
FICHA_FONTE, FICHA_CW, FICHA_LH = 12.5, 7.5, 19.5
FICHA_COLS = 56
FONTE = 'ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace'

COR = {
    "fundo": "#0d1117", "barra": "#161b22", "borda": "#30363d",
    "chave": "#ffa657", "valor": "#a5d6ff", "fraco": "#484f58", "texto": "#f0f6fc",
    "verde": "#7ee787", "azul": "#79c0ff", "marca": "#b392f0",
    "tons": ["#2d333b", "#6e7681", "#c9d1d9", "#ffffff"],
}


def milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def numeros() -> dict:
    cal = json.loads((DADOS / "contribuicoes.json").read_text(encoding="utf-8"))
    cal = cal["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    dias = [d for semana in cal["weeks"] for d in semana["contributionDays"]]
    seq = maior = 0
    for d in dias:
        seq = seq + 1 if d["contributionCount"] > 0 else 0
        maior = max(maior, seq)
    return {
        "total": cal["totalContributions"],
        "ativos": sum(1 for d in dias if d["contributionCount"] > 0),
        "sequencia": maior,
        "recorde": max(d["contributionCount"] for d in dias),
    }


def spans(partes: list[tuple[str, str]]) -> str:
    return "".join(f'<tspan fill="{cor}">{escape(txt)}</tspan>' for txt, cor in partes)


def linha_ficha(chave: str, valor: str) -> list[tuple[str, str]]:
    ini, fim = f". {chave}: ", f" {valor}"
    pontos = "." * max(1, FICHA_COLS - len(ini) - len(fim))
    cor_valor = COR["marca"] if valor in DESTAQUE else COR["valor"]
    return [(". ", COR["fraco"]), (chave, COR["chave"]), (": ", COR["fraco"]), (pontos, COR["fraco"]),
            (fim, cor_valor)]


def linha_dupla(c1: str, v1: str, c2: str, v2: str) -> list[tuple[str, str]]:
    esq = FICHA_COLS // 2 - 1
    a_ini, a_fim = f". {c1}: ", f" {v1}"
    b_ini, b_fim = f" | {c2}: ", f" {v2}"
    a_pts = "." * max(1, esq - len(a_ini) - len(a_fim))
    b_pts = "." * max(1, FICHA_COLS - esq - len(b_ini) - len(b_fim))
    return [(". ", COR["fraco"]), (c1, COR["chave"]), (": ", COR["fraco"]), (a_pts, COR["fraco"]),
            (a_fim, COR["valor"]), (" | ", COR["fraco"]), (c2, COR["chave"]), (": ", COR["fraco"]),
            (b_pts, COR["fraco"]), (b_fim, COR["valor"])]


def titulo(nome: str, cor: str) -> list[tuple[str, str]]:
    return [(nome + " ", cor), ("—" * (FICHA_COLS - len(nome) - 1), COR["fraco"])]


def main() -> None:
    rosto = json.loads((DADOS / "rosto.json").read_text(encoding="utf-8"))
    pares = [(l, t) for l, t in zip(rosto["linhas"], rosto["tons"])]
    while pares and not pares[0][0].strip():
        pares.pop(0)
    while pares and not pares[-1][0].strip():
        pares.pop()

    n = numeros()
    ficha: list[list[tuple[str, str]] | None] = [titulo("marcus@quantiumcode", COR["verde"])]
    ficha += [linha_ficha(*item) if item else [(".", COR["fraco"])] for item in FICHA]
    ficha += [[(".", COR["fraco"])], titulo("— Contato", COR["texto"])]
    ficha += [linha_ficha(*item) for item in CONTATO]
    ficha += [[(".", COR["fraco"])], titulo("— GitHub", COR["texto"])]
    ficha += [
        linha_dupla("Contribuições", milhar(n["total"]), "Dias ativos", str(n["ativos"])),
        linha_dupla("Repositórios", str(REPOSITORIOS), "Privados", str(PRIVADOS)),
        linha_dupla("Sequência", f"{n['sequencia']} dias", "Recorde/dia", str(n["recorde"])),
    ]

    topo = BARRA + 28  # linha do comando
    corpo = topo + 22
    arte_alt = len(pares) * ARTE_LH
    ficha_alt = len(ficha) * FICHA_LH
    fim = corpo + max(arte_alt, ficha_alt) + 18  # prompt final
    alt = int(fim + 22)
    arte_x = MARGEM
    ficha_x = LARG - MARGEM - FICHA_COLS * FICHA_CW
    arte_y0 = corpo + max(0, (ficha_alt - arte_alt) / 2)

    # Tempo: o comando digita, a saída aparece de cima para baixo, o cursor fica piscando.
    t_cmd, dur_cmd = 0.4, 0.8
    t_saida = t_cmd + dur_cmd + 0.25
    passo_arte = 1.2 / max(len(pares), 1)
    passo_ficha = 1.2 / max(len(ficha), 1)
    t_fim = t_saida + 1.4

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{LARG}" height="{alt}" viewBox="0 0 {LARG} {alt}" '
        f'xml:space="preserve" role="img" aria-labelledby="t d">',
        '<title id="t">marcus@quantiumcode: qos fetch</title>',
        '<desc id="d">Terminal com o rosto do Marcus desenhado em caracteres e a ficha: fundador e desenvolvedor '
        'da QuantiumCode, sistemas web, apps iOS e Android, agentes de IA e automações de WhatsApp.</desc>',
        "<style>",
        f"text {{ font-family: {FONTE}; white-space: pre; }}",
        ".ln { opacity: 0; animation: aparece .18s ease-out forwards; }",
        "@keyframes aparece { from { opacity: 0; } to { opacity: 1; } }",
        f".cursor {{ opacity: 0; animation: pisca 1.1s step-end {t_fim:.2f}s infinite; }}",
        "@keyframes pisca { 0% { opacity: 1; } 50% { opacity: 0; } }",
        "</style>",
        f'<rect x="0.5" y="0.5" width="{LARG - 1}" height="{alt - 1}" rx="12" fill="{COR["fundo"]}" '
        f'stroke="{COR["borda"]}"/>',
        f'<path d="M0.5 12.5a12 12 0 0 1 12-12h{LARG - 25}a12 12 0 0 1 12 12v{BARRA - 12}h-{LARG - 1}z" '
        f'fill="{COR["barra"]}"/>',
        f'<line x1="0.5" y1="{BARRA + .5}" x2="{LARG - .5}" y2="{BARRA + .5}" stroke="{COR["borda"]}"/>',
        # Brilho de monitor antigo no rosto: cada caractere brilha na própria cor.
        '<filter id="brilho" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.3" '
        'result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
    ]
    for i, cor in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        out.append(f'<circle cx="{22 + i * 20}" cy="{BARRA / 2 + .5}" r="6" fill="{cor}"/>')
    out.append(f'<text x="{LARG / 2}" y="{BARRA / 2 + 5}" text-anchor="middle" font-size="12.5" '
               f'fill="#7d8590">marcus@quantiumcode: ~ — zsh</text>')

    # Linha do comando: o prompt aparece, o comando é digitado letra a letra (SMIL, discreto).
    prompt = [("marcus@quantiumcode", COR["verde"]), (":", COR["texto"]), ("~", COR["azul"]), ("$ ", COR["texto"])]
    prompt_len = sum(len(t) for t, _ in prompt)
    cmd = "qos fetch"
    cmd_x = MARGEM + prompt_len * FICHA_CW
    out.append(f'<text x="{MARGEM}" y="{topo}" font-size="{FICHA_FONTE}" '
               f'textLength="{prompt_len * FICHA_CW:.1f}" lengthAdjust="spacingAndGlyphs">{spans(prompt)}</text>')
    larguras = ";".join(f"{k * FICHA_CW:.1f}" for k in range(len(cmd) + 1))
    tempos = ";".join(f"{k / len(cmd):.3f}" for k in range(len(cmd) + 1))
    out.append(
        f'<clipPath id="digita"><rect x="{cmd_x:.1f}" y="{topo - 16}" width="0" height="22">'
        f'<animate attributeName="width" values="{larguras}" keyTimes="{tempos}" calcMode="discrete" '
        f'begin="{t_cmd}s" dur="{dur_cmd}s" fill="freeze"/></rect></clipPath>')
    out.append(f'<text x="{cmd_x:.1f}" y="{topo}" font-size="{FICHA_FONTE}" fill="{COR["texto"]}" '
               f'clip-path="url(#digita)" textLength="{len(cmd) * FICHA_CW:.1f}" '
               f'lengthAdjust="spacingAndGlyphs">{cmd}</text>')

    # O rosto: cada caractere na cor do seu tom (claro = branco, escuro = cinza).
    out.append('<g filter="url(#brilho)">')
    for i, (linha, tons) in enumerate(pares):
        partes: list[tuple[str, str]] = []
        for ch, tom in zip(linha, tons.ljust(len(linha))):
            cor = COR["tons"][int(tom)] if tom.strip() else COR["fundo"]
            if partes and partes[-1][1] == cor:
                partes[-1] = (partes[-1][0] + ch, cor)
            else:
                partes.append((ch, cor))
        y = arte_y0 + (i + 1) * ARTE_LH
        out.append(f'<text class="ln" style="animation-delay:{t_saida + i * passo_arte:.2f}s" x="{arte_x}" '
                   f'y="{y:.1f}" font-size="{ARTE_FONTE}" textLength="{len(linha) * ARTE_CW:.1f}" '
                   f'lengthAdjust="spacingAndGlyphs">{spans(partes)}</text>')

    out.append("</g>")

    # A ficha.
    for i, partes in enumerate(ficha):
        texto = "".join(t for t, _ in partes)
        y = corpo + (i + 1) * FICHA_LH - 4
        out.append(f'<text class="ln" style="animation-delay:{t_saida + i * passo_ficha:.2f}s" x="{ficha_x}" '
                   f'y="{y:.1f}" font-size="{FICHA_FONTE}" textLength="{len(texto) * FICHA_CW:.1f}" '
                   f'lengthAdjust="spacingAndGlyphs">{spans(partes)}</text>')

    # Prompt final com o cursor piscando.
    out.append(f'<text class="ln" style="animation-delay:{t_fim - .2:.2f}s" x="{MARGEM}" y="{fim:.1f}" '
               f'font-size="{FICHA_FONTE}" textLength="{prompt_len * FICHA_CW:.1f}" '
               f'lengthAdjust="spacingAndGlyphs">{spans(prompt)}</text>')
    out.append(f'<rect class="cursor" x="{cmd_x:.1f}" y="{fim - 13:.1f}" width="{FICHA_CW:.1f}" height="16" '
               f'fill="{COR["texto"]}"/>')
    out.append("</svg>")

    (RAIZ / "assets" / "terminal.svg").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"terminal.svg: {LARG}x{alt}, rosto com {len(pares)} linhas, ficha com {len(ficha)} linhas")


if __name__ == "__main__":
    main()
