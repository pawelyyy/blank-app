import streamlit as st
import pandas as pd
import re

# ==========================================
# KONFIGURACJA STRONY (Musi być na samej górze)
# ==========================================
st.set_page_config(page_title="Macierz Konfiguracji Rynków", layout="wide", page_icon="📊")

# ==========================================
# BAZA WIEDZY
# ==========================================
me_markets_base = {"ar-bh", "ar-dz", "ar-eg", "ar-kw", "ar-ly", "ar-ma", "ar-om", "ar-qa", "ar-tn", "bg-bg",
                   "bs-latn-ba", "de-li", "de-lu", "en-cy", "en-my", "en-ph", "es-bo", "es-cr", "es-ec", "es-gt",
                   "es-hn", "es-ni", "es-pa", "es-pe", "es-py", "es-sv", "es-uy", "et-ee", "fr-lu", "hr-hr", "id-id",
                   "is-is", "ka-ge", "lt-lt", "lv-lv", "mk-mk", "mt-mt", "ro-md", "ro-ro", "sl-si", "sq-al",
                   "sr-latn-me", "sr-latn-rs", "th-th", "uk-ua", "vi-vn"}
me_uses_en_gb = {"ar-bh", "ar-dz", "ar-eg", "ar-kw", "ar-ly", "ar-ma", "ar-om", "ar-qa", "ar-tn", "bg-bg", "bs-latn-ba",
                 "et-ee", "lt-lt", "lv-lv", "ro-ro", "sl-sl", "he-il", "hr-hr", "is-is", "ka-ge", "lt-lt", "lv-lv",
                 "mk-mk", "mt-mt", "ro-md", "ro-ro", "sq-al", "sr-latn-me", "sr-latn"}

ALL_ME_MARKETS = me_markets_base | me_uses_en_gb

ME_EXCEPTIONS = {"th-th", "uk-ua", "vi-vn", "de-de", "es-mx", "fr-fr", "id-id", "en-gb"}

CATEGORIES = {
    "Global": {"ar-ae", "ar-sa", "cs-cz", "da-dk", "de-at", "de-ch", "de-de", "el-gr", "en-au", "en-ca", "en-gb",
               "en-hk", "en-ie", "en-in", "en-nz", "en-sg", "en-us", "en-za", "es-ar", "es-cl", "es-co", "es-es",
               "es-mx", "fi-fi", "fr-be", "fr-ca", "fr-ch", "fr-fr", "he-il", "hu-hu", "it-it", "ja-jp", "ko-kr",
               "nb-no", "nl-be", "nl-nl", "pl-pl", "pt-br", "pt-pt", "sk-sk", "sv-se", "tr-tr", "zh-hk", "zh-tw"},
    "/ME Markets": ALL_ME_MARKETS,
    "Priority Markets": {"de-de", "de-at", "de-ch", "nl-nl", "nl-be", "en-au", "en-gb", "en-hk", "en-ie", "en-nz",
                         "en-ca", "en-us", "fr-fr", "fr-be", "fr-ch", "fr-ca", "it-it", "ja-jp", "ko-kr", "pl-pl",
                         "pt-br", "es-co", "es-mx", "es-ar", "es-cl", "es-es", "zh-tw", "zh-hk"},
    "Cloud Market": {"cs-cz", "da-dk", "de-at", "de-ch", "de-de", "en-au", "en-ca", "en-gb", "en-ie", "en-in", "en-nz",
                     "es-ar", "es-es", "es-mx", "fi-fi", "fr-be", "fr-ca", "fr-ch", "fr-fr", "hu-hu", "it-it", "ja-jp",
                     "ko-kr", "nb-no", "nl-be", "nl-nl", "pl-pl", "pt-br", "pt-pt", "sk-sk", "sv-se"},
    "Non-Cloud Market": {"ar-ae", "ar-sa", "el-gr", "en-ae", "en-hk", "he-il", "en-sa", "en-sg", "en-za", "es-cl",
                         "es-co", "ru-ru", "tr-tr", "zh-hk", "zh-tw"},
    "Rewards Market": {"de-de", "en-au", "en-ca", "en-gb", "en-hk", "en-ie", "en-nz", "en-sg", "es-es", "es-mx",
                       "fr-be", "fr-ca", "fr-fr", "it-it", "ja-jp", "nb-no", "nl-be", "nl-nl", "pt-br", "sv-se",
                       "zh-hk", "zh-tw"},
    "3P GLP": {"de-de", "de-at", "de-ch", "en-au", "en-gb", "en-hk", "en-ie", "en-nz", "en-ca", "en-us", "fr-fr",
               "fr-be", "fr-ch", "fr-ca", "it-it", "ja-jp", "ko-kr", "es-es", "es-co", "es-mx", "es-ar", "es-cl",
               "pt-br"},
    "Xbox Design Lab": {"cs-cz", "da-dk", "de-at", "de-ch", "de-de", "el-gr", "en-au", "en-ca", "en-gb", "en-ie",
                        "en-sg", "en-za", "es-es", "fi-fi", "fr-bz", "fr-ca", "fr-ch", "fr-fr", "hu-hu", "it-it",
                        "ja-jp", "ko-kr", "nb-no", "nl-nl", "pl-pl", "pt-pt", "sv-se", "sk-sk", "zh-tw"}
}

