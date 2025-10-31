from rest_framework import serializers
from .models import (
    Produto, ProdutoVariacao, Estoque, Venda, ItemVenda, Cliente
)

# ----------------------------------------------------
# 1. Serializers de Catálogo e Estoque (Para Consulta do PDV)
# ----------------------------------------------------

class EstoqueSerializer(serializers.ModelSerializer):
    """Serializer para exibir apenas a quantidade de estoque."""
    class Meta:
        model = Estoque
        fields = ('quantidade',)

class ProdutoVariacaoSerializer(serializers.ModelSerializer):
    """Serializer para as variações de um produto (o item vendável)."""
    # Usa o EstoqueSerializer para aninhar a quantidade atual
    estoque = EstoqueSerializer(read_only=True)
    
    class Meta:
        model = ProdutoVariacao
        fields = (
            'id', 
            'variacao', # ID do tipo de variação (ex: Tamanho P)
            'codigo_barras_variacao', 
            'preco_adicional', 
            'preco_final', # Propriedade calculada no Model
            'estoque'
        )
        # O campo 'preco_final' é um método do modelo e será incluído automaticamente
        # A propriedade 'variacao' deve ser tratada como ID para ser mais leve

class ProdutoVendaSerializer(serializers.ModelSerializer):
    """Serializer principal para o PDV consultar o produto."""
    # Aninha as variações (grade) dentro do produto principal
    variacoes = ProdutoVariacaoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Produto
        fields = (
            'id', 
            'nome', 
            'sku', 
            'preco_venda', 
            'variacoes'
        )
        
# ----------------------------------------------------
# 2. Serializers de Venda (Para Criação/Escrita)
# ----------------------------------------------------

class ItemVendaSerializer(serializers.ModelSerializer):
    """
    Serializer para os itens individuais da venda.
    Usado para RECEBER os dados do PDV.
    """
    # O PDV enviará o ID da Variação do Produto que está sendo vendido
    produto_variacao_id = serializers.IntegerField() 

    class Meta:
        model = ItemVenda
        # Campos que o PDV DEVE ENVIAR para o servidor
        fields = (
            'produto_variacao_id',
            'quantidade', 
            'preco_unitario', 
            'desconto_item'
        )

class VendaSerializer(serializers.ModelSerializer):
    """
    Serializer principal para RECEBER e processar a transação de venda.
    """
    # Aninha o ItemVendaSerializer para processar a lista de produtos
    itens = ItemVendaSerializer(many=True)
    
    # O PDV enviará o CPF/CNPJ. Vamos usá-lo para buscar ou criar o cliente.
    cliente_cpf_cnpj = serializers.CharField(max_length=18, required=False, allow_blank=True)

    class Meta:
        model = Venda
        fields = (
            'numero_venda', 
            'valor_total', 
            'desconto_total', 
            'cliente_cpf_cnpj', 
            'itens'
        )
        
    # Mais adiante, adicionaremos o método create para salvar o cliente e o estoque.