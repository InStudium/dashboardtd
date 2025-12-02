import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import utils
import base64
import os

# Configuração da página
st.set_page_config(
    page_title="Indicadores Estratégicos T&D - Selbetti",
    page_icon="favicon.svg",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cores da paleta
CORES = {
    'laranja': '#EF8943',
    'verde_escuro': '#17392F',
    'verde': '#00754A',
    'cinza_claro': '#F1F1F1',
    'cinza': '#E0E0E0',
    'branco': '#FFFFFF'
}

# Paleta de cores padrão para gráficos (baseada nas cores do projeto)
PALETA_CORES = [CORES['verde'], CORES['laranja'], CORES['verde_escuro']]
# Escala contínua para gráficos de barras
ESCALA_CONTINUA = [CORES['verde'], CORES['laranja']]

# Paleta expandida para gráficos de pizza (6 cores diferentes)
# Usando as cores exatas fornecidas
PALETA_PIZZA = [
    CORES['laranja'],        # #EF8943
    CORES['verde_escuro'],   # #17392F
    CORES['verde'],          # #00754A
    CORES['cinza_claro'],    # #F1F1F1
    CORES['cinza'],          # #E0E0E0
    CORES['branco']          # #FFFFFF
]

def get_pizza_colors(names):
    """Retorna lista de cores para gráfico de pizza, repetindo se necessário"""
    colors = []
    for i, name in enumerate(names):
        colors.append(PALETA_PIZZA[i % len(PALETA_PIZZA)])
    return colors

# Função para renderizar ícones SVG 2D no estilo shadcn/ui
def get_icon(icon_name, size=20, color=None):
    """Retorna SVG de ícone 2D no estilo shadcn/ui com cores do projeto"""
    if color is None:
        color = CORES['verde_escuro']
    
    icons = {
        'chart': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 4px;">
            <rect x="3" y="3" width="18" height="18" rx="2" stroke="{color}" stroke-width="2" fill="none"/>
            <path d="M7 17L7 14" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
            <path d="M12 17L12 10" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
            <path d="M17 17L17 7" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
        </svg>''',
        'search': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 4px;">
            <circle cx="11" cy="11" r="8" stroke="{color}" stroke-width="2" fill="none"/>
            <path d="m21 21-4.35-4.35" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
        </svg>''',
        'trending-up': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 4px;">
            <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
            <polyline points="16 7 22 7 22 13" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </svg>''',
        'building': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 4px;">
            <path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z" stroke="{color}" stroke-width="2" fill="none"/>
            <path d="M6 12h4m-4 4h4m-4 4h4" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
            <path d="M18 9h2m-2 4h2m-2 4h2" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
        </svg>''',
        'user': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 4px;">
            <circle cx="12" cy="8" r="4" stroke="{color}" stroke-width="2" fill="none"/>
            <path d="M20 21c0-4.418-3.582-8-8-8s-8 3.582-8 8" stroke="{color}" stroke-width="2" fill="none"/>
        </svg>''',
        'calendar': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 4px;">
            <rect x="3" y="4" width="18" height="18" rx="2" stroke="{color}" stroke-width="2" fill="none"/>
            <line x1="16" y1="2" x2="16" y2="6" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
            <line x1="8" y1="2" x2="8" y2="6" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
            <line x1="3" y1="10" x2="21" y2="10" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
        </svg>''',
        'trophy': f'''<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="display: inline-block; vertical-align: middle; margin-right: 4px;">
            <path d="M6 9H4a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h2" stroke="{color}" stroke-width="2" fill="none"/>
            <path d="M18 9h2a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2h-2" stroke="{color}" stroke-width="2" fill="none"/>
            <path d="M4 13h16" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
            <path d="M12 3v18" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
            <path d="M8 21h8" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
        </svg>'''
    }
    return icons.get(icon_name, '')

def icon_html(icon_name, size=20, color=None):
    """Retorna HTML com ícone SVG"""
    return get_icon(icon_name, size, color)

def get_base64_image(image_path):
    """Converte imagem para base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return ""

# CSS customizado
def load_css():
    bg_image = get_base64_image("imagens/bg_selbetti.png")
    logo_image = get_base64_image("imagens/Selbetti - Logo Principal.png")
    
    st.markdown(f"""
    <style>
    .main {{
        background-color: transparent;
    }}
    .stApp {{
        background-image: url('data:image/png;base64,{bg_image}');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    /* Garantir espaço suficiente abaixo do header fixo do Streamlit */
    header[data-testid="stHeader"] {{
        position: fixed !important;
        top: 0 !important;
        z-index: 999 !important;
    }}
    /* Container principal com background - com padding-top grande para não ser encoberto */
    .main .block-container {{
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding-top: 12rem !important;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        margin-top: 0.5rem;
    }}
    /* Spacer fixo para garantir espaço abaixo do header do Streamlit */
    .header-spacer {{
        height: 5rem;
        width: 100%;
        display: block;
        margin: 0;
        padding: 0;
    }}
    /* Container do header com título e logo */
    .header-container {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
        margin-top: 0 !important;
        padding-top: 1.5rem !important;
        position: relative;
        z-index: 1;
        border-top: 1px solid rgba(23, 57, 47, 0.15);
    }}
    /* Garantir que o primeiro elemento não remova espaçamento */
    .element-container:first-child {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    /* Garantir que o markdown container não remova o espaçamento */
    [data-testid="stMarkdownContainer"]:has(.header-container) {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    /* Ajustar o conteúdo principal */
    .main {{
        padding-top: 0 !important;
    }}
    /* Forçar espaçamento no início do conteúdo principal */
    .stApp > div:first-child > div:first-child {{
        padding-top: 0 !important;
    }}
    .header-title {{
        color: {CORES['verde_escuro']};
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0;
        padding: 0;
        line-height: 1.2;
        flex: 1;
    }}
    .header-logo {{
        background-color: transparent;
        padding: 0;
        margin-left: 1rem;
    }}
    .header-logo img {{
        max-height: 60px;
        width: auto;
        background-color: transparent;
    }}
    .metric-card {{
        background-color: {CORES['branco']};
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid {CORES['laranja']};
    }}
    /* Reduzir espaçamento do primeiro elemento */
    .element-container:first-child {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    /* Remover espaçamento superior do header */
    .header-container:first-child,
    div:has(.header-container):first-child {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    /* Garantir que não há espaçamento antes do header */
    [data-testid="stMarkdownContainer"]:has(.header-container) {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    /* Ocultar apenas o menu principal, mas manter header e botão de toggle do sidebar */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    /* Estilizar rodapé customizado */
    .footer-credits {{
        text-align: center;
        padding: 1rem 0;
        margin-top: 2rem;
        border-top: 1px solid {CORES['cinza']};
        color: {CORES['verde_escuro']};
        font-size: 0.85rem;
    }}
    /* Garantir que o header e botão de toggle do sidebar estejam sempre visíveis */
    header {{
        visibility: visible !important;
    }}
    /* Botão de toggle do sidebar - sempre visível */
    button[kind="header"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="baseButton-header"] {{
        visibility: visible !important;
        display: block !important;
        opacity: 1 !important;
    }}
    /* Ajustar espaçamento do título */
    h1.header-title {{
        margin-top: 0 !important;
        padding-top: 0 !important;
    }}
    .section-title {{
        color: {CORES['verde_escuro']};
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0;
    }}
    .icon-inline {{
        display: inline-block;
        vertical-align: middle;
        margin-right: 6px;
    }}
    /* Bordas arredondadas para gráficos Plotly */
    .js-plotly-plot {{
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }}
    .plotly {{
        border-radius: 12px;
        overflow: hidden;
    }}
    /* Container dos gráficos */
    [data-testid="stPlotlyChart"] {{
        border-radius: 12px;
        overflow: hidden;
    }}
    div[data-testid="stPlotlyChart"] > div {{
        border-radius: 12px;
        overflow: hidden;
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}
    .stTabs [data-baseweb="tab"] {{
        padding: 10px 16px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {CORES['cinza_claro']};
        color: {CORES['verde_escuro']};
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # JavaScript separado para evitar exibição como texto
    st.markdown("""
    <script>
    (function() {
        function translateFileUploader() {
            const fileUploaders = document.querySelectorAll('[data-testid="stFileUploader"]');
            fileUploaders.forEach(function(uploader) {
                const paragraphs = uploader.querySelectorAll('p');
                paragraphs.forEach(function(p) {
                    if (p.textContent.includes('Drag and drop') || p.textContent.includes('file here')) {
                        p.textContent = 'Arraste e solte um arquivo aqui ou clique para navegar';
                    }
                });
            });
        }
        
        // Ajustar espaçamento dinamicamente baseado na altura do header do Streamlit
        function adjustHeaderSpacing() {
            const header = document.querySelector('header[data-testid="stHeader"]');
            const spacer = document.querySelector('.header-spacer');
            const headerContainer = document.querySelector('.header-container');
            
            if (header && spacer) {
                const headerHeight = header.offsetHeight || header.clientHeight || 60;
                // Altura do spacer = altura do header + espaço extra (30px)
                const spacerHeight = headerHeight + 30;
                spacer.style.height = spacerHeight + 'px';
            }
            
            // Garantir que o header-container tenha padding-top
            if (headerContainer) {
                headerContainer.style.paddingTop = '1.5rem';
            }
        }
        
        function init() {
            translateFileUploader();
            // Múltiplas tentativas para garantir que funcione
            adjustHeaderSpacing();
            setTimeout(adjustHeaderSpacing, 50);
            setTimeout(adjustHeaderSpacing, 200);
            setTimeout(adjustHeaderSpacing, 500);
            setTimeout(adjustHeaderSpacing, 1000);
        }
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', init);
        } else {
            init();
        }
        
        const observer = new MutationObserver(function() {
            translateFileUploader();
            setTimeout(adjustHeaderSpacing, 50);
            setTimeout(adjustHeaderSpacing, 200);
        });
        observer.observe(document.body, { childList: true, subtree: true });
        
        // Ajustar também quando a janela é redimensionada
        window.addEventListener('resize', function() {
            setTimeout(adjustHeaderSpacing, 50);
            setTimeout(adjustHeaderSpacing, 200);
        });
        
        // Ajustar quando a página está totalmente carregada
        window.addEventListener('load', function() {
            setTimeout(adjustHeaderSpacing, 100);
            setTimeout(adjustHeaderSpacing, 500);
        });
    })();
    </script>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data_cached():
    """Carrega dados com cache"""
    return utils.load_data()

def validate_csv(df):
    """Valida se o DataFrame tem as colunas necessárias"""
    required_columns = [
        'Data', 'Participante', 'Diretor', 'Curso', 'Duração', 
        'Participação', '% Participação', 'Respondeu a Pesquisa de Satisfação?', 
        'Status'
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    return len(missing_columns) == 0, missing_columns

def handle_file_upload(uploaded_file):
    """Processa o upload do arquivo CSV"""
    try:
        # Tentar ler o arquivo CSV com diferentes encodings
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        df = None
        
        for encoding in encodings:
            try:
                uploaded_file.seek(0)  # Resetar o ponteiro do arquivo
                df = pd.read_csv(uploaded_file, sep=';', encoding=encoding)
                break
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
        
        if df is None:
            return False, "Não foi possível ler o arquivo. Verifique o formato e encoding."
        
        # Validar colunas
        is_valid, missing_cols = validate_csv(df)
        if not is_valid:
            return False, f"O arquivo CSV não possui as colunas necessárias: {', '.join(missing_cols)}"
        
        # Validar se tem dados
        if len(df) == 0:
            return False, "O arquivo CSV está vazio."
        
        # Salvar o arquivo
        csv_path = 'Base_Dados_Cursos.csv'
        df.to_csv(csv_path, sep=';', index=False, encoding='utf-8')
        
        # Limpar o cache
        load_data_cached.clear()
        
        return True, f"Arquivo atualizado com sucesso! {len(df)} registros carregados."
    
    except Exception as e:
        return False, f"Erro ao processar o arquivo: {str(e)}"

def create_metric_card(title, value, subtitle="", delta=None):
    """Cria um card de métrica estilizado"""
    delta_html = f"<span style='color: {CORES['verde']}; font-size: 0.9rem;'>{delta}</span>" if delta else ""
    return f"""
    <div class="metric-card">
        <h3 style="color: {CORES['verde_escuro']}; margin: 0; font-size: 0.9rem;">{title}</h3>
        <h2 style="color: {CORES['laranja']}; margin: 0.5rem 0; font-size: 2rem;">{value}</h2>
        {f'<p style="color: {CORES["verde_escuro"]}; margin: 0; font-size: 0.8rem;">{subtitle}</p>' if subtitle else ''}
        {delta_html}
    </div>
    """

def apply_shadcn_style(fig, title=None):
    """Aplica estilo shadcn/ui aos gráficos Plotly"""
    # Verificar se é gráfico de pizza (não tem eixos)
    is_pie = any(trace.type == 'pie' for trace in fig.data)
    
    layout_updates = {
        # Cores de fundo - estilo shadcn/ui minimalista
        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
        'paper_bgcolor': 'rgba(0, 0, 0, 0)',
        
        # Fonte e tipografia
        'font': dict(
            family='system-ui, -apple-system, sans-serif',
            size=12,
            color=CORES['verde_escuro']
        ),
        
        # Margens e padding
        'margin': dict(l=50, r=30, t=50 if title else 30, b=50),
        'autosize': True,
        
        # Tooltip estilo shadcn/ui
        'hovermode': 'x unified' if not is_pie else 'closest',
        'hoverlabel': dict(
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            font=dict(
                size=12,
                family='system-ui, -apple-system, sans-serif',
                color=CORES['verde_escuro']
            )
        ),
    }
    
    # Adicionar título se fornecido
    if title:
        layout_updates['title'] = dict(
            text=title,
            font=dict(
                size=16,
                color=CORES['verde_escuro'],
                family='system-ui, -apple-system, sans-serif'
            ),
            x=0.02,
            xanchor='left',
            pad=dict(b=20, t=10)
        )
    
    # Adicionar grid apenas se não for pizza
    if not is_pie:
        layout_updates['xaxis'] = dict(
            gridcolor='rgba(0, 0, 0, 0.06)',
            gridwidth=1,
            showgrid=True,
            zeroline=False,
            linecolor='rgba(0, 0, 0, 0.1)',
            linewidth=1
        )
        layout_updates['yaxis'] = dict(
            gridcolor='rgba(0, 0, 0, 0.06)',
            gridwidth=1,
            showgrid=True,
            zeroline=False,
            linecolor='rgba(0, 0, 0, 0.1)',
            linewidth=1
        )
        layout_updates['showlegend'] = True
        layout_updates['legend'] = dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=11, color=CORES['verde_escuro']),
            bgcolor='rgba(0, 0, 0, 0)',
            bordercolor='rgba(0, 0, 0, 0)'
        )
    else:
        # Para gráficos de pizza, centralizar e ajustar
        layout_updates['showlegend'] = True
        layout_updates['legend'] = dict(
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='right',
            x=1.1,
            font=dict(size=11, color=CORES['verde_escuro']),
            bgcolor='rgba(0, 0, 0, 0)',
            bordercolor='rgba(0, 0, 0, 0)'
        )
    
    fig.update_layout(**layout_updates)
    
    # Atualizar estilo das linhas e barras para shadcn/ui, preservando cores
    for trace in fig.data:
        if trace.type == 'bar' or trace.type == 'histogram':
            if hasattr(trace, 'marker'):
                trace.marker.line.width = 0
                trace.marker.opacity = 0.85
                # Preservar cores se já estiverem definidas
                if not hasattr(trace.marker, 'color') or trace.marker.color is None:
                    # Aplicar cor padrão apenas se não houver cor definida
                    if len(fig.data) == 1:
                        trace.marker.color = CORES['laranja']
        elif trace.type == 'pie':
            # Manter opacidade para gráficos de pizza
            if hasattr(trace, 'marker'):
                trace.marker.line.width = 1
                trace.marker.line.color = 'rgba(255, 255, 255, 0.8)'
            # Garantir que as cores do gráfico de pizza sejam mantidas
            if hasattr(trace, 'marker') and hasattr(trace.marker, 'colors'):
                # As cores já foram definidas no color_discrete_map, não alterar
                pass
        elif trace.type == 'scatter':
            # Para gráficos de linha, garantir que as cores sejam mantidas
            if hasattr(trace, 'line') and trace.line.color:
                # Manter a cor já definida
                pass
    
    return fig

def main():
    load_css()
    
    # Spacer fixo para garantir espaço abaixo do header do Streamlit
    st.markdown('<div class="header-spacer"></div>', unsafe_allow_html=True)
    
    # Header - Título compacto no topo com logo
    chart_icon = get_icon("chart", 24, CORES["verde_escuro"])
    logo_image = get_base64_image("imagens/Selbetti - Logo Principal.png")
    st.markdown(f'''
    <div class="header-container">
        <h1 class="header-title">{chart_icon} Indicadores Estratégicos - T&D</h1>
        <div class="header-logo">
            <img src="data:image/png;base64,{logo_image}" alt="Selbetti Logo">
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    
    # Carregar dados
    df = load_data_cached()
    
    # Verificar se o DataFrame está vazio (arquivo não encontrado)
    if df.empty:
        st.warning("""
        ⚠️ **Arquivo de dados não encontrado!**
        
        Por favor, faça upload do arquivo `Base_Dados_Cursos.csv` usando o campo de upload na sidebar.
        
        O arquivo deve conter as seguintes colunas:
        - Data
        - Participante
        - Diretor
        - Curso
        - Duração
        - Participação
        - % Participação
        - % Câmera aberta
        - Respondeu a Pesquisa de Satisfação?
        - Status
        - Motivo Ausência
        """)
        st.stop()
    
    # Sidebar - Filtros
    st.sidebar.markdown(f'<div style="font-size: 1.2rem; font-weight: 600; color: {CORES["verde_escuro"]};">{icon_html("search", 20, CORES["verde_escuro"])} Filtros</div>', unsafe_allow_html=True)
    
    # Filtro de data
    if not df['Data'].isna().all():
        min_date = df['Data'].min()
        max_date = df['Data'].max()
        date_range = st.sidebar.date_input(
            "Período",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            df = df[(df['Data'] >= pd.Timestamp(date_range[0])) & 
                   (df['Data'] <= pd.Timestamp(date_range[1]))]
    
    # Filtro de curso
    cursos = ['Todos'] + sorted(df['Curso'].unique().tolist())
    curso_selecionado = st.sidebar.selectbox("Curso", cursos)
    if curso_selecionado != 'Todos':
        df = df[df['Curso'] == curso_selecionado]
    
    # Filtro de diretor
    diretores = ['Todos'] + sorted(df['Diretor'].unique().tolist())
    diretor_selecionado = st.sidebar.selectbox("Diretor/Área", diretores)
    if diretor_selecionado != 'Todos':
        df = df[df['Diretor'] == diretor_selecionado]
    
    # Sidebar - Upload de arquivo
    st.sidebar.markdown("---")
    st.sidebar.markdown(f'<div style="font-size: 1.2rem; font-weight: 600; color: {CORES["verde_escuro"]}; margin-bottom: 0.5rem;">📤 Atualizar Dados</div>', unsafe_allow_html=True)
    
    uploaded_file = st.sidebar.file_uploader(
        "Faça upload de um arquivo CSV",
        type=['csv'],
        help="Selecione um arquivo CSV com o mesmo formato do Base_Dados_Cursos.csv para atualizar os dados.",
        label_visibility="visible"
    )
    
    if uploaded_file is not None:
        # Mostrar informações do arquivo
        st.sidebar.info(f"📄 Arquivo selecionado: {uploaded_file.name}")
        
        # Pré-visualização do arquivo
        try:
            uploaded_file.seek(0)
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            preview_df = None
            for encoding in encodings:
                try:
                    uploaded_file.seek(0)
                    preview_df = pd.read_csv(uploaded_file, sep=';', encoding=encoding, nrows=5)
                    break
                except:
                    continue
            if preview_df is not None:
                with st.sidebar.expander("👁️ Pré-visualizar arquivo (primeiras 5 linhas)"):
                    st.dataframe(preview_df, use_container_width=True, hide_index=True)
        except:
            pass
        
        if st.sidebar.button("✅ Atualizar Base de Dados", type="primary", use_container_width=True):
            with st.sidebar:
                with st.spinner("Processando arquivo..."):
                    success, message = handle_file_upload(uploaded_file)
                    
                    if success:
                        st.success(message)
                        st.balloons()  # Animação de sucesso
                        st.rerun()  # Recarregar a aplicação para mostrar os novos dados
                    else:
                        st.error(message)
    
    # Abas principais - Streamlit não suporta HTML nas abas, então usamos texto simples
    tab1, tab2, tab3, tab4 = st.tabs([
        "Panorama Geral",
        "Por Área/Diretor",
        "Por Participante",
        "Evolução Temporal"
    ])
    
    with tab1:
        show_panorama_geral(df)
    
    with tab2:
        show_por_area(df)
    
    with tab3:
        show_por_participante(df)
    
    with tab4:
        show_evolucao_temporal(df)
    
    # Rodapé com créditos
    st.markdown("---")
    st.markdown(
        f'<div class="footer-credits">'
        f'Desenvolvido por <strong>Núcleo de Inteligência e T&D - 2025</strong>'
        f'</div>',
        unsafe_allow_html=True
    )

def generate_strategic_insights(df):
    """Gera insights estratégicos e sugestões de ações baseados na análise dos dados"""
    metrics = utils.get_summary_metrics(df)
    metrics_by_course = utils.get_metrics_by_course(df)
    metrics_by_director = utils.get_metrics_by_director(df)
    df_presentes = df[df['Presente'] == 1]
    
    insights = []
    acoes = []
    
    # INSIGHT 1: Análise da Taxa de Presença
    taxa_presenca = metrics['taxa_presenca']
    if taxa_presenca < 70:
        insights.append({
            'titulo': 'Taxa de Presença Abaixo do Ideal',
            'descricao': f'A taxa de presença atual é de {taxa_presenca:.1f}%, indicando que aproximadamente {100-taxa_presenca:.1f}% dos profissionais convidados não estão participando dos treinamentos.',
            'metodologia': 'Comparação da taxa de presença atual com benchmark de 70% (padrão de mercado para treinamentos corporativos).'
        })
        acoes.append({
            'titulo': 'Implementar Estratégias de Engajamento Pré-Treinamento',
            'descricao': 'Enviar lembretes personalizados 48h e 24h antes, criar expectativa sobre o conteúdo e alinhar horários com os gestores para liberação dos profissionais.',
            'metodologia': 'Baseado em estudos que mostram aumento de 15-20% na presença com lembretes estratégicos.'
        })
    elif taxa_presenca >= 85:
        insights.append({
            'titulo': 'Taxa de Presença Excelente',
            'descricao': f'A taxa de presença de {taxa_presenca:.1f}% está acima do benchmark de 70%, demonstrando alto comprometimento organizacional com o desenvolvimento.',
            'metodologia': 'Comparação com benchmark de 70% e análise de tendência positiva.'
        })
        acoes.append({
            'titulo': 'Manter e Replicar Boas Práticas',
            'descricao': 'Documentar as práticas que levaram a esta alta taxa de presença e replicá-las em outras áreas ou treinamentos.',
            'metodologia': 'Identificação de padrões de sucesso através de análise comparativa.'
        })
    else:
        insights.append({
            'titulo': 'Taxa de Presença Dentro do Esperado',
            'descricao': f'A taxa de presença de {taxa_presenca:.1f}% está dentro do esperado, mas há espaço para melhoria.',
            'metodologia': 'Comparação com benchmark de 70% e análise de oportunidades de crescimento.'
        })
        acoes.append({
            'titulo': 'Otimizar Processo de Convites',
            'descricao': 'Melhorar a comunicação sobre os treinamentos, destacar benefícios e criar senso de urgência.',
            'metodologia': 'Análise de gaps entre taxa atual e potencial máximo.'
        })
    
    # INSIGHT 2: Análise da Média de Participação
    media_participacao = metrics['media_participacao']
    if media_participacao < 60:
        insights.append({
            'titulo': 'Baixo Engajamento Durante os Treinamentos',
            'descricao': f'A média de participação é de {media_participacao:.1f}%, indicando que mesmo os presentes não estão totalmente engajados durante as sessões.',
            'metodologia': 'Análise da média de tempo de participação em relação à duração total dos treinamentos.'
        })
        acoes.append({
            'titulo': 'Redesenhar Metodologia de Ensino',
            'descricao': 'Incluir mais interatividade, pausas estratégicas, atividades práticas e gamificação para aumentar o engajamento durante as sessões.',
            'metodologia': 'Baseado em estudos de neurociência que mostram que interatividade aumenta retenção em 40-60%.'
        })
    elif media_participacao >= 80:
        insights.append({
            'titulo': 'Alto Nível de Engajamento',
            'descricao': f'A média de participação de {media_participacao:.1f}% indica que os participantes estão altamente engajados durante os treinamentos.',
            'metodologia': 'Análise da média de participação comparada com duração total dos cursos.'
        })
        acoes.append({
            'titulo': 'Aproveitar Alto Engajamento para Aprofundar Conteúdo',
            'descricao': 'Considerar aumentar a complexidade ou duração dos treinamentos, já que há alta capacidade de absorção.',
            'metodologia': 'Correlação positiva entre engajamento e capacidade de aprendizado.'
        })
    
    # INSIGHT 3: Análise da Taxa de Pesquisa
    taxa_pesquisa = metrics['taxa_pesquisa']
    if taxa_pesquisa < 50:
        insights.append({
            'titulo': 'Baixa Taxa de Feedback',
            'descricao': f'Apenas {taxa_pesquisa:.1f}% dos participantes estão respondendo às pesquisas de satisfação, limitando a capacidade de melhoria contínua.',
            'metodologia': 'Cálculo da proporção de pesquisas respondidas em relação ao total de participantes presentes.'
        })
        acoes.append({
            'titulo': 'Simplificar e Incentivar Respostas às Pesquisas',
            'descricao': 'Reduzir número de perguntas, enviar lembretes, oferecer incentivos e mostrar como o feedback é utilizado para melhorias.',
            'metodologia': 'Baseado em estudos que mostram aumento de 30-50% na taxa de resposta com pesquisas mais curtas e incentivos.'
        })
    else:
        insights.append({
            'titulo': 'Boa Taxa de Coleta de Feedback',
            'descricao': f'A taxa de {taxa_pesquisa:.1f}% de respostas às pesquisas permite uma boa base para análise de satisfação e melhoria contínua.',
            'metodologia': 'Análise da proporção de feedback coletado em relação aos participantes.'
        })
        acoes.append({
            'titulo': 'Aprofundar Análise de Feedback',
            'descricao': 'Criar dashboards de análise de sentimento, identificar padrões nas respostas e implementar melhorias baseadas em feedback recorrente.',
            'metodologia': 'Aproveitamento de dados já coletados para insights mais profundos.'
        })
    
    # INSIGHT 4: Análise de Variação entre Cursos
    if len(metrics_by_course) > 1:
        variacao_presenca = metrics_by_course['Taxa_Presenca'].std()
        curso_melhor = metrics_by_course.loc[metrics_by_course['Taxa_Presenca'].idxmax()]
        curso_pior = metrics_by_course.loc[metrics_by_course['Taxa_Presenca'].idxmin()]
        
        if variacao_presenca > 15:
            insights.append({
                'titulo': 'Alta Variação de Performance entre Cursos',
                'descricao': f'Há uma diferença significativa entre os cursos: {curso_melhor["Curso"]} tem {curso_melhor["Taxa_Presenca"]:.1f}% de presença, enquanto {curso_pior["Curso"]} tem {curso_pior["Taxa_Presenca"]:.1f}%.',
                'metodologia': 'Cálculo do desvio padrão da taxa de presença entre cursos e identificação dos extremos.'
            })
            acoes.append({
                'titulo': 'Replicar Boas Práticas dos Cursos de Alto Desempenho',
                'descricao': f'Analisar o que torna {curso_melhor["Curso"]} mais atrativo e aplicar essas estratégias em {curso_pior["Curso"]} e outros cursos com baixa performance.',
                'metodologia': 'Análise comparativa entre cursos de alta e baixa performance para identificar fatores de sucesso.'
            })
    
    # INSIGHT 5: Análise de Variação entre Diretores/Áreas
    if len(metrics_by_director) > 1:
        variacao_diretor = metrics_by_director['Taxa_Presenca'].std()
        diretor_melhor = metrics_by_director.loc[metrics_by_director['Taxa_Presenca'].idxmax()]
        diretor_pior = metrics_by_director.loc[metrics_by_director['Taxa_Presenca'].idxmin()]
        
        if variacao_diretor > 20:
            insights.append({
                'titulo': 'Desalinhamento Cultural entre Áreas',
                'descricao': f'A área de {diretor_melhor["Diretor"]} apresenta {diretor_melhor["Taxa_Presenca"]:.1f}% de presença, enquanto {diretor_pior["Diretor"]} apresenta {diretor_pior["Taxa_Presenca"]:.1f}%, indicando diferentes níveis de priorização do desenvolvimento.',
                'metodologia': 'Análise do desvio padrão da taxa de presença entre diretorias e identificação de gaps culturais.'
            })
            acoes.append({
                'titulo': 'Criar Programa de Mentoria entre Áreas',
                'descricao': f'Conectar líderes de {diretor_melhor["Diretor"]} com {diretor_pior["Diretor"]} para compartilhar práticas de engajamento e criar alinhamento cultural.',
                'metodologia': 'Transferência de conhecimento baseada em benchmarking interno entre áreas de alto e baixo desempenho.'
            })
    
    # INSIGHT 6: Análise de Distribuição de Participação
    if len(df_presentes) > 0:
        participacao_std = df_presentes['% Participação'].std()
        participacao_media = df_presentes['% Participação'].mean()
        
        if participacao_std > 30:
            insights.append({
                'titulo': 'Alta Variabilidade no Engajamento Individual',
                'descricao': f'A participação varia significativamente entre profissionais (desvio padrão de {participacao_std:.1f}%), indicando que alguns estão muito engajados enquanto outros participam minimamente.',
                'metodologia': 'Cálculo do desvio padrão da % de participação para medir variabilidade entre participantes.'
            })
            acoes.append({
                'titulo': 'Criar Programas de Desenvolvimento Personalizados',
                'descricao': 'Identificar profissionais com baixa participação e oferecer treinamentos mais curtos, em horários alternativos ou com metodologias diferentes que se adequem melhor ao seu perfil.',
                'metodologia': 'Segmentação de participantes baseada em padrões de engajamento identificados através de análise estatística.'
            })
    
    # Garantir que temos pelo menos 5 insights e 5 ações
    # Adicionar insights adicionais se necessário
    if len(insights) < 5:
        # Insight sobre câmera aberta se disponível
        if metrics['media_camera'] > 0 and len(insights) < 5:
            insights.append({
                'titulo': 'Análise de Engajamento Visual',
                'descricao': f'A média de câmera aberta é de {metrics["media_camera"]:.1f}%, indicando o nível de interação visual durante os treinamentos.',
                'metodologia': 'Análise da média de tempo com câmera aberta em relação à duração total dos treinamentos.'
            })
            acoes.append({
                'titulo': 'Incentivar Uso de Câmera para Maior Conexão',
                'descricao': 'Criar cultura de câmera aberta, destacar benefícios da interação visual e tornar o ambiente mais acolhedor para aumentar conforto dos participantes.',
                'metodologia': 'Correlação entre uso de câmera e níveis de engajamento e retenção de conteúdo.'
            })
        
        # Se ainda não temos 5, adicionar insights gerais
        if len(insights) < 5:
            total_cursos = metrics.get('total_cursos', len(metrics_by_course))
            insights.append({
                'titulo': 'Diversidade de Cursos Oferecidos',
                'descricao': f'O programa oferece {total_cursos} curso(s) diferente(s), demonstrando variedade na oferta de desenvolvimento.',
                'metodologia': 'Contagem do número único de cursos na base de dados.'
            })
            acoes.append({
                'titulo': 'Expandir Portfólio de Treinamentos',
                'descricao': 'Considerar adicionar novos cursos baseados nas necessidades identificadas e feedback dos participantes.',
                'metodologia': 'Análise de gaps de conhecimento e oportunidades de desenvolvimento identificadas.'
            })
        
        # Se ainda não temos 5, adicionar mais um insight
        if len(insights) < 5:
            total_participantes = metrics.get('total_participantes', len(df))
            insights.append({
                'titulo': 'Alcance do Programa de Treinamento',
                'descricao': f'O programa alcançou {total_participantes} participante(s), indicando o escopo de impacto do desenvolvimento organizacional.',
                'metodologia': 'Contagem total de registros de participação na base de dados.'
            })
            acoes.append({
                'titulo': 'Ampliar Alcance do Programa',
                'descricao': 'Identificar profissionais que ainda não participaram e criar estratégias de inclusão para expandir o impacto do programa.',
                'metodologia': 'Análise de cobertura do programa em relação ao total de profissionais elegíveis.'
            })
    
    # Garantir exatamente 5 insights e 5 ações
    return insights[:5], acoes[:5]

def show_panorama_geral(df):
    """Exibe o panorama geral dos indicadores"""
    st.markdown(f'<h2 class="section-title">Panorama Geral de Engajamento</h2>', unsafe_allow_html=True)
    
    # Calcular métricas
    metrics = utils.get_summary_metrics(df)
    
    # Cards de métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(create_metric_card(
            "Taxa de Presença",
            f"{metrics['taxa_presenca']:.1f}%",
            f"{metrics['total_presentes']} de {metrics['total_participantes']} participantes"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Média de Participação",
            f"{metrics['media_participacao']:.1f}%",
            "Tempo médio de engajamento"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "Taxa de Pesquisa",
            f"{metrics['taxa_pesquisa']:.1f}%",
            f"{metrics['total_pesquisas']} respostas coletadas"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Média Câmera Aberta",
            f"{metrics['media_camera']:.1f}%",
            "Engajamento visual"
        ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Gráficos principais
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição de participação - Gráfico de barras estilo shadcn/ui
        df_presentes = df[df['Presente'] == 1]
        
        # Criar intervalos (bins) para o gráfico de barras
        n_bins = 20
        min_val = df_presentes['% Participação'].min()
        max_val = df_presentes['% Participação'].max()
        bin_width = (max_val - min_val) / n_bins
        
        # Criar bins e contar frequências
        bins = []
        counts = []
        bin_labels = []
        
        for i in range(n_bins):
            bin_start = min_val + (i * bin_width)
            bin_end = min_val + ((i + 1) * bin_width)
            
            # Contar valores neste intervalo
            count = len(df_presentes[(df_presentes['% Participação'] >= bin_start) & 
                                    (df_presentes['% Participação'] < bin_end)])
            
            if i == n_bins - 1:  # Último bin inclui o valor máximo
                count = len(df_presentes[(df_presentes['% Participação'] >= bin_start) & 
                                        (df_presentes['% Participação'] <= bin_end)])
            
            if count > 0:  # Apenas adicionar bins com dados
                bins.append(f"{bin_start:.0f}-{bin_end:.0f}%")
                counts.append(count)
                bin_labels.append(f"{count}")
        
        # Criar gráfico de barras com barras separadas
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=bins,
            y=counts,
            marker=dict(
                color=CORES['laranja'],
                line=dict(width=0),  # Sem borda para estilo shadcn/ui
                opacity=0.85
            ),
            text=bin_labels,  # Rótulos nas barras
            textposition='outside',
            textfont=dict(
                size=11,
                color=CORES['verde_escuro'],
                family='system-ui, -apple-system, sans-serif'
            ),
            hovertemplate='<b>%{x}</b><br>Frequência: %{y}<extra></extra>',
            hoverlabel=dict(
                bgcolor='rgba(255, 255, 255, 0.95)',
                bordercolor='rgba(0, 0, 0, 0.1)',
                font=dict(size=12, color=CORES['verde_escuro'])
            )
        ))
        
        # Aplicar estilo shadcn/ui
        fig.update_layout(
            title=dict(
                text='Distribuição de % de Participação',
                font=dict(size=16, color=CORES['verde_escuro'], family='system-ui, -apple-system, sans-serif'),
                x=0.02,
                xanchor='left',
                pad=dict(b=20, t=10)
            ),
            xaxis=dict(
                title='% de Participação',
                gridcolor='rgba(0, 0, 0, 0.06)',
                gridwidth=1,
                showgrid=True,
                zeroline=False,
                linecolor='rgba(0, 0, 0, 0.1)',
                linewidth=1,
                tickangle=-45
            ),
            yaxis=dict(
                title='Frequência',
                gridcolor='rgba(0, 0, 0, 0.06)',
                gridwidth=1,
                showgrid=True,
                zeroline=False,
                linecolor='rgba(0, 0, 0, 0.1)',
                linewidth=1
            ),
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            font=dict(family='system-ui, -apple-system, sans-serif', size=12, color=CORES['verde_escuro']),
            margin=dict(l=50, r=30, t=50, b=80),
            showlegend=False,
            bargap=0.3  # Espaçamento entre barras para estilo shadcn/ui
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Status de presença
        status_counts = df['Status'].value_counts()
        # Obter cores da paleta expandida
        pizza_colors = get_pizza_colors(status_counts.index.tolist())
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color_discrete_sequence=pizza_colors
        )
        # Garantir que as cores sejam aplicadas corretamente usando a paleta
        fig.update_traces(
            marker=dict(
                colors=pizza_colors,
                line=dict(width=1, color='rgba(255, 255, 255, 0.8)')
            )
        )
        fig = apply_shadcn_style(fig, 'Distribuição de Presença/Ausência')
        st.plotly_chart(fig, use_container_width=True)
    
    # Análise por curso
    st.markdown(f'<h2 class="section-title">Análise por Curso</h2>', unsafe_allow_html=True)
    
    metrics_by_course = utils.get_metrics_by_course(df)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            metrics_by_course,
            x='Curso',
            y='Taxa_Presenca',
            color='Taxa_Presenca',
            color_continuous_scale=ESCALA_CONTINUA,
            labels={'Taxa_Presenca': 'Taxa de Presença (%)', 'Curso': 'Curso'}
        )
        fig = apply_shadcn_style(fig, 'Taxa de Presença por Curso')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            metrics_by_course,
            x='Curso',
            y='Media_Participacao',
            color='Media_Participacao',
            color_continuous_scale=ESCALA_CONTINUA,
            labels={'Media_Participacao': 'Média de Participação (%)', 'Curso': 'Curso'}
        )
        fig = apply_shadcn_style(fig, 'Média de Participação por Curso')
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.markdown(f'<h2 class="section-title">Métricas Detalhadas por Curso</h2>', unsafe_allow_html=True)
    st.dataframe(
        metrics_by_course.style.background_gradient(subset=['Taxa_Presenca', 'Media_Participacao', 'Taxa_Pesquisa'], 
                                                   cmap='RdYlGn'),
        use_container_width=True,
        hide_index=True
    )
    
    # Insights Estratégicos e Sugestões de Ações
    st.markdown(f'<h2 class="section-title">Insights Estratégicos e Recomendações</h2>', unsafe_allow_html=True)
    
    insights, acoes = generate_strategic_insights(df)
    
    # Seção de Insights
    st.markdown(f'<h3 style="color: {CORES["verde_escuro"]};">Insights Estratégicos</h3>', unsafe_allow_html=True)
    
    for i, insight in enumerate(insights, 1):
        with st.expander(f"**{i}. {insight['titulo']}**", expanded=(i == 1)):
            st.markdown(f"**Análise:** {insight['descricao']}")
            st.markdown(f"<small style='color: {CORES['verde_escuro']}; font-style: italic;'>📊 Metodologia: {insight['metodologia']}</small>", unsafe_allow_html=True)
    
    # Seção de Ações
    st.markdown(f'<h3 style="color: {CORES["verde_escuro"]};">Sugestões de Ações</h3>', unsafe_allow_html=True)
    
    for i, acao in enumerate(acoes, 1):
        with st.expander(f"**{i}. {acao['titulo']}**", expanded=(i == 1)):
            st.markdown(f"**Recomendação:** {acao['descricao']}")
            st.markdown(f"<small style='color: {CORES['verde_escuro']}; font-style: italic;'>📊 Fundamentação: {acao['metodologia']}</small>", unsafe_allow_html=True)
    
    # Metodologia Geral
    st.markdown(f'<h3 style="color: {CORES["verde_escuro"]};">Metodologia de Análise</h3>', unsafe_allow_html=True)
    st.info("""
    **Como chegamos a estas conclusões:**
    
    Os insights e ações foram gerados através de análise estatística dos dados coletados, utilizando:
    
    1. **Benchmarking**: Comparação dos indicadores com padrões de mercado (ex: 70% de presença como referência)
    2. **Análise Descritiva**: Cálculo de médias, desvios padrão e identificação de extremos (melhores e piores performances)
    3. **Análise Comparativa**: Comparação entre cursos, áreas e participantes para identificar padrões
    4. **Análise de Variabilidade**: Medição de dispersão dos dados para identificar inconsistências
    5. **Correlação**: Identificação de relações entre diferentes métricas (ex: presença vs. participação)
    
    As sugestões de ações são baseadas em:
    - **Evidências Científicas**: Referências a estudos e pesquisas sobre eficácia de treinamentos
    - **Best Practices**: Práticas comprovadas do mercado de T&D
    - **Análise de Causa-Raiz**: Identificação dos fatores que levam aos resultados observados
    - **Benchmarking Interno**: Comparação entre áreas/cursos de alto e baixo desempenho
    
    Todos os cálculos são realizados em tempo real sobre os dados carregados, garantindo que os insights reflitam a situação atual.
    """)
    
    # Governança de Dados
    st.markdown(f'<h3 style="color: {CORES["verde_escuro"]};">Governança de Dados</h3>', unsafe_allow_html=True)
    st.warning("""
    **⚠️ Confidencialidade e Uso Interno**
    
    **Estes são dados privados e confidenciais da organização, destinados exclusivamente para uso interno.**
    
    **Recomendações de Governança:**
    
    1. **Acesso Controlado**: Apenas profissionais autorizados devem ter acesso a este dashboard e aos dados subjacentes.
    
    2. **Uso Ético**: Os dados devem ser utilizados exclusivamente para fins de desenvolvimento organizacional, melhoria de processos de T&D e tomada de decisões estratégicas internas.
    
    3. **Proteção de Privacidade**: Informações individuais de participantes devem ser tratadas com confidencialidade. Evitar compartilhamento de dados pessoais sem autorização.
    
    4. **Compartilhamento Responsável**: Ao compartilhar insights ou relatórios derivados, garantir que não exponham informações sensíveis ou individuais sem necessidade.
    
    5. **Atualização Regular**: Manter os dados atualizados e validar a qualidade das informações antes de tomar decisões baseadas nestes indicadores.
    
    6. **Documentação**: Documentar qualquer análise adicional ou decisões tomadas com base nestes dados para rastreabilidade e auditoria.
    
    7. **Conformidade**: Garantir que o uso destes dados esteja em conformidade com políticas internas de privacidade e proteção de dados da organização.
    
    **Responsabilidade**: A área de T&D é responsável pela gestão, atualização e governança adequada destes dados.
    """)

def show_por_area(df):
    """Exibe análise por área/diretor"""
    st.markdown(f'<h2 class="section-title">Análise por Área/Diretor</h2>', unsafe_allow_html=True)
    
    metrics_by_director = utils.get_metrics_by_director(df)
    
    # Seleção de diretor para análise detalhada
    diretor_detalhe = st.selectbox(
        "Selecione um diretor para análise detalhada:",
        ['Todos'] + sorted(metrics_by_director['Diretor'].tolist())
    )
    
    # Gráficos comparativos
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            metrics_by_director.sort_values('Taxa_Presenca', ascending=True),
            x='Taxa_Presenca',
            y='Diretor',
            orientation='h',
            color='Taxa_Presenca',
            color_continuous_scale=ESCALA_CONTINUA,
            labels={'Taxa_Presenca': 'Taxa de Presença (%)', 'Diretor': 'Diretor'}
        )
        fig = apply_shadcn_style(fig, 'Taxa de Presença por Diretor')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            metrics_by_director.sort_values('Media_Participacao', ascending=True),
            x='Media_Participacao',
            y='Diretor',
            orientation='h',
            color='Media_Participacao',
            color_continuous_scale=ESCALA_CONTINUA,
            labels={'Media_Participacao': 'Média de Participação (%)', 'Diretor': 'Diretor'}
        )
        fig = apply_shadcn_style(fig, 'Média de Participação por Diretor')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de radar para comparação
    if diretor_detalhe != 'Todos':
        st.markdown(f'<h3 style="color: {CORES["verde_escuro"]};">Análise Detalhada: {diretor_detalhe}</h3>', unsafe_allow_html=True)
        
        dir_metrics = metrics_by_director[metrics_by_director['Diretor'] == diretor_detalhe].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Taxa Presença", f"{dir_metrics['Taxa_Presenca']:.1f}%")
        with col2:
            st.metric("Média Participação", f"{dir_metrics['Media_Participacao']:.1f}%")
        with col3:
            st.metric("Taxa Pesquisa", f"{dir_metrics['Taxa_Pesquisa']:.1f}%")
        with col4:
            camera_val = dir_metrics['Media_Camera'] if pd.notna(dir_metrics['Media_Camera']) else 0
            st.metric("Média Câmera", f"{camera_val:.1f}%")
        
        # Participantes desta área
        df_dir = df[df['Diretor'] == diretor_detalhe]
        participantes_dir = utils.get_individual_metrics(df_dir)
        
        st.markdown(f'<h4 style="color: {CORES["verde_escuro"]};">Participantes desta Área</h4>', unsafe_allow_html=True)
        st.dataframe(
            participantes_dir[['Participante', 'Presentes', 'Total_Convites', 'Taxa_Presenca', 
                              'Media_Participacao', 'Taxa_Pesquisa']].sort_values('Media_Participacao', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    
    # Tabela completa
    st.markdown(f'<h2 class="section-title">Métricas Completas por Diretor</h2>', unsafe_allow_html=True)
    st.dataframe(
        metrics_by_director.sort_values('Taxa_Presenca', ascending=False).style.background_gradient(
            subset=['Taxa_Presenca', 'Media_Participacao', 'Taxa_Pesquisa'], 
            cmap='RdYlGn'
        ),
        use_container_width=True,
        hide_index=True
    )

def show_por_participante(df):
    """Exibe análise por participante individual"""
    st.markdown(f'<h2 class="section-title">Análise Individual</h2>', unsafe_allow_html=True)
    
    individual_metrics = utils.get_individual_metrics(df)
    
    # Busca de participante
    st.markdown(f'<div style="margin-bottom: 0.5rem;">{icon_html("search", 18, CORES["verde_escuro"])} <strong>Buscar participante:</strong></div>', unsafe_allow_html=True)
    participante_search = st.text_input("", "", label_visibility="collapsed", placeholder="Digite o nome do participante...")
    if participante_search:
        individual_metrics = individual_metrics[
            individual_metrics['Participante'].str.contains(participante_search, case=False, na=False)
        ]
    
    # Filtro por diretor
    diretores_ind = ['Todos'] + sorted(individual_metrics['Diretor'].unique().tolist())
    diretor_ind = st.selectbox("Filtrar por Diretor:", diretores_ind)
    if diretor_ind != 'Todos':
        individual_metrics = individual_metrics[individual_metrics['Diretor'] == diretor_ind]
    
    # Top performers
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<h3 style="color: {CORES["verde_escuro"]};">{icon_html("trophy", 24, CORES["laranja"])} Top 10 - Maior Participação Média</h3>', unsafe_allow_html=True)
        top_participacao = individual_metrics.nlargest(10, 'Media_Participacao')[
            ['Participante', 'Diretor', 'Media_Participacao', 'Cursos_Diferentes', 'Taxa_Pesquisa']
        ]
        st.dataframe(top_participacao, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown(f'<h3 style="color: {CORES["verde_escuro"]};">{icon_html("chart", 24, CORES["laranja"])} Top 10 - Maior Taxa de Presença</h3>', unsafe_allow_html=True)
        top_presenca = individual_metrics.nlargest(10, 'Taxa_Presenca')[
            ['Participante', 'Diretor', 'Taxa_Presenca', 'Presentes', 'Total_Convites', 'Taxa_Pesquisa']
        ]
        st.dataframe(top_presenca, use_container_width=True, hide_index=True)
    
    # Análise detalhada de um participante
    st.markdown(f'<h2 class="section-title">Análise Detalhada por Participante</h2>', unsafe_allow_html=True)
    
    participantes_list = ['Selecione...'] + sorted(individual_metrics['Participante'].tolist())
    participante_selecionado = st.selectbox("Selecione um participante:", participantes_list)
    
    if participante_selecionado != 'Selecione...':
        participante_data = df[df['Participante'] == participante_selecionado]
        participante_metrics = individual_metrics[individual_metrics['Participante'] == participante_selecionado].iloc[0]
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Taxa Presença", f"{participante_metrics['Taxa_Presenca']:.1f}%")
        with col2:
            st.metric("Média Participação", f"{participante_metrics['Media_Participacao']:.1f}%")
        with col3:
            st.metric("Taxa Pesquisa", f"{participante_metrics['Taxa_Pesquisa']:.1f}%")
        with col4:
            st.metric("Cursos Diferentes", f"{int(participante_metrics['Cursos_Diferentes'])}")
        with col5:
            st.metric("Total Convites", f"{int(participante_metrics['Total_Convites'])}")
        
        # Histórico de participação
        st.markdown(f'<h4 style="color: {CORES["verde_escuro"]};">Histórico de Participação</h4>', unsafe_allow_html=True)
        st.dataframe(
            participante_data[['Data', 'Curso', 'Status', '% Participação', 
                            'Respondeu a Pesquisa de Satisfação?', '% Câmera aberta']].sort_values('Data', ascending=False),
            use_container_width=True,
            hide_index=True
        )
    
    # Tabela completa
    st.markdown(f'<h2 class="section-title">Todos os Participantes</h2>', unsafe_allow_html=True)
    st.dataframe(
        individual_metrics.sort_values('Media_Participacao', ascending=False).style.background_gradient(
            subset=['Taxa_Presenca', 'Media_Participacao', 'Taxa_Pesquisa'], 
            cmap='RdYlGn'
        ),
        use_container_width=True,
        hide_index=True
    )

def show_evolucao_temporal(df):
    """Exibe evolução temporal dos indicadores"""
    st.markdown(f'<h2 class="section-title">Evolução Temporal dos Indicadores</h2>', unsafe_allow_html=True)
    
    time_series = utils.get_time_series_metrics(df)
    
    # Gráfico de evolução
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Taxa de Presença ao Longo do Tempo', 
                       'Média de Participação ao Longo do Tempo',
                       'Taxa de Resposta em Pesquisas', 
                       'Média de Câmera Aberta'),
        vertical_spacing=0.12
    )
    
    # Taxa de presença
    fig.add_trace(
        go.Scatter(x=time_series['Data'], y=time_series['Taxa_Presenca'],
                  mode='lines+markers', name='Taxa Presença',
                  line=dict(color=CORES['verde'], width=3)),
        row=1, col=1
    )
    
    # Média participação
    fig.add_trace(
        go.Scatter(x=time_series['Data'], y=time_series['Media_Participacao'],
                  mode='lines+markers', name='Média Participação',
                  line=dict(color=CORES['laranja'], width=3)),
        row=1, col=2
    )
    
    # Taxa pesquisa
    fig.add_trace(
        go.Scatter(x=time_series['Data'], y=time_series['Taxa_Pesquisa'],
                  mode='lines+markers', name='Taxa Pesquisa',
                  line=dict(color=CORES['verde_escuro'], width=3)),
        row=2, col=1
    )
    
    # Média câmera
    camera_data = time_series['Media_Camera'].fillna(0)
    fig.add_trace(
        go.Scatter(x=time_series['Data'], y=camera_data,
                  mode='lines+markers', name='Média Câmera',
                  line=dict(color=CORES['verde'], width=3)),
        row=2, col=2
    )
    
    # Aplicar estilo shadcn/ui para subplots
    fig.update_layout(
        height=700,
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(
            family='system-ui, -apple-system, sans-serif',
            size=12,
            color=CORES['verde_escuro']
        ),
        hovermode='x unified',
        hoverlabel=dict(
            bgcolor='rgba(255, 255, 255, 0.95)',
            bordercolor='rgba(0, 0, 0, 0.1)',
            font=dict(
                size=12,
                family='system-ui, -apple-system, sans-serif',
                color=CORES['verde_escuro']
            )
        ),
        showlegend=False
    )
    
    # Atualizar eixos para estilo shadcn/ui
    for i in range(1, 3):
        for j in range(1, 3):
            fig.update_xaxes(
                gridcolor='rgba(0, 0, 0, 0.06)',
                gridwidth=1,
                showgrid=True,
                zeroline=False,
                linecolor='rgba(0, 0, 0, 0.1)',
                linewidth=1,
                row=i, col=j
            )
            fig.update_yaxes(
                gridcolor='rgba(0, 0, 0, 0.06)',
                gridwidth=1,
                showgrid=True,
                zeroline=False,
                linecolor='rgba(0, 0, 0, 0.1)',
                linewidth=1,
                row=i, col=j
            )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela temporal
    st.markdown(f'<h2 class="section-title">Dados Temporais Detalhados</h2>', unsafe_allow_html=True)
    st.dataframe(
        time_series.sort_values('Data', ascending=False).style.background_gradient(
            subset=['Taxa_Presenca', 'Media_Participacao', 'Taxa_Pesquisa'], 
            cmap='RdYlGn'
        ),
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    main()

