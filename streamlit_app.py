from __future__ import annotations

import json
import re
from typing import Dict, List, Tuple

import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI


st.set_page_config(
    page_title="Prompt Optimization Agent",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------------------------------- #
# LLM client (kurum içi / yerel LLM endpoint'i)
# --------------------------------------------------------------------------- #


def get_client() -> OpenAI:
    api_key = st.secrets.get("LLM_API_KEY", "")
    base_url = st.secrets.get("LLM_BASE_URL", "")
    if not api_key:
        st.error(
            "`LLM_API_KEY` bulunamadı. Streamlit Cloud → **Settings → Secrets** "
            "bölümüne `LLM_API_KEY`, `LLM_BASE_URL` ve `LLM_MODEL` ekleyin."
        )
        st.stop()
    return OpenAI(api_key=api_key, base_url=base_url or None)


def get_model() -> str:
    model = st.secrets.get("LLM_MODEL", "")
    if not model:
        st.error("`LLM_MODEL` yapılandırılmamış. Secrets içinden tanımlayın.")
        st.stop()
    return model


# --------------------------------------------------------------------------- #
# Sabitler
# --------------------------------------------------------------------------- #


HEDEF_AGENTLAR = {
    "General Purpose": (
        "Genel amaçlı kullanım. Dengeli bir yaklaşımla bağlam, rol, format ve "
        "kısıtlar eklenir."
    ),
    "Code Assist": (
        "Kod asistanı için optimizasyon. Programlama dili / framework, girdi-çıktı "
        "örnekleri, error handling, test beklentisi gibi teknik detaylar öne çıkarılır."
    ),
    "MailCraft": (
        "E-posta üretim ajanı için optimizasyon. Ton, hedef kitle, amaç, uzunluk "
        "ve dil kısıtları belirlenir."
    ),
}

CIKTI_DILLERI = ["Girdi ile aynı", "İngilizce", "Türkçe"]

CIKTI_FORMATLARI = {
    "Serbest (model karar versin)": "serbest",
    "Step-by-step (numaralı adımlar)": "step_by_step",
    "Instruction-based (talimat listesi)": "instruction",
    "JSON şeması iste": "json",
}

TONLAR_AGENTA_GORE = {
    "Code Assist": ["Nesnel ve teknik", "Kısa ve net", "Kapsamlı açıklamalı"],
    "MailCraft": ["Resmî", "Samimi", "Nazik ve profesyonel", "İkna edici"],
    "General Purpose": ["Nötr", "Resmî", "Samimi"],
}


# --------------------------------------------------------------------------- #
# Prompt inşası
# --------------------------------------------------------------------------- #


def sistem_promptu() -> str:
    return (
        "Sen Prompt Optimization Agent'sın. Görevin, kullanıcıdan gelen ham "
        "promptu analiz edip çok daha net, etkili ve sonuç odaklı bir prompta "
        "dönüştürmektir.\n\n"
        "ANALİZ KRİTERLERİ:\n"
        "- Belirsizlik (ambiguity)\n"
        "- Eksik bağlam (missing context)\n"
        "- Yapısal zayıflık\n"
        "- Output beklentisinin net olmaması\n\n"
        "UYGULANACAK TEKNİKLER:\n"
        "- Context ekleme (alan, amaç, arka plan)\n"
        "- Rol tanımlama (örn. 'You are a senior Python developer…')\n"
        "- Format belirleme (bullet, JSON, step-by-step vb.)\n"
        "- Constraint ekleme (limitler, ton, dil, uzunluk)\n\n"
        "HEDEF AGENT'A GÖRE ODAK:\n"
        "- Code Assist → dil/framework, girdi-çıktı, error handling, test\n"
        "- MailCraft → ton, hedef kitle, uzunluk, amaç, dil\n"
        "- General Purpose → dengeli yaklaşım\n\n"
        "ÇIKTI KURALLARI (ÇOK ÖNEMLİ):\n"
        "Yanıtını YALNIZCA aşağıdaki üç bölümlü formatta ver. Başka hiçbir "
        "giriş, selamlama veya markdown başlığı ekleme.\n\n"
        "---OPTIMIZED_PROMPT---\n"
        "<optimize edilmiş, doğrudan kullanılabilir prompt metni>\n\n"
        "---EXPLANATION---\n"
        "<neyin değiştiği ve neden değiştirildiği — 3-6 bullet>\n\n"
        "---TIPS---\n"
        "<benzer promptlar için 3-5 hızlı öneri — her madde - ile başlasın>\n"
    )


def kullanici_promptu(
    ham_prompt: str,
    hedef_agent: str,
    cikti_dili: str,
    cikti_formati: str,
    ton: str,
    role_ekle: bool,
) -> str:
    parcalar: List[str] = []
    parcalar.append(f"Hedef agent: {hedef_agent}")
    parcalar.append(f"Çıktı dili: {cikti_dili}")

    format_aciklama = {
        "serbest": "Serbest format — en uygun yapıyı kendin seç.",
        "step_by_step": "Step-by-step format — numaralı adımlar halinde yaz.",
        "instruction": (
            "Instruction-based format — rol + gereksinimler + kısıtlar sırasında "
            "talimat listesi kullan."
        ),
        "json": (
            "Modelin JSON formatında cevap vermesini isteyen bir prompt kur; "
            "beklenen JSON şemasını açık şekilde tanımla."
        ),
    }[cikti_formati]
    parcalar.append(f"Çıktı formatı: {format_aciklama}")

    if ton and ton != "Belirtilmedi":
        parcalar.append(f"İstenen ton: {ton}")

    if role_ekle:
        parcalar.append(
            "Optimize edilen promptun başına uygun bir rol tanımı ekle (örn. "
            "'You are a senior …')."
        )
    else:
        parcalar.append("Rol tanımı eklemeni zorunlu kılmıyoruz; gerekli görürsen ekleyebilirsin.")

    parcalar.append("Kullanıcının ham promptu:\n---\n" + ham_prompt.strip() + "\n---")
    return "\n\n".join(parcalar)


# --------------------------------------------------------------------------- #
# Çıktı ayrıştırma
# --------------------------------------------------------------------------- #


_SECTION_RE = re.compile(
    r"---OPTIMIZED_PROMPT---\s*(?P<opt>.*?)\s*"
    r"---EXPLANATION---\s*(?P<exp>.*?)\s*"
    r"---TIPS---\s*(?P<tips>.*)$",
    re.DOTALL,
)


def ayristir(cevap: str) -> Tuple[str, str, List[str]]:
    m = _SECTION_RE.search(cevap or "")
    if not m:
        return cevap.strip(), "", []

    optimized = m.group("opt").strip()
    explanation = m.group("exp").strip()
    tips_raw = m.group("tips").strip()

    tips: List[str] = []
    for line in tips_raw.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.startswith(("-", "*", "•")):
            s = s.lstrip("-*• ").strip()
        if s:
            tips.append(s)

    return optimized, explanation, tips


# --------------------------------------------------------------------------- #
# LLM çağrısı
# --------------------------------------------------------------------------- #


def optimize_et(
    ham_prompt: str,
    hedef_agent: str,
    cikti_dili: str,
    cikti_formati: str,
    ton: str,
    role_ekle: bool,
    temperature: float = 0.5,
) -> str:
    client = get_client()
    model = get_model()
    messages = [
        {"role": "system", "content": sistem_promptu()},
        {
            "role": "user",
            "content": kullanici_promptu(
                ham_prompt=ham_prompt,
                hedef_agent=hedef_agent,
                cikti_dili=cikti_dili,
                cikti_formati=cikti_formati,
                ton=ton,
                role_ekle=role_ekle,
            ),
        },
    ]
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return (resp.choices[0].message.content or "").strip()


# --------------------------------------------------------------------------- #
# Kopyala butonu (JS tabanlı)
# --------------------------------------------------------------------------- #


def kopyala_butonu(metin: str, key: str = "copy") -> None:
    js_metin = json.dumps(metin)
    components.html(
        f"""
        <!doctype html><html><head><style>
          html, body {{ margin:0; padding:0; background:transparent !important;
            color:#d0d0d0;
            font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Source Sans Pro',sans-serif; }}
          @media (prefers-color-scheme: light) {{ html, body {{ color:#222; }} }}
          #wrap {{ display:flex; justify-content:flex-end; }}
          #btn-{key} {{
            padding:6px 14px; border-radius:8px; cursor:pointer;
            font-size:14px; font-weight:500;
            border:1px solid rgba(128,128,128,0.35);
            background:transparent; color:inherit;
            transition:background 0.15s ease;
          }}
          #btn-{key}:hover {{ background:rgba(128,128,128,0.15); }}
        </style></head><body>
          <div id="wrap"><button id="btn-{key}">Kopyala</button></div>
          <script>
            const btn = document.getElementById("btn-{key}");
            btn.addEventListener("click", async () => {{
              try {{
                await navigator.clipboard.writeText({js_metin});
                const old = btn.innerText;
                btn.innerText = "Kopyalandı ✓";
                setTimeout(() => {{ btn.innerText = old; }}, 1500);
              }} catch (e) {{
                btn.innerText = "Kopyalanamadı";
              }}
            }});
          </script>
        </body></html>
        """,
        height=40,
    )


# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #


st.title("Prompt Optimization Agent")
st.caption(
    "Ham promptunuzu yapıştırın, sistem rol / bağlam / format / kısıtları "
    "ekleyerek sonuç odaklı bir prompta dönüştürsün."
)

with st.sidebar:
    st.header("Ayarlar")
    temperature = st.slider(
        "Yaratıcılık (temperature)", 0.0, 1.2, 0.5, 0.1,
        help=(
            "Düşük değer daha deterministik çıktı verir; yüksek değer daha çeşitli "
            "optimize prompt önerileri üretir."
        ),
    )
    role_ekle = st.checkbox(
        "Rol tanımı ekle (You are a …)", value=True,
        help="Optimize edilen promptun başına uygun bir rol tanımı eklenir.",
    )
    st.divider()
    with st.expander("ℹ️ Nasıl kullanılır?"):
        st.markdown(
            "1. **Ham promptu** yapıştırın.\n"
            "2. **Hedef agent** seçin (Code Assist / MailCraft / Genel).\n"
            "3. Dilerseniz **çıktı dili** ve **format** tercihini değiştirin.\n"
            "4. **Optimize Et** butonuna basın.\n"
            "5. Üretilen 3 bölümlü çıktıyı kopyalayıp kullanın."
        )

hedef_agent = st.radio(
    "Hedef Agent",
    list(HEDEF_AGENTLAR.keys()),
    index=0,
    horizontal=True,
    help="Optimizasyon, seçilen agent'ın beklentilerine göre şekillenir.",
)
st.caption(HEDEF_AGENTLAR[hedef_agent])

col_left, col_right = st.columns(2)
with col_left:
    cikti_dili = st.selectbox("Çıktı Dili", CIKTI_DILLERI, index=0)
with col_right:
    format_label = st.selectbox("Çıktı Formatı", list(CIKTI_FORMATLARI.keys()), index=0)
    cikti_formati = CIKTI_FORMATLARI[format_label]

ton_secenekleri = ["Belirtilmedi"] + TONLAR_AGENTA_GORE.get(hedef_agent, [])
ton = st.selectbox("İstenen Ton (opsiyonel)", ton_secenekleri, index=0)

ham_prompt = st.text_area(
    "Ham Prompt",
    height=180,
    placeholder=(
        "Örn. python kodu yaz api çağıran\n"
        "Örn. müşteriye gecikme için mail yaz\n"
        "Örn. bana marketing fikri ver"
    ),
)

olustur = st.button("✨ Optimize Et", type="primary", use_container_width=True)


if "son_cikti" not in st.session_state:
    st.session_state.son_cikti = ""
if "son_parsed" not in st.session_state:
    st.session_state.son_parsed = ("", "", [])
if "son_payload" not in st.session_state:
    st.session_state.son_payload = None


def _calistir(payload: Dict, temperature_val: float) -> None:
    with st.spinner("Prompt optimize ediliyor..."):
        try:
            raw = optimize_et(**payload, temperature=temperature_val)
            st.session_state.son_cikti = raw
            st.session_state.son_parsed = ayristir(raw)
            st.session_state.son_payload = payload
        except Exception as e:
            st.error(f"Üretim sırasında bir hata oluştu: {e}")


if olustur:
    if not ham_prompt.strip():
        st.warning("Lütfen optimize edilecek ham promptu girin.")
    else:
        payload = dict(
            ham_prompt=ham_prompt,
            hedef_agent=hedef_agent,
            cikti_dili=cikti_dili,
            cikti_formati=cikti_formati,
            ton=ton,
            role_ekle=role_ekle,
        )
        _calistir(payload, temperature)


if st.session_state.son_cikti:
    optimized, explanation, tips = st.session_state.son_parsed

    st.divider()

    st.subheader("✨ Optimized Prompt")
    if optimized:
        kopyala_butonu(optimized, key="opt")
        st.code(optimized, language="markdown")
    else:
        st.info("Optimize edilmiş prompt ayrıştırılamadı. Ham çıktıya aşağıdan bakabilirsiniz.")

    st.subheader("🔍 Improvement Explanation")
    if explanation:
        st.markdown(explanation)
    else:
        st.caption("Açıklama bölümü üretilmedi.")

    st.subheader("⚡ Quick Tips")
    if tips:
        for t in tips:
            st.markdown(f"- {t}")
    else:
        st.caption("Hızlı öneri bölümü üretilmedi.")

    with st.expander("Ham model çıktısı"):
        st.text(st.session_state.son_cikti)

    st.divider()
    if st.button("🔁 Yeniden Üret", use_container_width=True):
        if st.session_state.son_payload:
            _calistir(st.session_state.son_payload, min(1.2, temperature + 0.2))
            st.rerun()
