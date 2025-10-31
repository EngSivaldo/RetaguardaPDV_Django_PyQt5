from django.contrib import admin
# Importamos todos os modelos necessários
from .models import Categoria, Produto, Variacao, ProdutoVariacao, Estoque


# 1. Registro Simples da Categoria
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

# 2. Registro e Customização do Produto
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    # Campos exibidos na lista de produtos
    list_display = ('nome', 'sku', 'preco_venda', 'categoria', 'ativo')
    
    # Filtros laterais para facilitar a busca
    list_filter = ('categoria', 'ativo', 'origem_mercadoria')
    
    # Campos que permitem a busca rápida
    search_fields = ('nome', 'sku', 'codigo_barras', 'ncm')
    
    # Edição rápida de campos booleanos (Ativo)
    list_editable = ('ativo',)
    
    # Organização dos campos no formulário de edição
    fieldsets = (
        ("Informações Básicas", {
            'fields': ('nome', 'sku', 'codigo_barras', 'categoria', 'ativo'),
        }),
        ("Preços e Custos", {
            'fields': ('preco_custo', 'preco_venda'),
        }),
        ("Conformidade Fiscal", {
            # Estes campos são críticos e devem ser preenchidos pelo Gerente/Contador
            'fields': ('ncm', 'cest', 'origem_mercadoria'),
            'description': 'Informações essenciais para a emissão correta da Nota Fiscal (NFC-e/SAT).'
        }),
    )
    
# --- 1. Definição dos Inlines ---

class EstoqueInline(admin.StackedInline):
    """Permite editar o estoque diretamente no formulário de Variação."""
    model = Estoque
    can_delete = False  # Não queremos que o estoque seja excluído separadamente
    verbose_name = "Controle de Estoque"
    max_num = 1 # Garante que haja apenas uma entrada de estoque por variação

class ProdutoVariacaoInline(admin.TabularInline):
    """Permite adicionar/remover variações (Ex: Tamanho P, M) ao Produto."""
    model = ProdutoVariacao
    extra = 1 # Mostra 1 campo extra para adicionar nova variação
    # O Estoque Inline será exibido dentro de cada variação
    inlines = [EstoqueInline]
    
    # Campos que o gerente precisa preencher na grade
    fields = ('variacao', 'codigo_barras_variacao', 'preco_adicional')
    verbose_name = "Variação Específica (Grade)"
    verbose_name_plural = "Variações e Estoque da Grade"




@admin.register(Variacao)
class VariacaoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    
# --- 3. Registro e Customização do Produto (Agora com Inlines) ---
