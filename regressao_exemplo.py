"""
Exemplo de análise de Regressão Linear para relacionar:
- Volumes de treinamento
- Ementas dos cursos
- Performance melhorada dos profissionais

Este arquivo serve como base para implementação futura.
"""

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import utils

def prepare_data_for_regression(df):
    """
    Prepara dados para análise de regressão linear.
    
    Variáveis independentes (X):
    - Número de cursos participados
    - Média de participação
    - Taxa de presença
    - Taxa de resposta em pesquisas
    - Média de câmera aberta
    
    Variável dependente (y):
    - Performance (a ser definida com dados futuros)
    """
    
    # Calcular métricas por participante
    individual_metrics = utils.get_individual_metrics(df)
    
    # Preparar features
    X = individual_metrics[[
        'Cursos_Diferentes',
        'Media_Participacao',
        'Taxa_Presenca',
        'Taxa_Pesquisa',
        'Media_Camera'
    ]].fillna(0)
    
    # Exemplo: criar variável de performance (substituir por dados reais)
    # Por enquanto, usamos uma combinação das métricas como proxy
    y = (
        individual_metrics['Media_Participacao'] * 0.3 +
        individual_metrics['Taxa_Presenca'] * 0.3 +
        individual_metrics['Taxa_Pesquisa'] * 0.2 +
        individual_metrics['Media_Camera'].fillna(0) * 0.2
    )
    
    return X, y, individual_metrics

def train_regression_model(X, y):
    """Treina modelo de regressão linear"""
    
    # Dividir dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Treinar modelo
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Fazer previsões
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Calcular métricas
    r2_train = r2_score(y_train, y_pred_train)
    r2_test = r2_score(y_test, y_pred_test)
    mse_train = mean_squared_error(y_train, y_pred_train)
    mse_test = mean_squared_error(y_test, y_pred_test)
    
    return {
        'model': model,
        'r2_train': r2_train,
        'r2_test': r2_test,
        'mse_train': mse_train,
        'mse_test': mse_test,
        'coefficients': model.coef_,
        'intercept': model.intercept_,
        'feature_names': X.columns.tolist()
    }

def analyze_course_impact(df):
    """
    Analisa o impacto de cada curso nas métricas de engajamento.
    """
    course_metrics = utils.get_metrics_by_course(df)
    
    # Calcular correlações entre características dos cursos e engajamento
    # (a ser expandido com dados de ementas)
    
    return course_metrics

if __name__ == "__main__":
    # Exemplo de uso
    print("Carregando dados...")
    df = utils.load_data()
    
    print("Preparando dados para regressão...")
    X, y, individual_metrics = prepare_data_for_regression(df)
    
    print("Treinando modelo...")
    results = train_regression_model(X, y)
    
    print("\n=== Resultados da Regressão Linear ===")
    print(f"R² (Treino): {results['r2_train']:.4f}")
    print(f"R² (Teste): {results['r2_test']:.4f}")
    print(f"MSE (Treino): {results['mse_train']:.4f}")
    print(f"MSE (Teste): {results['mse_test']:.4f}")
    
    print("\n=== Coeficientes ===")
    for i, feature in enumerate(results['feature_names']):
        print(f"{feature}: {results['coefficients'][i]:.4f}")
    
    print(f"\nIntercepto: {results['intercept']:.4f}")
    
    print("\n=== Análise de Impacto por Curso ===")
    course_impact = analyze_course_impact(df)
    print(course_impact)