PARENT_CHILD_MAP = {
    "ar": {"parent": ["ar-sa"], "children": ["ar-ae", "ar-bh", "ar-dj", "ar-dz", "ar-eg", "ar-eh", "ar-er", "ar-iq", "ar-jo", "ar-km", "ar-kw", "ar-lb", "ar-ly", "ar-mr", "ar-om", "ar-ps", "ar-qa", "ar-sd", "ar-sn", "ar-so", "ar-ss", "ar-sy", "ar-tn", "ar-ye"], "separate": ["ar-ma"]},
    "de": {"parent": ["de-de"], "children": ["de-at", "de-ch", "de-it", "de-li", "de-lu"], "separate": []},
    "el": {"parent": [], "children": ["el-cy"], "separate": []},
    "en": {"parent": ["en-gb"], "children": ["en-ae", "en-ag", "en-ai", "en-al", "en-am", "en-aq", "en-as", "en-au", "en-aw", "en-az", "en-ba", "en-bb", "en-bd", "en-be", "en-bh", "en-bm", "en-br", "en-bs", "en-bt", "en-bw", "en-bz", "en-ca", "en-cc", "en-ch", "en-ck", "en-cn", "en-co", "en-cw", "en-cx", "en-cy", "en-de", "en-dk", "en-dm", "en-dz", "en-eg", "en-es", "en-et", "en-fj", "en-fk", "en-fm", "en-fr", "en-gd", "en-ge", "en-gg", "en-gh", "en-gi", "en-gm", "en-gs", "en-gu", "en-gy", "en-hk", "en-hm", "en-id", "en-ie", "en-il", "en-im", "en-in", "en-io", "en-iq", "en-is", "en-it", "en-je", "en-jm", "en-jo", "en-jp", "en-ke", "en-kh", "en-ki", "en-kn", "en-kr", "en-kw", "en-ky", "en-kz", "en-la", "en-lb", "en-lc", "en-lk", "en-lr", "en-ls", "en-ly", "en-ma", "en-me", "en-mg", "en-mh", "en-mk", "en-mm", "en-mn", "en-mp", "en-ms", "en-mt", "en-mu", "en-mv", "en-mw", "en-mx", "en-my", "en-na", "en-nf", "en-ng", "en-nl", "en-np", "en-nr", "en-nu", "en-nz", "en-om", "en-pe", "en-pg", "en-ph", "en-pk", "en-pn", "en-pr", "en-pw", "en-qa", "en-ru", "en-sa", "en-sb", "en-sc", "en-sg", "en-sh", "en-sl", "en-ss", "en-sx", "en-sy", "en-sz", "en-tc", "en-th", "en-tk", "en-tl", "en-tn", "en-to", "en-tr", "en-tt", "en-tv", "en-tw", "en-tz", "en-ug", "en-um", "en-vc", "en-vg", "en-vi", "en-vu", "en-ws", "en-ye", "en-za", "en-zm", "en-zw"], "separate": []},
    "es": {"parent": ["es-mx"], "children": ["es-ar", "es-aw", "es-bb", "es-bo", "es-bz", "es-cl", "es-co", "es-cr", "es-cu", "es-do", "es-ec", "es-gq", "es-gt", "es-hn", "es-jm", "es-ni", "es-pa", "es-pe", "es-pr", "es-py", "es-sv", "es-tt", "es-uy", "es-ve"], "separate": ["es-es", "es-us"]},
    "fr": {"parent": ["fr-fr"], "children": ["fr-ad", "fr-be", "fr-bf", "fr-bi", "fr-bj", "fr-bl", "fr-cd", "fr-cf", "fr-cg", "fr-ch", "fr-ci", "fr-cm", "fr-dj", "fr-dz", "fr-ga", "fr-gf", "fr-gn", "fr-gp", "fr-gq", "fr-ht", "fr-km", "fr-lu", "fr-ma", "fr-mc", "fr-mf", "fr-mg", "fr-ml", "fr-mq", "fr-mu", "fr-nc", "fr-ne", "fr-pf", "fr-pm", "fr-re", "fr-rw", "fr-sc", "fr-sn", "fr-td", "fr-tf", "fr-tg", "fr-tn", "fr-wf", "fr-yt"], "separate": ["fr-ca"]},
    "hr": {"parent": [], "children": ["hr-ba"], "separate": []},
    "it": {"parent": [], "children": ["it-ch", "it-sm", "it-va"], "separate": []},
    "nl": {"parent": ["nl-nl"], "children": ["nl-be", "nl-cw", "nl-sr"], "separate": []},
    "pt": {"parent": [], "children": ["pt-ao", "pt-cv", "pt-mz", "pt-st", "pt-tl"], "separate": []},
    "ro": {"parent": [], "children": ["ro-md"], "separate": []},
    "ru": {"parent": [], "children": ["ru-by", "ru-kg", "ru-kz", "ru-tj", "ru-uz"], "separate": []},
    "sv": {"parent": [], "children": ["sv-ax", "sv-fi"], "separate": []},
    "zh": {"parent": ["zh-cn"], "children": [], "separate": ["zh-hk", "zh-tw"]}
}

