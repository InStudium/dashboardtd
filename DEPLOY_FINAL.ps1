# Script final para deploy - Historico limpo sem tokens
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY FINAL - Dashboard T&D" -ForegroundColor Cyan
Write-Host "  Repositorio: InStudium/dashboardtd" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Token via variavel de ambiente
$token = $env:GITHUB_TOKEN
if ([string]::IsNullOrWhiteSpace($token)) {
    Write-Host "ERRO: Token nao configurado!" -ForegroundColor Red
    Write-Host "Execute: `$env:GITHUB_TOKEN = 'seu_token'" -ForegroundColor Yellow
    exit 1
}

# 1. Remover historico antigo e criar novo
Write-Host "[1/4] Criando historico limpo..." -ForegroundColor Yellow
Remove-Item -Recurse -Force .git -ErrorAction SilentlyContinue
git init
Write-Host "       OK" -ForegroundColor Green

# 2. Adicionar todos os arquivos
Write-Host "`n[2/4] Adicionando arquivos..." -ForegroundColor Yellow
git add -A
$fileCount = (git status --short | Measure-Object).Count
Write-Host "       $fileCount arquivo(s) adicionado(s)" -ForegroundColor Green

# 3. Criar commit inicial limpo
Write-Host "`n[3/4] Criando commit inicial..." -ForegroundColor Yellow
git commit -m "Initial commit - Dashboard T&D Selbetti - Projeto completo"
git branch -M main
Write-Host "       Commit criado" -ForegroundColor Green

# 4. Fazer push
Write-Host "`n[4/4] Fazendo push para GitHub..." -ForegroundColor Yellow
git remote add origin "https://$token@github.com/InStudium/dashboardtd.git"
$pushOutput = git push -u origin main --force 2>&1

$success = $false
foreach ($line in $pushOutput) {
    Write-Host "       $line" -ForegroundColor Gray
    if ($line -match "Enumerating|Counting|Compressing|Writing|Total.*delta|To https|done") {
        $success = $true
    }
    if ($line -match "error|fatal|rejected|GH013") {
        Write-Host "       ERRO: $line" -ForegroundColor Red
        $success = $false
        break
    }
}

if ($LASTEXITCODE -eq 0 -or $success) {
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "  SUCESSO! Deploy concluido!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "`nRepositorio: https://github.com/InStudium/dashboardtd" -ForegroundColor Cyan
    Write-Host "`nVerifique no navegador se todos os arquivos estao la!" -ForegroundColor Yellow
} else {
    Write-Host "`nERRO ao fazer push. Verifique as mensagens acima." -ForegroundColor Red
}

# Limpar token
git remote set-url origin "https://github.com/InStudium/dashboardtd.git"
Write-Host "`nToken removido da URL (seguranca)" -ForegroundColor Green
