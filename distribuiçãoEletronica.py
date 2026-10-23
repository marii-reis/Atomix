from flask import Flask, render_template, request, send_from_directory
import re
from fractions import Fraction
from math import gcd
from functools import reduce


app = Flask(
    __name__,
    template_folder=".",
    static_folder=".",
    static_url_path=""
)


@app.route("/style.css")
def servir_css():
    return send_from_directory(".", "style.css")


@app.route("/")
def index():
    return render_template("index.html")


# DISTRIBUIÇÃO ELETRÔNICA
@app.route("/distribuicao", methods=["GET", "POST"])
def distribuicao():
    resultado = ""

    if request.method == "POST":
        entrada = request.form.get("numero_atomico", "").strip()

        if not entrada.isdigit():
            resultado = "Por favor, informe um número inteiro válido."
        else:
            numero_atomico = int(entrada)

            if numero_atomico < 1 or numero_atomico > 118:
                resultado = "Digite um número atômico entre 1 e 118."
            else:
                subniveis = [
                    ("1s", 2), ("2s", 2), ("2p", 6),
                    ("3s", 2), ("3p", 6), ("4s", 2),
                    ("3d", 10), ("4p", 6), ("5s", 2),
                    ("4d", 10), ("5p", 6), ("6s", 2),
                    ("4f", 14), ("5d", 10), ("6p", 6),
                    ("7s", 2), ("5f", 14), ("6d", 10),
                    ("7p", 6)
                ]

                expoentes = {
                    1: "¹", 2: "²", 3: "³", 4: "⁴",
                    5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸",
                    9: "⁹", 10: "¹⁰", 11: "¹¹",
                    12: "¹²", 13: "¹³", 14: "¹⁴"
                }

                eletrons = numero_atomico
                distribuicao_lista = []

                for subnivel, limite in subniveis:
                    if eletrons == 0:
                        break

                    quantidade = min(eletrons, limite)
                    distribuicao_lista.append(
                        subnivel + expoentes[quantidade]
                    )
                    eletrons -= quantidade

                resultado = " ".join(distribuicao_lista)

    return render_template(
        "distribuiçãoEletronica.html",
        resultado=resultado
    )


# QUÍMICA ORGÂNICA
@app.route("/quimicaorganica")
def quimica_organica():
    return render_template("quimicaorganica.html")


# MASSA MOLAR
@app.route("/massamolar")
def massa_molar():
    return render_template("massamolar.html")


# SOBRE NÓS
@app.route("/sobre")
def sobre():
    return render_template("sobre.html")


# BALANCEAMENTO DE PH
@app.route("/balanceamentoPH")
def balanceamento_PH():
    return render_template("balanceamentoPH.html")


# INTERPRETA A FÓRMULA QUÍMICA
def contar_atomos(formula):
    tokens = re.findall(r"[A-Z][a-z]?|\d+|[()]", formula)

    if not tokens or "".join(tokens) != formula:
        raise ValueError(
            "Confira a fórmula química digitada."
        )

    pilha = [{}]
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token == "(":
            pilha.append({})
            i += 1

        elif token == ")":
            if len(pilha) == 1:
                raise ValueError(
                    "Confira os parênteses da fórmula."
                )

            grupo = pilha.pop()
            i += 1
            multiplicador = 1

            if i < len(tokens) and tokens[i].isdigit():
                multiplicador = int(tokens[i])
                i += 1

            for elemento, quantidade in grupo.items():
                pilha[-1][elemento] = (
                    pilha[-1].get(elemento, 0)
                    + quantidade * multiplicador
                )

        elif re.fullmatch(r"[A-Z][a-z]?", token):
            elemento = token
            i += 1
            quantidade = 1

            if i < len(tokens) and tokens[i].isdigit():
                quantidade = int(tokens[i])
                i += 1

            pilha[-1][elemento] = (
                pilha[-1].get(elemento, 0) + quantidade
            )

        else:
            raise ValueError(
                "Confira a fórmula química digitada."
            )

    if len(pilha) != 1:
        raise ValueError(
            "Confira os parênteses da fórmula."
        )

    return pilha[0]


