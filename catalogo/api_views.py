# catalogo/api_views.py

from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.renderers import TemplateHTMLRenderer # NOVO
from rest_framework.response import Response # NOVO

from .models import Produto, Venda 
from .serializers import ProdutoVendaSerializer, VendaSerializer 


# ----------------------------------------------------
# 1. ViewSet para Consulta de Produtos (GET)
# ----------------------------------------------------

class ProdutoConsultaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Endpoint de consulta (somente leitura) para o PDV.
    """
    queryset = Produto.objects.all()
    serializer_class = ProdutoVendaSerializer # CORRIGIDO: Nome do Serializer
    permission_classes = [AllowAny]
    
    
# ----------------------------------------------------
# 2. ViewSet para Registro de Vendas (POST)
# ----------------------------------------------------

class VendaCreateViewSet(CreateModelMixin, GenericViewSet):
    """
    ViewSet que permite apenas a criação (POST) de uma nova venda.
    """
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer
    permission_classes = [AllowAny]


# ----------------------------------------------------
# 3. ViewSet para Formulário de Teste (GET) - NOVO
# ----------------------------------------------------

class VendaTestFormViewSet(GenericViewSet):
    """
    View customizada APENAS para exibir um formulário de teste em HTML.
    O POST é feito diretamente para /api/vendas/
    """
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = [AllowAny]
    
    # Aponta para o template que está em catalogo/templates/catalogo/
    template_name = 'catalogo/venda_test_form.html' 

    def list(self, request):
        """No método GET, apenas renderiza o formulário."""
        # Retorna o contexto vazio
        return Response({})