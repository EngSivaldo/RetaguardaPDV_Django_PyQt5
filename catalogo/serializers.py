# catalogo/serializers.py

from rest_framework import serializers
from django.db import transaction 
from django.db import models # Necessário para models.F()

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
    
    # O PDV enviará o CPF/CNPJ.
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
        read_only_fields = ('numero_venda',) # O Django/BD gerencia

    def validate(self, data):
        """Valida se a quantidade pedida está disponível em estoque."""
        erros_estoque = {}
        if 'itens' not in data or not data['itens']:
             raise serializers.ValidationError({'itens': 'A lista de itens da venda não pode estar vazia.'})

        for item_data in data['itens']:
            try:
                variacao_id = item_data['produto_variacao_id']
                quantidade_pedida = item_data['quantidade']
                
                produto_variacao = ProdutoVariacao.objects.get(pk=variacao_id)
                
                try:
                    estoque_atual = produto_variacao.estoque.quantidade
                except Estoque.DoesNotExist:
                    estoque_atual = 0

                if quantidade_pedida > estoque_atual:
                    erros_estoque[variacao_id] = f"Estoque insuficiente. Disponível: {estoque_atual}, Pedido: {quantidade_pedida}."
            
            except ProdutoVariacao.DoesNotExist:
                erros_estoque[variacao_id] = "Variação de produto não encontrada."

        if erros_estoque:
            raise serializers.ValidationError({'itens': erros_estoque})
            
        return data


    def create(self, validated_data):
        """
        [LÓGICA CRÍTICA]
        Processa a transação de venda e atualiza o estoque de forma atômica.
        """
        with transaction.atomic():
            
            # 1. Processar o Cliente
            cliente_cpf_cnpj = validated_data.pop('cliente_cpf_cnpj', None)
            cliente = None
            if cliente_cpf_cnpj:
                cliente, _ = Cliente.objects.get_or_create(
                    cpf_cnpj=cliente_cpf_cnpj, 
                    defaults={'nome': 'Cliente Avulso (PDV)'}
                )
            
            # 2. Separar Itens do Carrinho
            itens_data = validated_data.pop('itens')

            # CORREÇÃO 1: Remove o campo 'numero_venda' da inserção inicial 
            validated_data.pop('numero_venda', None) 

            # 3. Criar a Venda Principal (numero_venda será temporariamente NULL)
            venda = Venda.objects.create(cliente=cliente, **validated_data)
            
            # Isso garante que ele seja ÚNICO no DB e resolve o erro UNIQUE constraint.
            if venda.numero_venda is None:
                venda.numero_venda = venda.id
                venda.save(update_fields=['numero_venda'])
            
            # 4. Criar os Itens da Venda e Atualizar o Estoque
            for item_data in itens_data:
                variacao_id = item_data.pop('produto_variacao_id')
                quantidade = item_data['quantidade']

                produto_variacao = ProdutoVariacao.objects.select_for_update().get(pk=variacao_id) 
                
                # 4a. Baixa de Estoque
                Estoque.objects.filter(produto_variacao=produto_variacao).update(
                    quantidade=models.F('quantidade') - quantidade
                )
                
                # 4b. Criação do ItemVenda
                ItemVenda.objects.create(
                    venda=venda, 
                    produto_variacao=produto_variacao, 
                    **item_data
                )

            return venda