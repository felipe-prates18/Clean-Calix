import csv
import re

def extrair_texto_apos_data(linha_detalhe: str):
    resultados = []

    if not linha_detalhe:
        return resultados

    for linha in linha_detalhe.splitlines():
        linha = linha.strip()
        if not linha:
            continue

        padrao = r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\s*-\s*(.*)"
        match = re.search(padrao, linha)
        if match:
            resultados.append(match.group(1).strip())

    return resultados


def processar_csv(caminho_csv):
    resultados = []

    with open(caminho_csv, "r", encoding="utf-8", newline="") as f:
        leitor = csv.DictReader(f, delimiter=";")

        for idx, row in enumerate(leitor, start=2):
            detalhes = (row.get("Detalhes") or "").strip()

            textos = extrair_texto_apos_data(detalhes)

            resultados.append({
                "linha": idx,
                "detalhes_original": detalhes,
                "textos_apos_data": textos,
            })

    return resultados


if __name__ == "__main__":
    arquivo = "contatos_de_campanha_2025-11-06T16_05_24.050Z.csv"

    dados = processar_csv(arquivo)

    print("\n=== RESULTADOS EXTRAÍDOS ===\n")
    for item in dados:
        print(f"Linha {item['linha']}:")
        for texto in item["textos_apos_data"]:
            print(f"  - {texto}")
        print("-" * 60)
