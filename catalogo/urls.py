# catalogo/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import api_views # Importa o arquivo que acabamos de criar

# O DefaultRouter do DRF lida com a criação de rotas (list/detail)
router = DefaultRouter()
router.register(r'produtos', api_views.ProdutoConsultaViewSet, basename='produto')
# Adicionaremos o ViewSet de Vendas aqui futuramente

urlpatterns = [
    # Inclui todas as rotas geradas pelo router (ex: /api/produtos/)
    path('', include(router.urls)),
]