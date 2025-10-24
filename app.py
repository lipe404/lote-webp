import streamlit as st
from PIL import Image
import io
import zipfile
import os
import tempfile
import concurrent.futures

# CONFIGURAÇÃO INICIAL
st.set_page_config(
    page_title="Conversor Universal de Imagens",
    page_icon="🖼️",
    layout="centered",
)

st.title("Conversor Universal de Imagens em Lote")
st.write(
    "Converta imagens de **qualquer formato** para **outro formato**, com redimensionamento, compressão adaptativa e suporte a pastas."
)

# OPÇÕES DE FORMATO
formatos_suportados = ["JPG", "JPEG", "PNG", "WEBP", "BMP", "TIFF"]

col1, col2 = st.columns(2)
with col1:
    formato_entrada = st.selectbox("Formato de entrada", formatos_suportados, index=0)
with col2:
    formato_saida = st.selectbox("Formato de saída", formatos_suportados, index=2)

# MODO DE CONVERSÃO
modo = st.radio(
    "Escolha o modo de entrada:",
    ["Arquivos individuais", "Pasta compactada (.zip)"],
    horizontal=True,
)

# UPLOAD
if modo == "Arquivos individuais":
    uploaded_files = st.file_uploader(
        f"Selecione os arquivos {formato_entrada}",
        type=[formato_entrada.lower()],
        accept_multiple_files=True,
    )
else:
    uploaded_zip = st.file_uploader(
        "Envie um arquivo ZIP contendo imagens", type=["zip"]
    )
    uploaded_files = []

# OPÇÕES DE PROCESSAMENTO
st.subheader("Configurações adicionais")

col3, col4 = st.columns(2)
with col3:
    max_width = st.number_input("Largura máxima (px, 0 = manter original)", 0, 10000, 0)
with col4:
    max_height = st.number_input("Altura máxima (px, 0 = manter original)", 0, 10000, 0)

adaptive_compression = st.checkbox(
    "Ativar compressão adaptativa (baseada no tamanho original)", True
)

if formato_saida in ["JPG", "JPEG", "WEBP"]:
    base_quality = st.slider("Qualidade base", 10, 100, 85)
else:
    base_quality = None


# FUNÇÃO DE CONVERSÃO
def process_image(file_data, filename):
    try:
        image = Image.open(io.BytesIO(file_data))
        original_size_kb = len(file_data) / 1024

        # Redimensionamento automático
        if max_width > 0 or max_height > 0:
            image.thumbnail((max_width or image.width, max_height or image.height))

        # Tratamento de transparência para JPG
        if formato_saida in ["JPG", "JPEG"] and image.mode in ("RGBA", "LA"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        else:
            image = image.convert("RGB")

        # Compressão adaptativa
        quality = base_quality
        if (
            adaptive_compression
            and base_quality
            and formato_saida in ["JPG", "JPEG", "WEBP"]
        ):
            if original_size_kb > 5000:
                quality = max(base_quality - 40, 40)
            elif original_size_kb > 2000:
                quality = max(base_quality - 20, 50)
            elif original_size_kb > 1000:
                quality = max(base_quality - 10, 60)

        output = io.BytesIO()
        save_params = {"format": formato_saida}
        if quality:
            save_params["quality"] = quality

        image.save(output, **save_params)
        output.seek(0)
        new_filename = os.path.splitext(filename)[0] + f".{formato_saida.lower()}"
        return new_filename, output

    except Exception as e:
        return f"erro_{filename}", io.BytesIO(str(e).encode())


# PROCESSAMENTO PRINCIPAL
if (modo == "Arquivos individuais" and uploaded_files) or (
    modo == "Pasta compactada (.zip)" and uploaded_zip
):
    converted_files = []

    # Extração se for ZIP
    if modo == "Pasta compactada (.zip)":
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(uploaded_zip, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        all_files = []
        for root, _, files in os.walk(temp_dir):
            for f in files:
                if f.lower().endswith(
                    tuple([".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"])
                ):
                    with open(os.path.join(root, f), "rb") as img_file:
                        all_files.append((img_file.read(), f))
    else:
        all_files = [(f.read(), f.name) for f in uploaded_files]

    st.info(f"Iniciando conversão de {len(all_files)} arquivo(s)...")
    progress_bar = st.progress(0)
    status_text = st.empty()

    # Processamento assíncrono
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda data: process_image(*data), all_files))

        for i, result in enumerate(results):
            converted_files.append(result)
            progress_bar.progress((i + 1) / len(all_files))
            status_text.text(f"Convertendo {i + 1}/{len(all_files)}...")

    progress_bar.empty()
    status_text.text("Conversão concluída com sucesso!")

    # PRÉ-VISUALIZAÇÃO
    with st.expander("Pré-visualizar (mostrando 3 primeiras)"):
        for name, data in converted_files[:3]:
            try:
                st.image(data, caption=name, use_column_width=True)
            except:
                pass
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
    st.warning("Envie arquivos ou uma pasta compactada para iniciar a conversão.")
