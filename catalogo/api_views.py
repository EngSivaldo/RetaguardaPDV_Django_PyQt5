# catalogo/api_views.py

from rest_framework import viewsets
from rest_framework.permissions import AllowAny # Usaremos esta permissão
from .models import Produto
from .serializers import ProdutoVendaSerializer

# ----------------------------------------------------
# 1. ViewSet para Consulta de Produtos (GET)
# ----------------------------------------------------

class ProdutoConsultaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para listar e buscar produtos e suas variações (grade/estoque).
    É ReadOnly, ou seja, só permite GET (consulta) e não POST, PUT, DELETE.
    Este endpoint é usado pelo PDV para carregar o catálogo.
    """
    queryset = Produto.objects.filter(ativo=True)
    serializer_class = ProdutoVendaSerializer
    permission_classes = [AllowAny] # Permite acesso sem autenticação (por enquanto)
    # Futuramente, trocaremos para uma permissão de API Key.

    # O filtro 'ativo=True' garante que apenas produtos ativos sejam retornados.
    
# ----------------------------------------------------
# 2. ViewSet para Registro de Vendas (POST)
# ----------------------------------------------------

# (O ViewSet de Vendas é mais complexo e será implementado na próxima etapa
# junto com o método .create() no Serializer, para garantir transação e estoque.)