# BALANCEAMENTO DE EQUAÇÕES
def balancear_equacao(equacao):
    equacao = equacao.replace("→", "->").replace("=", "->")

    partes = equacao.split("->")

    if len(partes) != 2:
        raise ValueError(
            "Separe os reagentes e produtos com ->."
        )

    reagentes = partes[0].split("+")
    produtos = partes[1].split("+")

    formulas = [
        formula.strip()
        for formula in reagentes + produtos
    ]

    if (
        not reagentes
        or not produtos
        or any(not formula for formula in formulas)
    ):
        raise ValueError(
            "Confira os reagentes e produtos da equação."
        )

    atomos = [contar_atomos(formula) for formula in formulas]

    elementos = sorted(
        set().union(*(atomo.keys() for atomo in atomos))
    )

    matriz = []

    for elemento in elementos:
        linha = []

        for i, contagem in enumerate(atomos):
            sinal = 1 if i < len(reagentes) else -1

            linha.append(
                Fraction(sinal * contagem.get(elemento, 0))
            )

        matriz.append(linha)

    linhas = len(matriz)
    colunas = len(formulas)
    pivots = []
    linha_atual = 0

    # Eliminação de Gauss
    for coluna in range(colunas):
        pivo = next(
            (
                r for r in range(linha_atual, linhas)
                if matriz[r][coluna] != 0
            ),
            None
        )

        if pivo is None:
            continue

        matriz[linha_atual], matriz[pivo] = (
            matriz[pivo],
            matriz[linha_atual]
        )

        valor = matriz[linha_atual][coluna]

        matriz[linha_atual] = [
            valor_celula / valor
            for valor_celula in matriz[linha_atual]
        ]

        for r in range(linhas):
            if r != linha_atual:
                fator = matriz[r][coluna]

                matriz[r] = [
                    matriz[r][c]
                    - fator * matriz[linha_atual][c]
                    for c in range(colunas)
                ]

        pivots.append(coluna)
        linha_atual += 1

        if linha_atual == linhas:
            break

    livres = [
        coluna for coluna in range(colunas)
        if coluna not in pivots
    ]

    if len(livres) != 1:
        raise ValueError(
            "Não foi possível encontrar um balanceamento único."
        )

    coeficientes = [
        Fraction(0) for _ in range(colunas)
    ]

    coeficientes[livres[0]] = Fraction(1)

    for r, coluna in enumerate(pivots):
        coeficientes[coluna] = -sum(
            matriz[r][c] * coeficientes[c]
            for c in livres
        )

    denominador_comum = 1

    for coeficiente in coeficientes:
        denominador_comum = (
            denominador_comum * coeficiente.denominator
            // gcd(
                denominador_comum,
                coeficiente.denominator
            )
        )

    inteiros = [
        int(coeficiente * denominador_comum)
        for coeficiente in coeficientes
    ]

    divisor = reduce(
        gcd,
        (abs(coeficiente) for coeficiente in inteiros)
    )

    if divisor == 0:
        raise ValueError(
            "Não foi possível balancear essa equação."
        )

    inteiros = [
        coeficiente // divisor
        for coeficiente in inteiros
    ]

    if any(coeficiente <= 0 for coeficiente in inteiros):
        raise ValueError(
            "Essa equação não possui uma solução positiva."
        )

    resultado = []

    for i, formula in enumerate(formulas):
        coeficiente = (
            "" if inteiros[i] == 1
            else str(inteiros[i])
        )

        resultado.append(coeficiente + formula)

    quantidade_reagentes = len(reagentes)

    return (
        " + ".join(resultado[:quantidade_reagentes])
        + " → "
        + " + ".join(resultado[quantidade_reagentes:])
    )


@app.route("/equacoes", methods=["GET", "POST"])
def equacoes():
    resultado = ""

    if request.method == "POST":
        equacao = request.form.get("equacao", "").strip()

        if not equacao:
            resultado = "Digite uma equação para balancear."
        else:
            try:
                resultado = balancear_equacao(equacao)
            except ValueError as erro:
                resultado = str(erro)
            except Exception:
                resultado = (
                    "Não foi possível balancear essa equação."
                )

    return render_template(
        "equacoes.html",
        resultado=resultado
    )


# ESTEQUIOMETRIA
@app.route("/estequiometria", methods=["GET", "POST"])
def estequiometria():
    return render_template("estequiometria.html")


if __name__ == "__main__":
    app.run(debug=True)
