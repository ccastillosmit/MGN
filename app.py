import streamlit as st
import anthropic
import httpx
import base64
import json
import re
import urllib.request
import urllib.error
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import io
import tempfile
import os

# ============================================================
#  CONFIGURACIÓN DE PÁGINA
# ============================================================

st.set_page_config(
    page_title="MyGrandmaNina — Procesador de Contenido",
    page_icon="🧡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
#  ESTILOS PERSONALIZADOS
# ============================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Lato:wght@300;400;700&display=swap');

    /* Fondo general */
    .stApp {
        background: linear-gradient(135deg, #FDF6F0 0%, #F9EDE4 50%, #FDF6F0 100%);
        font-family: 'Lato', sans-serif;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2C1810 0%, #4A2C1A 100%);
        border-right: 3px solid #D4913A;
    }
    [data-testid="stSidebar"] * {
        color: #F0C9B0 !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stFileUploader label {
        color: #F0C9B0 !important;
        font-family: 'Lato', sans-serif;
        font-weight: 700;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        font-size: 0.75rem;
    }

    /* Título principal */
    .main-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #2C1810;
        text-align: center;
        letter-spacing: -0.02em;
        margin-bottom: 0.2rem;
        line-height: 1.1;
    }
    .main-subtitle {
        font-family: 'Lato', sans-serif;
        font-size: 0.95rem;
        color: #8B6355;
        text-align: center;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }

    /* Cards de output */
    .output-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 24px rgba(44, 24, 16, 0.08);
        border: 1px solid #F0C9B0;
        margin-bottom: 1rem;
    }
    .output-label {
        font-family: 'Playfair Display', serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #2C1810;
        margin-bottom: 0.5rem;
    }

    /* Caption box */
    .caption-box {
        background: linear-gradient(135deg, #FDF6F0, #F9EDE4);
        border-left: 4px solid #D4913A;
        border-radius: 0 12px 12px 0;
        padding: 1.2rem 1.5rem;
        font-family: 'Lato', sans-serif;
        font-size: 0.9rem;
        color: #3D2314;
        line-height: 1.7;
        white-space: pre-wrap;
        word-wrap: break-word;
    }

    /* Botón principal */
    .stButton > button {
        background: linear-gradient(135deg, #D4913A, #C07830) !important;
        color: white !important;
        border: none !important;
        border-radius: 50px !important;
        padding: 0.7rem 2rem !important;
        font-family: 'Lato', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        font-size: 0.85rem !important;
        box-shadow: 0 4px 16px rgba(212, 145, 58, 0.35) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    .stButton > button:hover {
        box-shadow: 0 6px 24px rgba(212, 145, 58, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    /* Download buttons */
    .stDownloadButton > button {
        background: white !important;
        color: #D4913A !important;
        border: 2px solid #D4913A !important;
        border-radius: 50px !important;
        font-family: 'Lato', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        font-size: 0.8rem !important;
        width: 100% !important;
    }

    /* Divider */
    .divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #D4913A, transparent);
        margin: 2rem 0;
        border: none;
    }

    /* Status badge */
    .status-ok {
        display: inline-block;
        background: #E8F5E9;
        color: #2E7D32;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
    }
    .status-skip {
        display: inline-block;
        background: #FFF3E0;
        color: #E65100;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.05em;
    }

    /* Info box */
    .info-box {
        background: rgba(212, 145, 58, 0.08);
        border: 1px solid rgba(212, 145, 58, 0.3);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        font-size: 0.85rem;
        color: #5C3D1E;
        margin: 1rem 0;
    }

    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Spinner color */
    .stSpinner > div {
        border-top-color: #D4913A !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
#  FILOSOFÍA DE MARCA
# ============================================================

MARCA = """
Sos el community manager de MyGrandmaNina, una marca artesanal argentina de
artículos para bebés y niños de Córdoba. Vende productos tejidos a mano:
móviles de cuna crochet, muñecos amigurumi, ropa de bebé tejida, gimnasios
de madera, letras decorativas y accesorios artesanales.

FILOSOFÍA: "Cada bebé merece recibir el mundo envuelto en amor."
Los productos son artesanales, como los haría una abuela con amor.

TONO DE VOZ:
- Cálido, maternal, cercano, rioplatense argentino
- "mirá", "re", "bárbaro", "hermoso", "divino", "¿te lo imaginás?"
- Nunca "peque" — siempre "bebé", "nene", "nena", "chiquito/a"
- Emojis moderados: 🧡 🌈 👶 🤍 ✨

PALETA DE COLORES: ocre #D4913A, rosa palo #E8A898, sage #B5BCAF, durazno #F0C9B0
"""

# ============================================================
#  FUNCIONES CORE (adaptadas del script original)
# ============================================================

def imagen_a_base64(img_bytes: bytes, media_type: str = "image/jpeg") -> tuple[str, str]:
    return base64.standard_b64encode(img_bytes).decode("utf-8"), media_type

def redimensionar_logo(logo: Image.Image, ancho_foto: int, porcentaje: float, opacidad: int = 255) -> Image.Image:
    ancho_destino = int(ancho_foto * porcentaje)
    ratio = ancho_destino / logo.width
    nuevo_alto = int(logo.height * ratio)
    logo = logo.resize((ancho_destino, nuevo_alto), Image.LANCZOS)
    r, g, b, a = logo.split()
    a = a.point(lambda x: min(x, opacidad))
    return Image.merge("RGBA", (r, g, b, a))

def pegar_logo(foto: Image.Image, logo: Image.Image, posicion: str, margen_pct: float = 0.025) -> Image.Image:
    fw, fh = foto.size
    lw, lh = logo.size
    margen = int(fw * margen_pct)
    posiciones = {
        "superior_izquierda": (margen, margen),
        "superior_derecha": (fw - lw - margen, margen),
        "inferior_izquierda": (margen, fh - lh - margen),
        "inferior_derecha": (fw - lw - margen, fh - lh - margen),
        "centro_superior": ((fw - lw) // 2, margen),
    }
    x, y = posiciones.get(posicion, posiciones["inferior_derecha"])
    foto.paste(logo, (x, y), logo)
    return foto

def agregar_texto_historia(foto: Image.Image, texto: str, estilo: str, posicion_texto: str) -> Image.Image:
    draw = ImageDraw.Draw(foto)
    fw, fh = foto.size
    tam_fuente = int(fw * 0.07)
    try:
        fuente = ImageFont.truetype("arialbd.ttf", size=tam_fuente)
    except Exception:
        try:
            fuente = ImageFont.truetype("arial.ttf", size=tam_fuente)
        except Exception:
            fuente = ImageFont.load_default()

    color_texto = (255, 255, 255) if estilo == "blanco" else (60, 40, 20)
    posiciones_y = {"superior": int(fh * 0.15), "centro": int(fh * 0.45), "inferior": int(fh * 0.72)}
    y_texto = posiciones_y.get(posicion_texto, int(fh * 0.72))
    lineas = texto.split("\n") if "\n" in texto else [texto]

    for i, linea in enumerate(lineas):
        bbox = draw.textbbox((0, 0), linea, font=fuente)
        ancho_texto = bbox[2] - bbox[0]
        x_texto = (fw - ancho_texto) // 2
        y_actual = y_texto + i * int(fw * 0.10)
        draw.text((x_texto + 2, y_actual + 2), linea, font=fuente, fill=(0, 0, 0, 120))
        draw.text((x_texto, y_actual), linea, font=fuente, fill=color_texto)
    return foto

def analizar_foto(img_bytes: bytes, media_type: str, destino: str, api_key: str) -> dict:
    imagen_b64, tipo_mime = imagen_a_base64(img_bytes, media_type)

    prompt_gemini = """
Además, generá un campo "prompt_imagen_contextual" con un prompt en inglés
para Imagen 3 de Google que genere una foto de lifestyle mostrando este producto
en uso: un bebé o niño usándolo, o una habitación infantil decorada con él.
El prompt debe:
- Describir el producto con detalle (colores, texturas, materiales)
- Pedir estilo fotografía lifestyle real, luz natural, fondo neutro o madera clara
- Tono cálido y amoroso, paleta pastel
- Máximo 3 oraciones en inglés
- NO mencionar marcas ni logos
"""

    if destino == "feed":
        prompt_destino = f"""
Esta foto va al FEED de Instagram.

Devolvé ÚNICAMENTE un JSON válido sin texto antes ni después:
{{
  "caption": "caption completo para Instagram acá",
  "posicion_logo": "inferior_derecha",
  "razon_posicion": "breve explicación",
  "prompt_imagen_contextual": "prompt en inglés para Imagen 3"
}}

Para posicion_logo usá solo: "superior_izquierda", "superior_derecha",
"inferior_izquierda", "inferior_derecha".
Elegí donde el logo no tape el producto ni la cara del bebé.

El caption debe seguir este formato:
1. Frase gancho emotiva (máx 10 palabras)
2. Cuerpo: 2-3 oraciones cálidas describiendo el producto
3. Call to action suave por DM
4. 10-15 hashtags en español e inglés
5. Línea final fija: "Visitá nuestra tienda 👉 https://mygrandmanina.mitiendanube.com"

{prompt_gemini}
"""
    else:
        prompt_destino = f"""
Esta foto va a una HISTORIA de Instagram (formato vertical 9:16).

Devolvé ÚNICAMENTE un JSON válido sin texto antes ni después:
{{
  "caption": "caption completo para Instagram acá",
  "posicion_logo": "centro_superior",
  "razon_posicion": "breve explicación",
  "texto_superpuesto": "texto corto para poner sobre la imagen (máx 2 líneas)",
  "estilo_texto": "blanco",
  "posicion_texto": "inferior",
  "tipo_contenido": "emotivo",
  "prompt_imagen_contextual": "prompt en inglés para Imagen 3"
}}

El caption:
1. Frase gancho emotiva (máx 10 palabras)
2. Cuerpo: 2-3 oraciones cálidas
3. Call to action suave
4. 10-15 hashtags
5. Línea final fija: "Visitá nuestra tienda 👉 https://mygrandmanina.mitiendanube.com"

{prompt_gemini}
"""

    cliente = anthropic.Anthropic(
        api_key=api_key,
        http_client=httpx.Client(timeout=120.0)
    )
    mensaje = cliente.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1800,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": tipo_mime, "data": imagen_b64}},
                {"type": "text", "text": MARCA + "\n\n" + prompt_destino}
            ]
        }]
    )

    respuesta = re.sub(r"```json|```", "", mensaje.content[0].text).strip()
    return json.loads(respuesta)

def procesar_feed(img_bytes: bytes, logo_img: Image.Image, analisis: dict) -> bytes:
    foto = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    logo = redimensionar_logo(logo_img.copy(), foto.width, 0.18)
    foto = pegar_logo(foto, logo, analisis.get("posicion_logo", "inferior_derecha"))
    buf = io.BytesIO()
    foto.convert("RGB").save(buf, "JPEG", quality=95)
    return buf.getvalue()

def procesar_historia(img_bytes: bytes, logo_img: Image.Image, analisis: dict) -> bytes:
    foto = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    fw, fh = foto.size

    alto_destino = int(fw * 16 / 9)
    if fh < alto_destino:
        ancho_destino = int(fh * 9 / 16)
        left = (fw - ancho_destino) // 2
        foto = foto.crop((left, 0, left + ancho_destino, fh))
    else:
        top = (fh - alto_destino) // 2
        foto = foto.crop((0, top, fw, top + alto_destino))

    foto = foto.resize((1080, 1920), Image.LANCZOS)
    logo = redimensionar_logo(logo_img.copy(), 1080, 0.28)
    foto = pegar_logo(foto, logo, analisis.get("posicion_logo", "centro_superior"), margen_pct=0.055)

    texto = analisis.get("texto_superpuesto", "")
    if texto:
        foto = agregar_texto_historia(foto, texto, analisis.get("estilo_texto", "blanco"), analisis.get("posicion_texto", "inferior"))

    buf = io.BytesIO()
    foto.convert("RGB").save(buf, "JPEG", quality=95)
    return buf.getvalue()

def generar_imagen_contextual(prompt: str, gemini_key: str) -> bytes | None:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:predict?key={gemini_key}"
    payload = json.dumps({
        "instances": [{"prompt": prompt}],
        "parameters": {"aspectRatio": "1:1", "sampleCount": 1, "safetyFilterLevel": "block_only_high", "personGeneration": "allow_adult"}
    }).encode("utf-8")

    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        imagen_b64 = data["predictions"][0]["bytesBase64Encoded"]
        return base64.b64decode(imagen_b64)
    except Exception:
        return None

# ============================================================
#  INTERFAZ — SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 1.5rem;'>
        <div style='font-family: Playfair Display, serif; font-size: 1.4rem; font-weight: 700; color: #F0C9B0; letter-spacing: -0.01em;'>MyGrandmaNina</div>
        <div style='font-size: 0.65rem; letter-spacing: 0.2em; color: #C4956A; text-transform: uppercase; margin-top: 0.2rem;'>Procesador de Contenido</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("<div style='font-size:0.7rem; letter-spacing:0.15em; text-transform:uppercase; color:#C4956A; font-weight:700; margin-bottom:0.5rem;'>🔑 API Keys</div>", unsafe_allow_html=True)

    anthropic_key = st.text_input(
        "Anthropic (Claude)",
        value="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",
        type="password",
        help="Tu API key de Anthropic"
    )

    gemini_key = st.text_input(
        "Gemini (Google)",
        value="AIzaSyAgb6MQYiVJasBOl6Xze9aQNpyEDGRW3lw",
        type="password",
        help="Tu API key de Google AI Studio"
    )

    st.markdown("---")

    st.markdown("<div style='font-size:0.7rem; letter-spacing:0.15em; text-transform:uppercase; color:#C4956A; font-weight:700; margin-bottom:0.5rem;'>⚙️ Configuración</div>", unsafe_allow_html=True)

    destino = st.selectbox(
        "Destino del contenido",
        options=["feed", "historia"],
        format_func=lambda x: "📷 Feed de Instagram" if x == "feed" else "📱 Historia de Instagram"
    )

    generar_contextual = st.checkbox("Generar imagen contextual (Gemini)", value=False)

    st.markdown("---")

    st.markdown("<div style='font-size:0.7rem; letter-spacing:0.15em; text-transform:uppercase; color:#C4956A; font-weight:700; margin-bottom:0.5rem;'>🖼️ Logo de marca</div>", unsafe_allow_html=True)

    logo_file = st.file_uploader(
        "Subí el logo PNG (fondo transparente)",
        type=["png"],
        help="Logo con fondo transparente (.png)"
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem; color:#8B6355; line-height:1.6; text-align:center;'>
        v2.0 · Fase 1<br>
        <span style='color:#C4956A;'>🧡</span> Hecho con amor
    </div>
    """, unsafe_allow_html=True)

# ============================================================
#  INTERFAZ — MAIN
# ============================================================

st.markdown('<div class="main-title">🧡 MyGrandmaNina</div>', unsafe_allow_html=True)
st.markdown('<div class="main-subtitle">Procesador automático de contenido para Instagram</div>', unsafe_allow_html=True)

# Upload de foto
col_upload, col_info = st.columns([2, 1])

with col_upload:
    foto_file = st.file_uploader(
        "📸 Subí la foto del producto",
        type=["jpg", "jpeg", "png", "webp"],
        help="La foto que querés procesar para Instagram"
    )

with col_info:
    if foto_file:
        st.markdown(f"""
        <div class="info-box">
            <strong>📁 Archivo:</strong> {foto_file.name}<br>
            <strong>📐 Tamaño:</strong> {foto_file.size // 1024} KB<br>
            <strong>🎯 Destino:</strong> {'Feed' if destino == 'feed' else 'Historia'}<br>
            <strong>🖼️ Logo:</strong> {'✅ Cargado' if logo_file else '⚠️ Sin logo'}
        </div>
        """, unsafe_allow_html=True)

# Validaciones
can_process = foto_file is not None and logo_file is not None and anthropic_key

if foto_file and not logo_file:
    st.warning("⚠️ Necesitás subir el logo PNG para procesar la foto.")

if foto_file and logo_file:
    # Preview de la foto original
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    col_prev, col_btn = st.columns([3, 1])
    with col_prev:
        st.markdown("**Vista previa — foto original**")
        preview_img = Image.open(foto_file)
        st.image(preview_img, use_container_width=True)
        foto_file.seek(0)
    with col_btn:
        st.markdown("<br><br>", unsafe_allow_html=True)
        procesar = st.button("✨ Procesar foto", disabled=not can_process)

    # ── PROCESAMIENTO ────────────────────────────────────
    if procesar:
        img_bytes = foto_file.read()
        logo_img = Image.open(logo_file).convert("RGBA")

        ext = foto_file.name.split(".")[-1].lower()
        media_type_map = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}
        media_type = media_type_map.get(ext, "image/jpeg")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("### ✨ Resultados")

        # Paso 1: Claude analiza
        with st.spinner("🤖 Claude está analizando tu foto..."):
            try:
                analisis = analizar_foto(img_bytes, media_type, destino, anthropic_key)
                st.success(f"✅ Análisis listo — Logo en: **{analisis.get('posicion_logo')}** ({analisis.get('razon_posicion')})")
            except Exception as e:
                st.error(f"❌ Error al analizar la foto: {e}")
                st.stop()

        # Paso 2: Generar imágenes
        col1, col2, col3 = st.columns(3)

        with col1:
            with st.spinner("📷 Generando imagen para Feed..."):
                feed_bytes = procesar_feed(img_bytes, logo_img, analisis)
            st.markdown('<div class="output-card">', unsafe_allow_html=True)
            st.markdown('<div class="output-label">📷 Feed de Instagram</div>', unsafe_allow_html=True)
            st.image(feed_bytes, use_container_width=True)
            st.download_button(
                "⬇️ Descargar Feed",
                data=feed_bytes,
                file_name="mygrandmanina_feed.jpg",
                mime="image/jpeg"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            with st.spinner("📱 Generando Historia..."):
                historia_bytes = procesar_historia(img_bytes, logo_img, analisis)
            st.markdown('<div class="output-card">', unsafe_allow_html=True)
            st.markdown('<div class="output-label">📱 Historia de Instagram</div>', unsafe_allow_html=True)
            st.image(historia_bytes, use_container_width=True)
            st.download_button(
                "⬇️ Descargar Historia",
                data=historia_bytes,
                file_name="mygrandmanina_historia.jpg",
                mime="image/jpeg"
            )
            st.markdown('</div>', unsafe_allow_html=True)

        with col3:
            st.markdown('<div class="output-card">', unsafe_allow_html=True)
            st.markdown('<div class="output-label">🎨 Imagen Contextual (Gemini)</div>', unsafe_allow_html=True)
            if generar_contextual and gemini_key:
                prompt_img = analisis.get("prompt_imagen_contextual", "")
                if prompt_img:
                    with st.spinner("🎨 Gemini generando imagen..."):
                        contextual_bytes = generar_imagen_contextual(prompt_img, gemini_key)
                    if contextual_bytes:
                        st.image(contextual_bytes, use_container_width=True)
                        st.download_button(
                            "⬇️ Descargar Contextual",
                            data=contextual_bytes,
                            file_name="mygrandmanina_contextual.jpg",
                            mime="image/jpeg"
                        )
                    else:
                        st.warning("⚠️ No se pudo generar con Gemini. Verificá tu API key o plan.")
                        st.markdown(f"**Prompt generado:**\n\n_{prompt_img}_")
                else:
                    st.info("Claude no generó prompt para imagen contextual.")
            else:
                st.markdown("""
                <div style='text-align:center; padding: 2rem 1rem; color: #B5BCAF;'>
                    <div style='font-size: 2rem; margin-bottom: 0.5rem;'>🎨</div>
                    <div style='font-size: 0.85rem;'>Activá "Generar imagen contextual" en el panel lateral para usar esta función</div>
                </div>
                """, unsafe_allow_html=True)
                if analisis.get("prompt_imagen_contextual"):
                    with st.expander("Ver prompt generado por Claude"):
                        st.write(analisis.get("prompt_imagen_contextual"))
            st.markdown('</div>', unsafe_allow_html=True)

        # ── CAPTION ─────────────────────────────────────
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown("### 📝 Caption para Instagram")

        caption = analisis.get("caption", "")
        st.markdown(f'<div class="caption-box">{caption}</div>', unsafe_allow_html=True)

        col_copy1, col_copy2 = st.columns([1, 3])
        with col_copy1:
            st.download_button(
                "⬇️ Descargar caption (.txt)",
                data=caption.encode("utf-8"),
                file_name="mygrandmanina_caption.txt",
                mime="text/plain"
            )

        # ── REPORTE ──────────────────────────────────────
        with st.expander("📊 Ver reporte completo del análisis"):
            reporte = f"""REPORTE DE ANÁLISIS — MyGrandmaNina
Destino: {destino.upper()}
Posición logo: {analisis.get('posicion_logo')}
Razón: {analisis.get('razon_posicion')}
"""
            if destino == "historia":
                reporte += f"""Texto superpuesto: {analisis.get('texto_superpuesto', '-')}
Estilo texto: {analisis.get('estilo_texto', '-')}
Tipo contenido: {analisis.get('tipo_contenido', '-')}
"""
            reporte += f"\nPrompt Gemini:\n{analisis.get('prompt_imagen_contextual', '-')}\n\nCAPTION:\n{caption}"
            st.code(reporte, language=None)

else:
    # Estado vacío
    st.markdown("""
    <div style='text-align:center; padding: 4rem 2rem; color: #C4956A;'>
        <div style='font-size: 4rem; margin-bottom: 1rem;'>🧡</div>
        <div style='font-family: Playfair Display, serif; font-size: 1.5rem; color: #2C1810; margin-bottom: 0.5rem;'>
            Subí una foto para empezar
        </div>
        <div style='font-size: 0.9rem; color: #8B6355; max-width: 400px; margin: 0 auto; line-height: 1.6;'>
            Cargá la foto del producto y el logo PNG en el panel lateral, elegí el destino y hacé clic en <strong>Procesar foto</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)
