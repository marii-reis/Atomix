from flask import Flask, render_template, request, send_from_directory


app = Flask(__name__, template_folder=".", static_folder=".")


@app.route("/style.css")
def servir_css():
    return send_from_directory(".", "style.css")


@app.route("/")
def index():
    return render_template("index.html")


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
                    ("1s", 2), ("2s", 2), ("2p", 6), ("3s", 2), ("3p", 6),
                    ("4s", 2), ("3d", 10), ("4p", 6), ("5s", 2), ("4d", 10),
                    ("5p", 6), ("6s", 2), ("4f", 14), ("5d", 10), ("6p", 6),
                    ("7s", 2), ("5f", 14), ("6d", 10), ("7p", 6)
                ]

                eletrons = numero_atomico
                distribuicao_lista = []

                expoentes = {
                    1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵",
                    6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹", 10: "¹⁰",
                    11: "¹¹", 12: "¹²", 13: "¹³", 14: "¹⁴"
                }

                for subnivel, limite in subniveis:
                    if eletrons == 0:
                        break

                    quantidade = min(eletrons, limite)
                    distribuicao_lista.append(subnivel + expoentes[quantidade])
                    eletrons -= quantidade

                resultado = " ".join(distribuicao_lista)

    return render_template("distribuiçãoEletronica.html", resultado=resultado)

@app.route("/quimicaorganica")
def quimica_organica():
    return render_template("quimicaorganica.html")

@app.route("/massamolar")
def massa_molar():
    return render_template("massamolar.html")

@app.route("/sobre")
def sobre():
    return render_template("sobre.html")

@app.route("/balanceamentoPH.html")
def balanceamento_PH():
    return render_template("balanceamentoPH.html")

@app.route("/equacoes")
def equacoes():
    return render_template("equacoes.html")

if __name__ == "__main__":
    app.run(debug=True)
