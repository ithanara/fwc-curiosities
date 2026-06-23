import re

import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://en.wikipedia.org/wiki/2026_FIFA_World_Cup_squads"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; squad-scraper/1.0)"}


def get_soup(url: str) -> tuple[BeautifulSoup, str]:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    print(f"[debug] status HTTP: {resp.status_code} | tamanho da resposta: {len(resp.text)} chars")
    resp.raise_for_status()

    # Tenta vários parsers em ordem; alguns (ex: lxml) podem falhar silenciosamente
    # em documentos grandes/específicos e retornar uma árvore vazia.
    for parser_name in ("html.parser", "lxml", "html5lib"):
        try:
            candidate = BeautifulSoup(resp.text, parser_name)
        except Exception as e:
            print(f"[debug] parser '{parser_name}' levantou exceção: {e}")
            continue

        n_tables = len(candidate.find_all("table"))
        n_paragraphs = len(candidate.find_all("p"))
        print(f"[debug] parser '{parser_name}': {n_tables} tables, {n_paragraphs} parágrafos")

        if n_tables > 0:
            return candidate, resp.text

    # Se nenhum parser encontrou tabelas, retorna o último testado mesmo assim
    # (vai cair no fallback de salvar debug_page.html mais à frente)
    return candidate, resp.text



# Reconhece links para a página da seleção nacional, ex:
# /wiki/Czech_Republic_national_football_team
# /wiki/Canada_men%27s_national_soccer_team
TEAM_LINK_RE = re.compile(r"_national_(football|soccer)_team", re.IGNORECASE)


def extract_squads(url: str = URL) -> pd.DataFrame:
    soup, raw_html = get_soup(url)

    content = soup.find("div", class_="mw-parser-output")
    n_tables_in_content = len(content.find_all("table")) if content is not None else 0

    if content is None or n_tables_in_content == 0:
        # A div mw-parser-output pode vir "vazia" dependendo do parser usado
        # (acontece com html.parser em documentos com aninhamento meio quebrado).
        # Nesse caso, usamos o documento inteiro como escopo — não precisamos
        # do escopo restrito, só de achar as <table class="wikitable"> e os <p>.
        print(
            f"[debug] div.mw-parser-output encontrada mas com {n_tables_in_content} tabelas "
            f"— usando soup inteiro como escopo em vez dela"
        )
        content = soup

    raw_tables = content.find_all("table")
    print(f"[debug] total de <table> (qualquer classe) encontradas: {len(raw_tables)}")
    if raw_tables:
        print(f"[debug] classes da 1a tabela: {raw_tables[0].get('class')}")
        print(f"[debug] classes da última tabela: {raw_tables[-1].get('class')}")
    else:
        debug_path = "debug_page.html"
        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(raw_html)
        print(f"[debug] 0 tabelas encontradas — HTML bruto salvo em '{debug_path}' para inspeção manual")

    all_paragraphs = content.find_all("p")
    print(f"[debug] total de <p> encontrados: {len(all_paragraphs)}")

    all_frames = []
    current_team = None
    debug_headings_found = 0
    debug_tables_seen = 0
    debug_tables_skipped_no_team = 0

    # Percorre h3 (cabeçalhos, se existirem) e elementos de texto/table na ordem do documento
    for element in content.find_all(["h2", "h3", "p", "table"]):

        if element.name in ("h2", "h3"):
            headline = element.find("span", class_="mw-headline")
            text = headline.get_text(strip=True) if headline else element.get_text(strip=True)
            # só conta como heading de seleção se não for algo genérico tipo "Group A", "Notes", etc.
            if text and not text.lower().startswith(("group", "note", "see also", "reference")):
                current_team = text
                debug_headings_found += 1

        elif element.name == "p":
            # Esta página identifica a seleção por um link para a página
            # "<Pais> national football/soccer team" dentro do parágrafo,
            # não por um cabeçalho h3. Ex: "...The [Czech Republic](.../Czech_Republic_national_football_team) announced..."
            for link in element.find_all("a", href=True):
                if TEAM_LINK_RE.search(link["href"]):
                    current_team = link.get_text(strip=True)
                    break  # primeiro link de seleção no parágrafo é o que importa

        elif element.name == "table" and "wikitable" in (element.get("class") or []):
            debug_tables_seen += 1
            if current_team is None:
                debug_tables_skipped_no_team += 1
                continue  # tabela antes de identificarmos qualquer seleção (ignora)
            try:
                df = pd.read_html(str(element))[0]
            except ValueError:
                continue

            df.insert(0, "Selecao", current_team)
            all_frames.append(df)

    print(
        f"[debug] headings detectados: {debug_headings_found} | "
        f"tabelas wikitable vistas: {debug_tables_seen} | "
        f"tabelas puladas (sem seleção identificada ainda): {debug_tables_skipped_no_team} | "
        f"tabelas aproveitadas: {len(all_frames)}"
    )

    if not all_frames:
        raise RuntimeError(
            "Nenhuma tabela de elenco foi encontrada. "
            "Veja a linha [debug] acima para diagnosticar: se 'tabelas wikitable vistas' "
            "estiver em 0, o problema é que content.find('div', class_='mw-parser-output') "
            "não encontrou o conteúdo (página pode ter vindo vazia/bloqueada). "
            "Se 'tabelas vistas' > 0 mas 'aproveitadas' = 0, o problema é na detecção do nome "
            "da seleção (regex TEAM_LINK_RE não bateu com os links da página)."
        )

    final_df = pd.concat(all_frames, ignore_index=True)

    # Pequena limpeza: remove parênteses "(captain)" para uma coluna separada, se quiser
    final_df["Captain"] = final_df["Player"].str.contains(r"\(captain\)", na=False)
    final_df["Player"] = (
        final_df["Player"].str.replace(r"\s*\(captain\)", "", regex=True).str.strip()
    )

    return final_df


if __name__ == "__main__":
    df = extract_squads()
    print(df.shape)
    print(df.head(20))

    df.to_csv("Extract/fifa_2026_squads.csv", index=False, encoding="utf-8-sig")
    print("Arquivo salvo: fifa_2026_squads.csv")
