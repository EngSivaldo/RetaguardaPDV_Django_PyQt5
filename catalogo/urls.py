# catalogo/urls.py

from django.urls import path, include
from rest_framework import routers
from . import api_views

# Router principal para as APIs de produção
router = routers.DefaultRouter()
router.register(r'produtos', api_views.ProdutoConsultaViewSet, basename='produto-consulta')
router.register(r'vendas', api_views.VendaCreateViewSet, basename='venda-create')

# Router para o formulário de teste (GET /api/vendas-teste/)
test_form_router = routers.DefaultRouter()
test_form_router.register(r'vendas-teste', api_views.VendaTestFormViewSet, basename='venda-teste')

urlpatterns = [
    # Inclui as rotas padrão da API
    path('', include(router.urls)),
    
    # Inclui a rota do formulário de teste (GET /api/vendas-teste/)
    path('', include(test_form_router.urls)) 
]