TEST_DATA = """Target Languages
de-de
de-at
de-ch
en-au
en-gb
en-hk
en-ie
en-nz
en-ca
fr-fr
fr-be
fr-ch
fr-ca
it-it
ja-jp
ko-kr
es-es
es-co
es-mx
es-ar
es-cl
pt-br
bs-latn-ba
th-th"""

# Kolory tła dla wierszy w tabeli
TEMPLATE_COLORS = [
    "#D6EAF8", "#D5F5E3", "#FCF3CF", "#FADBD8", "#E8DAEF",
    "#D1F2EB", "#FDEBD0", "#EAECEE", "#F5EEF8", "#E6B0AA"
]

# ==========================================
# LOGIKA
# ==========================================
def get_mapping_info(locale_code):
    locale_code = locale_code.lower()

    if locale_code in ALL_ME_MARKETS and locale_code not in ME_EXCEPTIONS:
        return "Child (EN-GB)"

    for group, data in PARENT_CHILD_MAP.items():
        if locale_code in data["parent"]:
            return "Parent"
        if locale_code in data["children"]:
            parents = [p.upper() for p in data["parent"]]
            parent_str = ", ".join(parents) if parents else "Brak"
            return f"Child ({parent_str})"
        if locale_code in data["separate"]:
            return "Separate"

    return "Stand-alone"

# ==========================================
# INTERFEJS WEBOWY (STREAMLIT)
# ==========================================
st.title("Macierz Konfiguracji Rynków v2.4")

