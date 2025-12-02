import pandas as pd
import os
from pathlib import Path

def load_data(csv_path=None):
    """Carrega e processa os dados do CSV"""
    # Se não foi fornecido um caminho, tentar encontrar o arquivo
    if csv_path is None:
        # Tentar diferentes variações do nome do arquivo
        possible_names = [
            'Base_Dados_Cursos.csv',
            'Base_Dados_Cursos.CSV',
            'base_dados_cursos.csv',
            'BASE_DADOS_CURSOS.CSV'
        ]
        
        csv_path = None
        for name in possible_names:
            if os.path.exists(name):
                csv_path = name
                break
        
        # Se ainda não encontrou, tentar no diretório atual
        if csv_path is None:
            current_dir = Path(__file__).parent if '__file__' in globals() else Path.cwd()
            for name in possible_names:
                full_path = current_dir / name
                if full_path.exists():
                    csv_path = str(full_path)
                    break
        
        # Se ainda não encontrou, usar o nome padrão e deixar o erro acontecer
        if csv_path is None:
            csv_path = 'Base_Dados_Cursos.csv'
    
    # Verificar se o arquivo existe
    if not os.path.exists(csv_path):
        # Criar DataFrame vazio com a estrutura correta se o arquivo não existir
        # Isso permite que o app inicie mesmo sem o arquivo, e o usuário pode fazer upload
        df = pd.DataFrame(columns=[
            'Data', 'Participante', 'Diretor', 'Curso', 'Duração', 
            'Participação', '% Participação', '% Câmera aberta', 
            'Respondeu a Pesquisa de Satisfação?', 'Status', 'Motivo Ausência'
        ])
        return df
    
    df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
    
    # Converter data
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')
    
    # Processar % Participação (remover % e converter para float)
    df['% Participação'] = df['% Participação'].astype(str).str.replace('%', '').str.replace(',', '.').str.replace('nan', '0')
    df['% Participação'] = pd.to_numeric(df['% Participação'], errors='coerce').fillna(0)
    
    # Processar % Câmera aberta
    df['% Câmera aberta'] = df['% Câmera aberta'].astype(str).str.replace('%', '').str.replace(',', '.').str.replace('nan', '')
    df['% Câmera aberta'] = pd.to_numeric(df['% Câmera aberta'], errors='coerce')
    
    # Converter Participação para minutos
    df['Participação_minutos'] = df['Participação'].apply(convert_time_to_minutes)
    
    # Converter Duração para minutos
    df['Duração_minutos'] = df['Duração'].apply(convert_time_to_minutes)
    
    # Criar coluna binária para pesquisa
    df['Respondeu_Pesquisa'] = df['Respondeu a Pesquisa de Satisfação?'].apply(lambda x: 1 if x == 'Sim' else 0)
    
    # Criar coluna binária para presença
    df['Presente'] = df['Status'].apply(lambda x: 1 if x == 'Presente' else 0)
    
    return df

def convert_time_to_minutes(time_str):
    """Converte string de tempo (HH:MM:SS) para minutos"""
    if pd.isna(time_str) or time_str == '':
        return 0
    
    try:
        parts = str(time_str).split(':')
        if len(parts) == 3:
            hours, minutes, seconds = map(int, parts)
            return hours * 60 + minutes + seconds / 60
        elif len(parts) == 2:
            hours, minutes = map(int, parts)
            return hours * 60 + minutes
        else:
            return 0
    except (ValueError, TypeError):
        return 0

def get_summary_metrics(df):
    """Calcula métricas gerais de resumo"""
    total_participantes = len(df)
    total_presentes = df['Presente'].sum()
    taxa_presenca = (total_presentes / total_participantes * 100) if total_participantes > 0 else 0
    
    # Média de participação = soma total de horas de participação / soma total de horas de duração * 100
    total_participacao_minutos = df['Participação_minutos'].sum()
    total_duracao_minutos = df['Duração_minutos'].sum()
    media_participacao = (total_participacao_minutos / total_duracao_minutos * 100) if total_duracao_minutos > 0 else 0
    
    total_pesquisas = df['Respondeu_Pesquisa'].sum()
    taxa_pesquisa = (total_pesquisas / total_presentes * 100) if total_presentes > 0 else 0
    
    media_camera = df[df['% Câmera aberta'].notna()]['% Câmera aberta'].mean() if df['% Câmera aberta'].notna().any() else 0
    
    total_cursos = df['Curso'].nunique()
    total_diretores = df['Diretor'].nunique()
    
    return {
        'total_participantes': total_participantes,
        'total_presentes': total_presentes,
        'taxa_presenca': taxa_presenca,
        'media_participacao': media_participacao,
        'total_pesquisas': total_pesquisas,
        'taxa_pesquisa': taxa_pesquisa,
        'media_camera': media_camera,
        'total_cursos': total_cursos,
        'total_diretores': total_diretores
    }

