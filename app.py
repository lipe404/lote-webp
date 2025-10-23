import streamlit as st
from PIL import Image
import io
import zipfile
import os

st.set_page_config(page_title="Conversor JPG → WEBP", page_icon="🖼️", layout="centered")

st.title("🖼️ Conversor de Imagens JPG para WEBP em Lote")
st.write("Envie vários arquivos JPG e baixe todos convertidos para o formato WEBP.")

uploaded_files = st.file_uploader(
    "Selecione os arquivos JPG", type=["jpg", "jpeg"], accept_multiple_files=True
)

quality = st.slider("Qualidade da conversão (WEBP)", 1, 100, 80)

if uploaded_files:
    st.info(f"{len(uploaded_files)} arquivo(s) enviado(s).")
    converted_files = []

    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, file in enumerate(uploaded_files):
        image = Image.open(file).convert("RGB")
        output = io.BytesIO()
        image.save(output, format="WEBP", quality=quality)
        output.seek(0)

        new_filename = os.path.splitext(file.name)[0] + ".webp"
        converted_files.append((new_filename, output))

        # Atualiza barra de progresso
        progress_bar.progress((i + 1) / len(uploaded_files))
        status_text.text(f"Convertendo {i + 1}/{len(uploaded_files)} arquivos...")

    status_text.text("✅ Conversão concluída com sucesso!")

    # Mostra prévia apenas das 3 primeiras imagens
    with st.expander("👀 Pré-visualizar (mostrando 3 primeiras)"):
        for name, data in converted_files[:3]:
            st.image(data, caption=name, use_column_width=True)
        if len(converted_files) > 3:
            st.caption(f"... e mais {len(converted_files) - 3} imagens convertidas.")

    # Cria ZIP em memória
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for name, data in converted_files:
            zipf.writestr(name, data.getvalue())
    zip_buffer.seek(0)

    st.download_button(
        label="📦 Baixar todos em ZIP",
        data=zip_buffer,
        file_name="imagens_convertidas_webp.zip",
        mime="application/zip",
    )

    progress_bar.empty()
else:
    st.warning("Envie pelo menos um arquivo JPG para iniciar a conversão.")