# --- LEWY PANEL (SIDEBAR) ---
st.sidebar.header("Ustawienia i Filtry")

use_test_data = st.sidebar.toggle("Wklej dane testowe", value=False)
default_input = TEST_DATA if use_test_data else ""
input_data = st.sidebar.text_area("Kody Językowe:", value=default_input, height=150)

exclude_child = st.sidebar.checkbox("Ukryj rynki 'Child'")
sort_by = st.sidebar.radio("Sortowanie tabeli:", ["Wg Kategorii", "Alfabetycznie"])

st.sidebar.markdown("### Kategorie do macierzy:")
active_categories = []
for cat_name in CATEGORIES.keys():
    if cat_name == "Global":
        continue
    # Streamlit w locie rejestruje status każdego checkboxa
    if st.sidebar.checkbox(cat_name, value=True):
        active_categories.append(cat_name)

# --- PRZETWARZANIE DANYCH ---
raw_codes = re.split(r'[\s,]+', input_data.strip())
# Usuwamy duplikaty i puste słowa, filtrujemy "target" i "languages"
locales = list(dict.fromkeys([code.lower() for code in raw_codes if code and code.lower() not in ["target", "languages"]]))

if not locales or not active_categories:
    st.info("👈 Wklej kody językowe w panelu po lewej stronie i zaznacz co najmniej jedną kategorię.")