def get_metrics_by_director(df):
    """Calcula métricas agrupadas por diretor"""
    metrics = df.groupby('Diretor').agg({
        'Presente': ['sum', 'count'],
        'Participação_minutos': 'sum',
        'Duração_minutos': 'sum',
        'Respondeu_Pesquisa': 'sum',
        '% Câmera aberta': 'mean'
    }).reset_index()
    
    metrics.columns = ['Diretor', 'Presentes', 'Total', 'Participacao_Total_Min', 'Duracao_Total_Min', 'Pesquisas_Respondidas', 'Media_Camera']
    metrics['Taxa_Presenca'] = (metrics['Presentes'] / metrics['Total'] * 100).round(2)
    metrics['Taxa_Pesquisa'] = (metrics['Pesquisas_Respondidas'] / metrics['Presentes'].replace(0, 1) * 100).round(2)
    metrics.loc[metrics['Presentes'] == 0, 'Taxa_Pesquisa'] = 0
    # Média de participação = soma de participação / soma de duração * 100
    metrics['Media_Participacao'] = (metrics['Participacao_Total_Min'] / metrics['Duracao_Total_Min'].replace(0, 1) * 100).round(2)
    metrics.loc[metrics['Duracao_Total_Min'] == 0, 'Media_Participacao'] = 0
    metrics['Media_Camera'] = metrics['Media_Camera'].round(2)
    
    return metrics

def get_metrics_by_course(df):
    """Calcula métricas agrupadas por curso"""
    metrics = df.groupby('Curso').agg({
        'Presente': ['sum', 'count'],
        'Participação_minutos': 'sum',
        'Duração_minutos': 'sum',
        'Respondeu_Pesquisa': 'sum',
        '% Câmera aberta': 'mean'
    }).reset_index()
    
    metrics.columns = ['Curso', 'Presentes', 'Total', 'Participacao_Total_Min', 'Duracao_Total_Min', 'Pesquisas_Respondidas', 'Media_Camera']
    metrics['Taxa_Presenca'] = (metrics['Presentes'] / metrics['Total'] * 100).round(2)
    metrics['Taxa_Pesquisa'] = (metrics['Pesquisas_Respondidas'] / metrics['Presentes'].replace(0, 1) * 100).round(2)
    metrics.loc[metrics['Presentes'] == 0, 'Taxa_Pesquisa'] = 0
    # Média de participação = soma de participação / soma de duração * 100
    metrics['Media_Participacao'] = (metrics['Participacao_Total_Min'] / metrics['Duracao_Total_Min'].replace(0, 1) * 100).round(2)
    metrics.loc[metrics['Duracao_Total_Min'] == 0, 'Media_Participacao'] = 0
    metrics['Media_Camera'] = metrics['Media_Camera'].round(2)
    
    return metrics

def get_individual_metrics(df):
    """Calcula métricas por participante individual"""
    metrics = df.groupby('Participante').agg({
        'Presente': ['sum', 'count'],
        '% Participação': 'mean',
        'Respondeu_Pesquisa': 'sum',
        '% Câmera aberta': 'mean',
        'Curso': 'nunique',
        'Diretor': 'first'
    }).reset_index()
    
    metrics.columns = ['Participante', 'Presentes', 'Total_Convites', 'Media_Participacao', 
                      'Pesquisas_Respondidas', 'Media_Camera', 'Cursos_Diferentes', 'Diretor']
    metrics['Taxa_Presenca'] = (metrics['Presentes'] / metrics['Total_Convites'] * 100).round(2)
    metrics['Taxa_Pesquisa'] = (metrics['Pesquisas_Respondidas'] / metrics['Presentes'].replace(0, 1) * 100).round(2)
    metrics.loc[metrics['Presentes'] == 0, 'Taxa_Pesquisa'] = 0
    metrics['Media_Participacao'] = metrics['Media_Participacao'].round(2)
    metrics['Media_Camera'] = metrics['Media_Camera'].round(2)
    
    return metrics

def get_time_series_metrics(df):
    """Calcula métricas ao longo do tempo"""
    df_sorted = df.sort_values('Data')
    time_series = df_sorted.groupby('Data').agg({
        'Presente': ['sum', 'count'],
        'Participação_minutos': 'sum',
        'Duração_minutos': 'sum',
        'Respondeu_Pesquisa': 'sum',
        '% Câmera aberta': 'mean',
        'Curso': 'first'
    }).reset_index()
    
    time_series.columns = ['Data', 'Presentes', 'Total', 'Participacao_Total_Min', 'Duracao_Total_Min',
                          'Pesquisas_Respondidas', 'Media_Camera', 'Curso']
    time_series['Taxa_Presenca'] = (time_series['Presentes'] / time_series['Total'] * 100).round(2)
    time_series['Taxa_Pesquisa'] = (time_series['Pesquisas_Respondidas'] / time_series['Presentes'].replace(0, 1) * 100).round(2)
    time_series.loc[time_series['Presentes'] == 0, 'Taxa_Pesquisa'] = 0
    # Média de participação = soma de participação / soma de duração * 100
    time_series['Media_Participacao'] = (time_series['Participacao_Total_Min'] / time_series['Duracao_Total_Min'].replace(0, 1) * 100).round(2)
    time_series.loc[time_series['Duracao_Total_Min'] == 0, 'Media_Participacao'] = 0
    
    return time_series

