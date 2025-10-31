# 🛒 Sistema PDV (Frente de Caixa) & Retaguarda (Gestão)

## 🌟 Descrição do Projeto

Este projeto consiste em um sistema comercial completo, desenvolvido com uma arquitetura desacoplada para garantir **escalabilidade e alta performance** na frente de loja.

O objetivo é fornecer uma solução robusta para o comércio de médio porte, cobrindo desde o registro rápido de vendas (PDV) até a gestão financeira, de estoque e conformidade fiscal (Retaguarda).

**Arquitetura:**

- **Backend (Retaguarda e API):** Servidor robusto para gestão e comunicação (Django).
- **Frontend (Frente de Caixa - PDV):** Aplicação Desktop dedicada para agilidade (PyQt5/PySide6).

## 🛠️ Tecnologias Utilizadas

| Componente         | Tecnologia                      | Versão (Recomendada) | Objetivo Principal                                          |
| :----------------- | :------------------------------ | :------------------- | :---------------------------------------------------------- |
| **Backend/API**    | **Python (Django)**             | 3.10+                | Lógica de Negócio, Gestão de Dados (Modelos), Painel Admin. |
| **API Framework**  | **Django REST Framework (DRF)** | Latest               | Criação dos endpoints para comunicação com o PDV.           |
| **Frontend/PDV**   | **Python (PyQt5/PySide6)**      | 5.15+ / 6.x          | Interface Gráfica Desktop, Leitura de Códigos de Barras.    |
| **Banco de Dados** | **PostgreSQL / SQLite**         | 14+                  | Persistência de Dados.                                      |

## 🚀 Status do MVP (Mínimo Produto Viável)

✅ **Modelagem de Dados (Catálogo):**

- Modelos `Categoria`, `Produto`, `Variação` e `Estoque` **concluídos**.
- Modelos `Cliente`, `Venda` e `ItemVenda` **concluídos**.
- Configuração do `Django Admin` para gestão **concluída**.

**Próximos Passos:** Implementação da API de Vendas (Sprint 1).

## ⚙️ Como Rodar o Projeto Localmente (Backend - Django)

1.  **Clone o Repositório:**
    ```bash
    git clone SUA_URL_DO_REPOSITORIO
    cd retaguarda_pdv_project
    ```
2.  **Crie e Ative o Ambiente Virtual (.venv):**
    ```bash
    python -m venv .venv
    .\.venv\Scripts\activate
    ```
3.  **Instale as Dependências:** (Instalar Django e DRF na próxima etapa)
4.  **Inicie o Servidor:**
    ```bash
    python manage.py runserver
    ```

## 📝 Licença

Este projeto está licenciado sob a Licença MIT.
