import streamlit as st
from PIL import Image
import io
import zipfile
import os

# ========================
# CONFIGURAÇÃO INICIAL
# ========================
st.set_page_config(
    page_title="Conversor Universal de Imagens", page_icon="🖼️", layout="centered"
)

st.title("Conversor Universal de Imagens em Lote")
st.write(
    "Converta imagens de **qualquer formato** para **outro formato** com controle de qualidade."
)

# OPÇÕES DE FORMATO
formatos_suportados = ["JPG", "JPEG", "PNG", "WEBP", "BMP", "TIFF"]

col1, col2 = st.columns(2)
with col1:
    formato_entrada = st.selectbox(
        "Formato de entrada", formatos_suportados, index=0
    )
with col2:
    formato_saida = st.selectbox("Formato de saída", formatos_suportados, index=2)

# Upload dos arquivos
uploaded_files = st.file_uploader(
    f"Selecione os arquivos {formato_entrada}",
    type=[formato_entrada.lower()],
    accept_multiple_files=True,
)

# Controle de qualidade (apenas para formatos com compressão)
if formato_saida in ["JPG", "JPEG", "WEBP"]:
    quality = st.slider("Qualidade da conversão", 1, 100, 85)
else:
    quality = None

# PROCESSAMENTO
if uploaded_files:
    st.info(f"{len(uploaded_files)} arquivo(s) enviado(s).")
    converted_files = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, file in enumerate(uploaded_files):
        try:
            image = Image.open(file)
            # Converte transparência se for RGB
            if formato_saida in ["JPG", "JPEG"] and image.mode in ("RGBA", "LA"):
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])
                image = background
            else:
                image = image.convert("RGB")

            # Converte e salva em memória
            output = io.BytesIO()
            save_params = {"format": formato_saida}
            if quality:
                save_params["quality"] = quality

            image.save(output, **save_params)
            output.seek(0)

            new_filename = os.path.splitext(file.name)[0] + f".{formato_saida.lower()}"
            converted_files.append((new_filename, output))

        except Exception as e:
            st.error(f"Erro ao converter {file.name}: {e}")

        progress_bar.progress((i + 1) / len(uploaded_files))
        status_text.text(f"Convertendo {i + 1}/{len(uploaded_files)} arquivos...")

    progress_bar.empty()
    status_text.text("Conversão concluída com sucesso!")

    # PRÉ-VISUALIZAÇÃO
    with st.expander("Pré-visualizar (mostrando 3 primeiras)"):
        for name, data in converted_files[:3]:
            st.image(data, caption=name, use_column_width=True)
        if len(converted_files) > 3:
            st.caption(f"... e mais {len(converted_files) - 3} imagens convertidas.")

    # DOWNLOAD ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zipf:
        for name, data in converted_files:
            zipf.writestr(name, data.getvalue())
    zip_buffer.seek(0)

    st.download_button(
        label=f"Baixar todos em ZIP ({formato_saida})",
        data=zip_buffer,
        file_name=f"imagens_convertidas_{formato_saida.lower()}.zip",
        mime="application/zip",
    )
else:
    st.warning("Envie pelo menos um arquivo para iniciar a conversão.")
