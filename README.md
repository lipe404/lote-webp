# Conversor Universal de Imagens em Lote (Streamlit)

Aplicação web em Streamlit para conversão em lote de imagens entre diversos formatos, com redimensionamento opcional, compressão adaptativa, preservação de perfil ICC e tratamento correto de transparência. Suporta envio de arquivos individuais ou uma pasta compactada (`.zip`) e oferece pré-visualização e download consolidado dos resultados em um único arquivo ZIP.

## Recursos

- Conversão entre `JPG`, `JPEG`, `PNG`, `WEBP`, `BMP`, `TIFF`.
- Upload de arquivos individuais do formato escolhido ou um `.zip` com subpastas.
- Redimensionamento por largura/altura máximas, mantendo proporção.
- Compressão adaptativa baseada no tamanho original do arquivo.
- Preservação de perfil ICC quando presente.
- Tratamento de transparência: composição automática em fundo branco para `JPEG`; preservação de alfa para `PNG/WEBP/TIFF`.
- Execução paralela (thread pool) para acelerar lotes.
- Pré-visualização das 3 primeiras imagens convertidas.
- Download dos resultados em um único `.zip`.

## Estrutura

- `app.py`: aplicação Streamlit completa, interface, processamento e download.
- `requirements.txt`: dependências Python.

Pontos principais do fluxo:
- Interface e configurações: `app.py:10–71`.
- Função de conversão e salvamento: `app.py:75–161`.
- Processamento em lote, barra de progresso e pré-visualização: `app.py:167–215`.
- Geração e disponibilização do ZIP final: `app.py:217–230`.

## Requisitos

- Python 3.10+ (versões mais novas também funcionam).
- Dependências do arquivo `requirements.txt`.

Instalação rápida:

```bash
python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Execução

```bash
streamlit run app.py
```

Após iniciar, acesse a URL local informada pelo Streamlit (ex.: `http://localhost:8501`).

## Uso

- Selecione o formato de entrada e o formato de saída.
- Escolha o modo: arquivos individuais ou pasta compactada (`.zip`).
- Ajuste as configurações:
  - `Largura máxima` e `Altura máxima` (0 mantém o tamanho original).
  - `Compressão adaptativa` (qualidade varia conforme o tamanho original).
  - `Qualidade base` (para `JPG/JPEG/WEBP`).
- Envie os arquivos ou o `.zip`.
- Acompanhe o progresso e visualize as primeiras imagens convertidas.
- Baixe o resultado em um arquivo `.zip`.

## Formatos suportados

Entrada e saída: `JPG`, `JPEG`, `PNG`, `WEBP`, `BMP`, `TIFF`.

Observações:
- No modo arquivos individuais, a seleção restringe por extensão do formato de entrada escolhido.
- No modo `.zip`, todos os formatos suportados dentro do pacote serão processados.

## Notas técnicas

- Redimensionamento com `Image.thumbnail(..., resample=Image.LANCZOS)` para qualidade superior.
- Preservação de `icc_profile` durante o `save` quando disponível.
- `JPEG`: `subsampling=0`, `optimize=True` e qualidade ajustável.
- `PNG`: `optimize=True` (lossless).
- `WEBP`: `method=6`, `exact=True` e `alpha_quality=100` quando há canal alfa; qualidade ajustável.
- Execução paralela via `ThreadPoolExecutor` para lotes.

## Limitações e considerações

- A detecção do formato baseia-se em extensão; arquivos renomeados incorretamente podem falhar.
- Metadados EXIF (como rotação) não são ajustados automaticamente.
- O zip é gerado em memória; lotes muito grandes podem exigir muita RAM.
- Em caso de erro ao converter um arquivo, o ZIP conterá um arquivo `erro_<nome>` com a mensagem.

## Roadmap sugerido

- Detectar formato por conteúdo (magic numbers) em vez de extensão.
- Ajustar orientação via EXIF quando presente.
- Opções avançadas de compressão (`progressive JPEG`, `PNG compress_level`, `TIFF LZW/Deflate`).
- Métricas de tamanho antes/depois e relatório de ganhos.
- Limites e validações de ZIP (tamanho total, número de arquivos, proteção contra path traversal).
- Opção de processamento em streaming para reduzir uso de memória.
- Testes automatizados com amostras pequenas.
- Internacionalização (i18n) e configurações persistentes.

## Licença

Não especificada. Adicione uma licença se desejar abrir o código.

## Contribuição

Issues e PRs são bem-vindos. Sugestões detalhadas estão em `analise.md`.

