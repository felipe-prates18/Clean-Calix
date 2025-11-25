import csv
import re
from pathlib import Path

PHONE_COLUMNS = [
    "Celular 1",
    "Celular 2",
    "Celular 3",
    "Celular 4",
    "celular 5",
    "Telefone 1",
    "telefone 2",
    "Telefone 3",
    "Telefone 4",
    "telefone 5",
]

STATUS_REMOVE_ROW = {
    "completado - sem interesse",
    "completado - envio de proposta",
    "completado - parente localizado",
    "completado - localizado",
}


def normalizar_numero(numero: str) -> str:
    apenas_digitos = re.sub(r"\D", "", numero or "")

    if apenas_digitos.startswith("55") and len(apenas_digitos) > 11:
        apenas_digitos = apenas_digitos[2:]

    if len(apenas_digitos) > 11:
        apenas_digitos = apenas_digitos[-11:]

    return apenas_digitos


def extrair_detalhes(detalhes_brutos: str):
    resultados = []

    for linha in (detalhes_brutos or "").splitlines():
        linha = linha.strip()
        if not linha:
            continue

        padrao = (
            r"^\s*([+\d][\d\s().-]*)\s*-\s*"
            r"\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}\s*-\s*(.+)$"
        )
        match = re.match(padrao, linha)
        if not match:
            continue

        numero, status = match.groups()
        resultados.append((numero.strip(), status.strip()))

    return resultados


def remover_numero_da_linha(linha: dict, numero_alvo: str):
    numero_normalizado = normalizar_numero(numero_alvo)

    for coluna in PHONE_COLUMNS:
        valor_coluna = linha.get(coluna, "")
        if valor_coluna and normalizar_numero(valor_coluna) == numero_normalizado:
            linha[coluna] = ""


def classificar_status(status: str):
    status_normalizado = (status or "").strip().lower()

    if status_normalizado in STATUS_REMOVE_ROW:
        return "remover_linha"

    if (
        "telefone não existe" in status_normalizado
        or status_normalizado.startswith("completado - ñ conhece")
        or "telefone mudou" in status_normalizado
    ):
        return "remover_numero"

    return "manter"


def processar_csv(caminho_csv: str, caminho_saida: str):
    total_entrada = 0
    total_saida = 0

    with open(caminho_csv, "r", encoding="utf-8", newline="") as origem:
        leitor = csv.DictReader(origem, delimiter=";")
        dados_saida = []

        for linha in leitor:
            total_entrada += 1
            remover_linha = False

            for numero, status in extrair_detalhes(linha.get("Detalhes") or ""):
                acao = classificar_status(status)

                if acao == "remover_linha":
                    remover_linha = True
                    break

                if acao == "remover_numero":
                    remover_numero_da_linha(linha, numero)

            if not remover_linha:
                dados_saida.append(linha)
                total_saida += 1

    with open(caminho_saida, "w", encoding="utf-8", newline="") as destino:
        escritor = csv.DictWriter(destino, fieldnames=leitor.fieldnames, delimiter=";")
        escritor.writeheader()
        escritor.writerows(dados_saida)

    return total_entrada, total_saida


def gerar_caminho_saida(caminho_csv: str) -> str:
    caminho = Path(caminho_csv)
    return str(caminho.with_name(f"{caminho.stem}_ajustado{caminho.suffix}"))


if __name__ == "__main__":
    arquivo = "contatos_de_campanha_2025-11-06T16_05_24.050Z.csv"
    destino = gerar_caminho_saida(arquivo)

    entradas, saidas = processar_csv(arquivo, destino)

    print(f"Arquivo processado: {arquivo}")
    print(f"Arquivo gerado:    {destino}")
    print(f"Linhas originais: {entradas}")
    print(f"Linhas finais:    {saidas}")
