# 📊 Indicadores Estratégicos - Treinamento & Desenvolvimento Selbetti

Dashboard interativo desenvolvido em Streamlit para análise de indicadores estratégicos da área de Treinamento e Desenvolvimento da Selbetti.

## 🎯 Objetivos

Este projeto visa:

- Entender indicadores padrões de engajamento dos profissionais
- Elevar metade dos indicadores para um novo patamar
- Observar oportunidades e aplicações práticas dos conteúdos abordados nos treinamentos
- Fornecer visões panorâmicas e focadas (áreas, grupos profissionais e indivíduos)
- Analisar participação em pesquisas e uso de câmera durante encontros

## 🚀 Funcionalidades

### 📈 Panorama Geral

- Visão ampla dos indicadores de engajamento
- Métricas principais: taxa de presença, participação média, taxa de pesquisa, média de câmera aberta
- Análise por curso com gráficos comparativos

### 🏢 Por Área/Diretor

- Análise comparativa entre diferentes diretorias
- Identificação de áreas com maior/menor engajamento
- Análise detalhada por diretor selecionado

### 👤 Por Participante

- Análise individual de cada profissional
- Top performers em participação e presença
- Histórico completo de participação por profissional

### 📅 Evolução Temporal

- Acompanhamento da evolução dos indicadores ao longo do tempo
- Identificação de tendências e padrões

## 🛠️ Tecnologias

- **Streamlit**: Framework para criação da interface web
- **Python**: Linguagem de programação
- **Pandas**: Manipulação e análise de dados
- **Plotly**: Visualizações interativas
- **NumPy**: Operações numéricas

## 📦 Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## 🎨 Design

O projeto utiliza a paleta de cores da Selbetti:

- **Laranja**: `#EF8943`
- **Verde Escuro**: `#17392F`
- **Verde**: `#00754A`
- **Cinza Claro**: `#F1F1F1`
- **Cinza**: `#E0E0E0`
- **Branco**: `#FFFFFF`

## 🚀 Como Executar

Execute o seguinte comando no terminal:

```bash
streamlit run app.py
```

O dashboard será aberto automaticamente no navegador.

## 🔄 Automação de Deploy

O projeto inclui um script PowerShell para automatizar o processo de commit e push para o GitHub.

### Deploy Automático

Para fazer deploy de todos os arquivos no repositório GitHub:

```powershell
cd "c:\Users\italo.lucena\OneDrive\1. IE Consultoria\1. Selbetti\T&D\Indicadores Estratégicos"

# Configurar token
$env:GITHUB_TOKEN = "seu_token_aqui"

# Executar script de deploy
.\DEPLOY_FINAL.ps1
```

O script irá:
- ✅ Criar um histórico Git limpo
- ✅ Adicionar todos os arquivos do projeto
- ✅ Criar commit inicial
- ✅ Fazer push para o repositório `InStudium/dashboardtd` no branch `main`

### Requisitos

- Git instalado e configurado
- Token do GitHub com permissão `repo`
- Acesso de escrita no repositório `InStudium/dashboardtd`

### Obter Token do GitHub

1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token (classic)"
3. Selecione permissão `repo`
4. Copie o token gerado
5. Use o token na variável `$env:GITHUB_TOKEN` antes de executar o script

## 📊 Estrutura de Dados

O projeto utiliza o arquivo `Base_Dados_Cursos.csv` com as seguintes colunas:

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

## 🔮 Funcionalidades Futuras

- Análise de Regressão Linear para relacionar volumes e ementas dos cursos com a performance melhorada dos profissionais
- Machine Learning para previsão de engajamento
- Recomendações personalizadas de treinamentos

## 📝 Notas

- Os dados são carregados com cache para melhor performance
- Filtros disponíveis na sidebar permitem análise segmentada
- Todas as visualizações são interativas e responsivas

## 👥 Desenvolvido para

Área de Treinamento e Desenvolvimento - Selbetti

## 📝 Créditos

Desenvolvido por **Núcleo de Inteligência e T&D - 2025**
