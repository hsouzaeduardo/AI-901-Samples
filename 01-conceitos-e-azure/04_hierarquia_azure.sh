#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Módulo 01 - Tópicos: "Microsoft Azure: uma plataforma em nuvem" e
#                      "Microsoft Foundry: recurso, projeto e modelos"
#
# Percorre a hierarquia do Azure com a CLI:
#   Locatário (Entra ID) -> Assinatura -> Grupo de recursos -> Recurso (Foundry)
#   -> Projeto do Foundry -> Implantação de modelo
#
# Pré-requisitos: Azure CLI 2.80.0 ou superior (az upgrade), "az login" e papel
#                Contributor/Owner no grupo de recursos.
# ATENÇÃO: cria recursos que podem gerar custo. Rode a limpeza no final.
# ---------------------------------------------------------------------------
set -euo pipefail

LOCAL="eastus2"
RG="rg-ai901-exemplos"
RECURSO="foundry-ai901-$RANDOM"     # nome globalmente único (vira subdomínio)
PROJETO="projeto-ai901"
MODELO="gpt-4.1-mini"
VERSAO_MODELO="2025-04-14"

echo "== 1) Locatário (tenant) e identidade - Microsoft Entra ID"
az account show --query "{locatario:tenantId, usuario:user.name}" -o table

echo "== 2) Assinatura - limite de cobrança dentro do locatário"
az account show --query "{assinatura:name, id:id}" -o table

echo "== 3) Grupo de recursos - organização e gestão"
az group create --name "$RG" --location "$LOCAL" -o table

echo "== 4) Recurso do Foundry - computação, armazenamento, entrega de modelos"
az cognitiveservices account create \
  --name "$RECURSO" --resource-group "$RG" --location "$LOCAL" \
  --kind AIServices --sku S0 \
  --custom-domain "$RECURSO" \
  --assign-identity \
  --allow-project-management true \
  --yes -o table
# --assign-identity: identidade gerenciada exigida pelo gerenciamento de projetos
# --allow-project-management: não pode ser alterado depois da criação

echo "== 5) Projeto do Foundry - ambiente de trabalho isolado"
# Se falhar (ex.: CLI antiga), o script continua - crie o projeto no portal ai.azure.com
az cognitiveservices account project create \
  --name "$RECURSO" --resource-group "$RG" \
  --project-name "$PROJETO" --location "$LOCAL" -o table \
  || echo "   AVISO: projeto não criado pela CLI. Crie-o no portal do Foundry e siga em frente."

echo "== 6) Implantação de modelo - considerações do slide 'Modelos do Foundry'"
#   --sku-name      = TIPO de implantação (GlobalStandard, DataZoneStandard, Standard, ProvisionedManaged...)
#   --model-version = VERSÃO do modelo
#   --sku-capacity  = LIMITE DE TAXA (em milhares de tokens por minuto - TPM)
az cognitiveservices account deployment create \
  --name "$RECURSO" --resource-group "$RG" \
  --deployment-name "$MODELO" \
  --model-name "$MODELO" --model-version "$VERSAO_MODELO" --model-format OpenAI \
  --sku-name GlobalStandard --sku-capacity 10 -o table

echo "== 7) Ponto de extremidade e chave (vão para o arquivo .env)"
ENDPOINT=$(az cognitiveservices account show -n "$RECURSO" -g "$RG" --query properties.endpoint -o tsv)
echo "AZURE_AI_SERVICES_ENDPOINT=$ENDPOINT"
echo "AZURE_OPENAI_ENDPOINT=https://$RECURSO.openai.azure.com/openai/v1/"
echo "PROJECT_ENDPOINT=https://$RECURSO.services.ai.azure.com/api/projects/$PROJETO"
echo "AZURE_SERVICES_AI_ENDPOINT=https://$RECURSO.services.ai.azure.com/"
echo "Chave: az cognitiveservices account keys list -n $RECURSO -g $RG --query key1 -o tsv"
echo "(Prefira Microsoft Entra ID - DefaultAzureCredential - em produção. Veja 06_endpoint_sdk.py)"

echo
echo "Para LIMPAR tudo ao final da aula:"
echo "  az group delete --name $RG --yes --no-wait"
