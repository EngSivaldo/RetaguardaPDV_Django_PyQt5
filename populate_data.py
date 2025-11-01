# populate_data.py (CÓDIGO COMPLETO PARA POPULAR MÚLTIPLOS PRODUTOS)

import os
import django
from django.db import transaction
from decimal import Decimal

# ----------------------------------------------------
# 1. Configuração do Ambiente Django
# ----------------------------------------------------
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retaguarda_pdv.settings')
django.setup()

# Importar modelos APÓS a configuração do Django
from catalogo.models import (
    Categoria, Produto, Variacao, ProdutoVariacao, Estoque,Venda, ItemVenda
)

# ----------------------------------------------------
# 2. Dados de Teste Multi-Produto
# ----------------------------------------------------

# Lista de todos os produtos que serão criados
ALL_PRODUCTS_DATA = [
    {
        "nome": "Camisa Polo Clássica",
        "sku": "CP001",
        "preco_custo": Decimal('35.00'),
        "preco_venda": Decimal('79.90'),
        "categoria_nome": "Roupas",
        "estoque_inicial": 20,
        "variacoes": [ # Produto com Variação de Tamanho
            {"tipo": "Tamanho", "valores": [("P", 0.00), ("M", 0.00), ("G", 0.00), ("GG", 10.00)]}
        ]
    },
    {
        "nome": "Refrigerante Cola 2L",
        "sku": "REF2L",
        "preco_custo": Decimal('5.00'),
        "preco_venda": Decimal('8.50'),
        "categoria_nome": "Mercearia",
        "estoque_inicial": 50,
        "variacoes": [ # Produto Simples (usa variação 'Único')
            {"tipo": "Padrão", "valores": [("Único", 0.00)]}
        ]
    },
    {
        "nome": "Sabão em Pó 1Kg",
        "sku": "SAB1K",
        "preco_custo": Decimal('9.00'),
        "preco_venda": Decimal('12.99'),
        "categoria_nome": "Limpeza",
        "estoque_inicial": 40,
        "variacoes": [ # Produto Simples (usa variação 'Único')
            {"tipo": "Padrão", "valores": [("Único", 0.00)]}
        ]
    },
    {
        "nome": "Calça Jeans Slim",
        "sku": "CJS002",
        "preco_custo": Decimal('60.00'),
        "preco_venda": Decimal('149.90'),
        "categoria_nome": "Roupas",
        "estoque_inicial": 15,
        "variacoes": [ # Produto com Variação de Tamanho
            {"tipo": "Tamanho", "valores": [("38", 0.00), ("40", 5.00), ("42", 5.00), ("44", 10.00)]}
        ]
    }
]

# ----------------------------------------------------
# 3. Funções de Criação (Refatoradas)
# ----------------------------------------------------

@transaction.atomic
def populate_data():
    print("--- 🏁 Iniciando População de Dados de Teste Multi-Produto ---")
    
    # 1. LIMPEZA DOS DADOS (Ordem Inversa de Dependência)
    
    # Deletar Vendas e Itens de Venda primeiro (Dependem de ProdutoVariacao)
    ItemVenda.objects.all().delete()
    Venda.objects.all().delete()
    
    # Deletar Estoque (Depende de ProdutoVariacao)
    Estoque.objects.all().delete()

    # Deletar Catálogo
    ProdutoVariacao.objects.all().delete()
    Produto.objects.all().delete()
    Variacao.objects.all().delete()
    Categoria.objects.all().delete()
    
    print("Dados de teste anteriores (Vendas, Estoques e Catálogo) foram limpos com sucesso.")
    
    # Dicionário para armazenar categorias já criadas
    categorias_cache = {} 
    
    for dados_produto in ALL_PRODUCTS_DATA:
        # --- A. Tratamento da Categoria ---
        categoria_nome = dados_produto.get('categoria_nome')
        if categoria_nome not in categorias_cache:
            categoria, created = Categoria.objects.get_or_create(
                nome=categoria_nome, 
                defaults={'descricao': f'Categoria de {categoria_nome}'}
            )
            categorias_cache[categoria_nome] = categoria
        else:
            categoria = categorias_cache[categoria_nome]
            
        # --- B. Criar Produto Principal ---
        produto, created = Produto.objects.get_or_create(
            sku=dados_produto['sku'], 
            defaults={
                'nome': dados_produto['nome'],
                'preco_custo': dados_produto['preco_custo'],
                'preco_venda': dados_produto['preco_venda'],
                'categoria': categoria,
                'ativo': True,
                # Adicione campos NCM, CodigoBarras etc. se desejar
            }
        )
        print(f"\n✔️ Produto Principal '{produto.nome}' (ID: {produto.id}) criado.")

        # --- C. Criar Variações e Estoque ---
        for variacao_set in dados_produto.get('variacoes', []):
            tipo_nome = variacao_set['tipo']
            
            # 1. Cria o Tipo de Variação (ex: "Tamanho" ou "Padrão")
            tipo_variacao, _ = Variacao.objects.get_or_create(nome=tipo_nome)
            
            # 2. Cria as Variações Específicas e o Estoque
            for valor_nome, adicional in variacao_set['valores']:
                
                # Cria a variação de valor (ex: "P" ou "Único")
                variacao_valor, _ = Variacao.objects.get_or_create(nome=valor_nome)

                # Cria o item vendável (ProdutoVariacao)
                cod_barras_var = f"{dados_produto['sku']}-{valor_nome}".upper().replace(' ', '')
                
                produto_variacao, created_pv = ProdutoVariacao.objects.get_or_create(
                    produto=produto,
                    variacao=variacao_valor,
                    defaults={
                        'codigo_barras_variacao': cod_barras_var,
                        'preco_adicional': Decimal(str(adicional))
                    }
                )
                
                # Cria/Atualiza o Estoque
                estoque, created_e = Estoque.objects.get_or_create(
                    produto_variacao=produto_variacao,
                    defaults={'quantidade': dados_produto['estoque_inicial']}
                )
                
                print(f"   -> Item: {produto_variacao} | Estoque: {estoque.quantidade} | Preço: R$ {produto_variacao.preco_final()}")


    print("\n--- ✅ População de Dados Concluída! ---")
    print("IDs de Produto disponíveis para teste (se o BD estava vazio): 1, 2, 3, 4.")
    print("Basta usar um desses IDs para buscar no seu PDV.")


# ----------------------------------------------------
# 4. Execução
# ----------------------------------------------------

if __name__ == '__main__':
    try:
        populate_data()
    except Exception as e:
        print(f"❌ Ocorreu um erro durante a população de dados: {e}")