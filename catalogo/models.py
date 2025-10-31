from django.db import models




class Categoria(models.Model):
    """Modelo para agrupar produtos (ex: Eletrônicos, Roupas, Alimentos)."""
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Categoria")
    
    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome

class Produto(models.Model):
    """Modelo central que armazena todas as informações do item à venda."""
    
    # --- Dados Básicos do Produto ---
    nome = models.CharField(max_length=255, verbose_name="Nome do Produto")
    sku = models.CharField(max_length=50, unique=True, verbose_name="SKU/Código Interno")
    codigo_barras = models.CharField(max_length=150, unique=True, blank=True, null=True, verbose_name="Código de Barras (EAN)")
    
    # --- Preços e Custos ---
    preco_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço de Custo")
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Venda")
    
    # --- Relacionamento e Estoque ---
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL, # Mantém o produto se a categoria for excluída
        null=True, 
        blank=True, 
        verbose_name="Categoria"
    )
    # A quantidade em estoque será separada em um modelo 'Estoque' para permitir multi-filial (Próxima Etapa).
    
    # --- Dados Fiscais (Críticos para PDV) ---
    ncm = models.CharField(max_length=8, verbose_name="NCM (Nomenclatura Comum do Mercosul)")
    cest = models.CharField(max_length=7, blank=True, null=True, verbose_name="CEST")
    origem_mercadoria = models.PositiveSmallIntegerField(
        choices=[(0, 'Nacional'), (1, 'Estrangeira - Importação Direta'), (2, 'Estrangeira - Adquirida no Mercado Interno')],
        default=0,
        verbose_name="Origem"
    )
    
    # --- Status ---
    ativo = models.BooleanField(default=True, verbose_name="Ativo para Venda")

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return self.nome
      
      
# Importações necessárias do Django
from django.db import models
from .models import Produto # Importando o modelo Produto que já criamos

# ------------------------------
# NOVOS MODELOS
# ------------------------------

class Variacao(models.Model):
    """
    Define um tipo de variação (ex: Tamanho, Cor, Voltagem).
    """
    nome = models.CharField(max_length=100, unique=True, verbose_name="Nome da Variação")
    
    class Meta:
        verbose_name = "Variação (Tipo)"
        verbose_name_plural = "Variações (Tipos)"

    def __str__(self):
        return self.nome

class ProdutoVariacao(models.Model):
    """
    Representa uma combinação específica de produto e variação (a SKU real).
    Ex: Camisa X (Produto) - Tamanho G (Variacao).
    Este é o item que estará no carrinho.
    """
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='variacoes')
    variacao = models.ForeignKey(Variacao, on_delete=models.CASCADE)
    
    # O PDV usará este campo para buscar a variação exata
    codigo_barras_variacao = models.CharField(max_length=150, unique=True, blank=True, null=True, verbose_name="Cód. de Barras Específico")
    
    # Preço da variação (opcionalmente pode ser diferente do Produto principal)
    preco_adicional = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Preço Adicional")
    
    class Meta:
        # Garante que um produto não tenha o mesmo tipo de variação duplicado
        unique_together = ('produto', 'variacao')
        verbose_name = "Variação do Produto"
        verbose_name_plural = "Variações dos Produtos"

    def __str__(self):
        return f"{self.produto.nome} - {self.variacao.nome}"
    
    def preco_final(self):
        """Calcula o preço de venda final para esta variação."""
        return self.produto.preco_venda + self.preco_adicional


class Estoque(models.Model):
    """
    Controla o saldo de estoque para a variação específica do produto.
    Modelamos o estoque separadamente para permitir controle multi-filial futuro.
    """
    # Relacionamento: cada entrada de estoque é para uma variação específica
    produto_variacao = models.OneToOneField(
        ProdutoVariacao, 
        on_delete=models.CASCADE, 
        primary_key=True, 
        verbose_name="Item de Estoque"
    )
    
    quantidade = models.IntegerField(default=0, verbose_name="Quantidade Atual")
    
    # Alerta para o Gerente de Estoque (US-EST-002)
    quantidade_minima = models.IntegerField(default=5, verbose_name="Estoque Mínimo de Alerta")
    
    data_ultima_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Estoque"
        verbose_name_plural = "Estoques"

    def __str__(self):
        return f"Estoque de {self.produto_variacao.produto.nome} ({self.produto_variacao.variacao.nome})"
      
      


# --- NOVOS MODELOS: VENDAS ---

class Cliente(models.Model):
    """
    Modelo para registrar clientes (CRM básico).
    """
    nome = models.CharField(max_length=255, verbose_name="Nome Completo")
    cpf_cnpj = models.CharField(max_length=18, blank=True, null=True, unique=True, verbose_name="CPF/CNPJ")
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefone")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"

    def __str__(self):
        return self.nome if self.nome else f"Cliente {self.id}"


class Venda(models.Model):
    """
    Representa o cabeçalho (a transação) da venda.
    """
    STATUS_CHOICES = [
        ('A', 'Aberta'),
        ('F', 'Fechada'),
        ('C', 'Cancelada'),
        ('P', 'Pendente (Contingência)'),
    ]

    # Dados da Transação
    numero_venda = models.IntegerField(unique=True, verbose_name="Número da Venda")
    data_venda = models.DateTimeField(auto_now_add=True, verbose_name="Data/Hora da Venda")
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='F', verbose_name="Status")
    
    # Valores
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Valor Total")
    desconto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Desconto Aplicado")

    # Relacionamentos (Por enquanto, apenas Cliente. Usuário e Caixa virão depois)
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Cliente"
    )

    class Meta:
        verbose_name = "Venda"
        verbose_name_plural = "Vendas"

    def __str__(self):
        return f"Venda Nº {self.numero_venda} - R$ {self.valor_total}"


class ItemVenda(models.Model):
    """
    Representa cada item individual dentro de uma Venda.
    """
    # Relacionamentos
    venda = models.ForeignKey(
        Venda, 
        on_delete=models.CASCADE, 
        related_name='itens', 
        verbose_name="Venda Associada"
    )
    # Qual variação do produto foi vendida
    produto_variacao = models.ForeignKey(
        ProdutoVariacao, 
        on_delete=models.PROTECT, # Importante: Não exclua o produto se ele estiver em uma venda!
        verbose_name="Produto Vendido"
    )

    # Detalhes do Item
    quantidade = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Quantidade")
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário na Venda")
    desconto_item = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Desconto no Item")
    
    class Meta:
        verbose_name = "Item da Venda"
        verbose_name_plural = "Itens da Venda"
        
    def __str__(self):
        return f"{self.produto_variacao.produto.nome} ({self.quantidade}x)"