else:
    unique_configurations = {}
    valid_locales = []

    for loc in locales:
        map_type = get_mapping_info(loc)
        if exclude_child and map_type.startswith("Child"):
            continue

        valid_locales.append(loc)
        features = {cat: (loc in CATEGORIES[cat]) for cat in active_categories}
        # Podpis unikalnej kombinacji to po prostu lista (tuple) wartości True/False
        signature = tuple(features[cat] for cat in active_categories)

        if signature not in unique_configurations:
            unique_configurations[signature] = {"langs": [], "features": features}
        unique_configurations[signature]["langs"].append(loc.upper())

    # Generowanie ID i przypisanie kolorów
    sig_to_template = {}
    for idx, sig in enumerate(unique_configurations.keys()):
        template_id = idx + 1
        color = TEMPLATE_COLORS[idx % len(TEMPLATE_COLORS)]
        sig_to_template[sig] = {"id": template_id, "color": color}

    data_rows = []
    for loc in valid_locales:
        map_type = get_mapping_info(loc)
        features = {cat: (loc in CATEGORIES[cat]) for cat in active_categories}
        signature = tuple(features[cat] for cat in active_categories)
        temp_info = sig_to_template[signature]

        row = {
            "Język": loc.upper(),
            "Relacja": map_type,
            "Szablon ID": f"#{temp_info['id']}"
        }
        # Dynamiczne dodawanie kolumn kategorii
        for cat in active_categories:
            row[cat] = "✔️" if features[cat] else ""
        
        # Zapisujemy kolor w ukrytej kolumnie na później
        row["_Color"] = temp_info["color"]
        data_rows.append(row)

    # Sortowanie danych
    if sort_by == "Alfabetycznie":
        sorted_data = sorted(data_rows, key=lambda x: x['Język'])
    else:
        # Sortuj najpierw po Szablon ID (jako liczba zdejmując '#'), potem alfabetycznie po języku
        sorted_data = sorted(data_rows, key=lambda x: (int(x['Szablon ID'].replace("#", "")), x['Język']))

    df = pd.DataFrame(sorted_data)

    # --- ZAKŁADKI ---
    tab_matrix, tab_templates, tab_export = st.tabs(["📊 Macierz (Graficzna)", "🧩 Wymagane Szablony", "📝 Eksport (Zwykły Tekst)"])

    with tab_matrix:
        # Legenda Szablonów
        st.markdown("##### Legenda Szablonów")
        cols = st.columns(len(sig_to_template))
        for i, (sig, temp_info) in enumerate(sig_to_template.items()):
            t_id = temp_info["id"]
            color = temp_info["color"]
            with cols[i]:
                # Wykorzystujemy wbudowany HTML Streamlita dla wizualnych bloczków
                st.markdown(f'<div style="background-color:{color}; color: #333; padding: 5px; border-radius: 5px; text-align: center;"><b>#{t_id}</b></div>', unsafe_allow_html=True)
        
        st.write("") # Odstęp

        # Funkcja do stylowania wierszy Pandas DataFrame
        def apply_row_style(row):
            bg_color = df.loc[row.name, "_Color"]
            # Wymuszamy ciemny kolor fontu, żeby napisy były widoczne na jasnych, pastelowych tłach
            return [f"background-color: {bg_color}; color: #222222"] * len(row)

        # Usunięcie z widoku kolumny technicznej _Color
        display_df = df.drop(columns=["_Color"])
        styled_df = display_df.style.apply(apply_row_style, axis=1)

        # Wyświetlanie tabeli (ukrywamy numery wierszy - indekso)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)

    with tab_templates:
        for sig, temp_info in sig_to_template.items():
            t_id = temp_info["id"]
            data = unique_configurations[sig]
            bg_color = temp_info["color"]

            with st.container():
                langs_str = ", ".join(sorted(data['langs']))
                active_traits = [cat for cat in active_categories if data['features'][cat]]
                traits_str = ", ".join(active_traits) if active_traits else "Brak (nie wymaga wariacji)"

                # Rysujemy "kartę" za pomocą HTML
                st.markdown(f"""
                <div style="background-color: {bg_color}; color: #222222; padding: 20px; border-radius: 10px; margin-bottom: 10px;">
                    <h4 style="margin-top: 0; color: #111;">Szablon #{t_id}</h4>
                    <p style="margin-bottom: 5px;"><b>Przypisane rynki:</b> <span style="font-family: monospace;">{langs_str}</span></p>
                    <p style="margin-bottom: 0px;"><b>Wymagane funkcje:</b> {traits_str}</p>
                </div>
                """, unsafe_allow_html=True)

    with tab_export:
        col_w_loc = 12
        col_w_type = 20
        col_widths = {cat: max(len(cat), 4) for cat in active_categories}

        report = "=== MACIERZ KONFIGURACJI ===\n\n"
        header = f"{'JĘZYK'.ljust(col_w_loc)} | {'TYP (Rel)'.ljust(col_w_type)} | {'ID'.ljust(4)} | "
        header += " | ".join([cat.ljust(col_widths[cat]) for cat in active_categories])
        report += header + "\n" + "-" * len(header) + "\n"

        # Ponownie budujemy logikę dla czystego tekstu
        for row in sorted_data:
            tid_clean = row['Szablon ID'].replace("#", "")
            feat_bools = {cat: (row[cat] == "✔️") for cat in active_categories}
            
            line = f"{row['Język'].ljust(col_w_loc)} | {row['Relacja'].ljust(col_w_type)} | {tid_clean.ljust(4)} | "
            feat_str = " | ".join([("✔️" if feat_bools[cat] else "-").ljust(col_widths[cat]) for cat in active_categories])
            report += line + feat_str + "\n"

        report += "\n\n=== WYMAGANE UNIKALNE SZABLONY / STRONY ===\n\n"
        for sig, temp_info in sig_to_template.items():
            t_id = temp_info["id"]
            data = unique_configurations[sig]

            langs = ", ".join(sorted(data['langs']))
            traits = [cat for cat in active_categories if data['features'][cat]]
            traits_str = ", ".join(traits) if traits else "Wszystkie wariacje wyłączone"
            report += f"🔹 SZABLON {t_id} (Rynki: {langs})\n   Włączone cechy: {traits_str}\n" + "-" * 40 + "\n"

        st.download_button(
            label="💾 Pobierz Raport (.txt)",
            data=report,
            file_name="macierz_konfiguracji.txt",
            mime="text/plain"
        )
        
        st.text_area("Podgląd Eksportu:", value=report, height=400)