# pdv_frontend_test.py (CÓDIGO COMPLETO COM ESTILO PDV)

import sys
import requests
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLineEdit, QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QSizePolicy
)
from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QFont, QColor
from decimal import Decimal

# URL base da sua API Django (ajuste se necessário)
API_BASE_URL = "http://127.0.0.1:8000/api/" 

class PDVTesteApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PDV - Protótipo Funcional (Vendas e Consulta)')
        self.setGeometry(100, 100, 1100, 700) # Tela maior
        self.carrinho = [] 
        self.produto_selecionado = None
        self.locale = QLocale(QLocale.Portuguese, QLocale.Brazil)
        self.apply_style() # Aplica o novo estilo
        self.init_ui()
    
    # ----------------------------------------------------
    # 1. FUNÇÃO DE ESTILO (QSS)
    # ----------------------------------------------------
    def apply_style(self):
        """Aplica um estilo de alto contraste e fontes grandes."""
        style = """
            QWidget {
                background-color: #2c3e50; /* Fundo escuro */
                color: #ecf0f1; /* Texto claro */
                font-size: 10pt;
            }
            QLabel#NomeProduto, QLabel#PrecoProduto {
                font-size: 20pt;
                font-weight: bold;
                color: #f1c40f; /* Amarelo de destaque */
                padding: 5px;
            }
            QLabel#TotalLabel {
                font-size: 24pt;
                font-weight: bold;
                color: #2ecc71; /* Verde forte */
                background-color: #34495e;
                padding: 10px;
                border: 2px solid #2ecc71;
            }
            QLineEdit, QTableWidget {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                padding: 8px;
                font-size: 11pt;
            }
            QPushButton {
                background-color: #007bff; /* Azul primário */
                color: white;
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton#BtnFinalizar {
                background-color: #2ecc71; /* Verde para ação principal */
                font-weight: bold;
            }
            QPushButton#BtnFinalizar:hover {
                background-color: #27ae60;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """
        self.setStyleSheet(style)


    def init_ui(self):
        main_layout = QHBoxLayout()

        # ----------------------
        # LADO ESQUERDO: CONTROLE (Proporção 1)
        # ----------------------
        controle_layout = QVBoxLayout()
        
        # 1. Campo de Busca (SKU/ID)
        controle_layout.addWidget(QLabel('Buscar Produto (ID/SKU):'))
        self.input_busca = QLineEdit(self)
        self.input_busca.setPlaceholderText("ID do Produto (Ex: 1)")
        self.input_busca.setMinimumHeight(40) # Aumenta o campo
        self.btn_busca = QPushButton('🔍 Consultar Catálogo', self)
        self.btn_busca.clicked.connect(self.buscar_produto)
        controle_layout.addWidget(self.input_busca)
        controle_layout.addWidget(self.btn_busca)
        controle_layout.addSpacing(30)

        # 2. Informações e Adição (Destaque do Produto)
        controle_layout.addWidget(QLabel('PRODUTO EM DESTAQUE:'))
        self.label_prod_nome = QLabel('Nenhum')
        self.label_prod_nome.setObjectName("NomeProduto")
        self.label_prod_nome.setWordWrap(True) # Para nomes longos
        
        self.label_prod_preco = QLabel('R$ 0.00')
        self.label_prod_preco.setObjectName("PrecoProduto")
        self.label_prod_preco.setAlignment(Qt.AlignRight)
        
        controle_layout.addWidget(self.label_prod_nome)
        controle_layout.addWidget(self.label_prod_preco)
        controle_layout.addSpacing(30)

        # 3. Adicionar ao Carrinho (Layout de Grade Simples)
        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel('Quantidade:'), 0, 0)
        self.input_qtd = QLineEdit('1')
        self.input_qtd.setMinimumHeight(40)
        grid_layout.addWidget(self.input_qtd, 0, 1)
        
        self.btn_adicionar = QPushButton('🛒 Adicionar ao Carrinho', self)
        self.btn_adicionar.clicked.connect(self.adicionar_ao_carrinho)
        self.btn_adicionar.setEnabled(False) 
        grid_layout.addWidget(self.btn_adicionar, 1, 0, 1, 2)
        
        # 4. Campo de CPF/CNPJ para a Venda
        controle_layout.addLayout(grid_layout)
        controle_layout.addSpacing(30)
        controle_layout.addWidget(QLabel('CPF/CNPJ do Cliente:'))
        self.input_cpf = QLineEdit(self)
        self.input_cpf.setPlaceholderText("Opcional: 111.111.111-11")
        self.input_cpf.setMinimumHeight(30)
        controle_layout.addWidget(self.input_cpf)
        
        controle_layout.addStretch(1) 
        main_layout.addLayout(controle_layout, 1) 

        # ----------------------
        # LADO DIREITO: CARRINHO E TOTAL (Proporção 2.5 - Maior destaque)
        # ----------------------
        carrinho_layout = QVBoxLayout()
        carrinho_layout.addWidget(QLabel('**CARRINHO DE VENDA**'))

        # 1. Tabela do Carrinho
        self.tabela_carrinho = QTableWidget(self)
        self.tabela_carrinho.setColumnCount(5)
        self.tabela_carrinho.setHorizontalHeaderLabels(
            ['ID Variação', 'Produto/Var.', 'Qtd.', 'Preço Unit.', 'Subtotal']
        )
        # Distribui as colunas para melhor visualização
        self.tabela_carrinho.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela_carrinho.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents) # Subtotal
        carrinho_layout.addWidget(self.tabela_carrinho)

        # 2. Totalizadores (DESTAQUE)
        total_layout = QHBoxLayout()
        label_total_texto = QLabel('TOTAL A PAGAR:')
        label_total_texto.setFont(QFont("Arial", 16, QFont.Bold))
        label_total_texto.setStyleSheet("color: #ecf0f1;")
        
        self.label_total = QLabel('R$ 0,00')
        self.label_total.setObjectName("TotalLabel")
        self.label_total.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.label_total.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        total_layout.addWidget(label_total_texto)
        total_layout.addWidget(self.label_total)
        carrinho_layout.addLayout(total_layout)

        # 3. Botões de Ação
        btn_acao_layout = QHBoxLayout()
        self.btn_remover = QPushButton('❌ REMOVER Item', self)
        
        self.btn_finalizar = QPushButton('PAGAR / FINALIZAR VENDA (F10)', self)
        self.btn_finalizar.setObjectName("BtnFinalizar")
        self.btn_finalizar.setShortcut(Qt.Key_F10) # Atalho de teclado

        self.btn_remover.clicked.connect(self.remover_do_carrinho)
        self.btn_finalizar.clicked.connect(self.finalizar_venda) 
        
        btn_acao_layout.addWidget(self.btn_remover)
        btn_acao_layout.addWidget(self.btn_finalizar)
        carrinho_layout.addLayout(btn_acao_layout)

        main_layout.addLayout(carrinho_layout, 2) # Proporção 2 para o carrinho
        self.setLayout(main_layout)

    # ... (MÉTODOS restantes: buscar_produto, adicionar_ao_carrinho, remover_do_carrinho, atualizar_tabela_carrinho, finalizar_venda)
    # ... (Os métodos de lógica permanecem os mesmos)

    def buscar_produto(self):
        """Busca o produto na API e exibe os dados (GET)."""
        produto_id = self.input_busca.text().strip()
        self.btn_adicionar.setEnabled(False)
        self.produto_selecionado = None
        
        if not produto_id:
            QMessageBox.warning(self, "Alerta", "Insira o ID do produto.")
            return

        try:
            url = f"{API_BASE_URL}produtos/{produto_id}/"
            response = requests.get(url, timeout=5)
            
            self.label_prod_nome.setText('Buscando...')
            self.label_prod_preco.setText('...')
            
            if response.status_code == 200:
                dados = response.json()
                variacoes_encontradas = dados.get('variacoes')

                if variacoes_encontradas:
                    # Simplificação: assume a primeira variação
                    variacao_venda = variacoes_encontradas[0] 
                    
                    self.produto_selecionado = {
                        'id': dados.get('id'),
                        'nome': dados.get('nome'),
                        'variacao_id': variacao_venda.get('id'), 
                        'variacao_nome': variacao_venda.get('variacao'), 
                        'preco_venda': Decimal(str(variacao_venda.get('preco_final', '0.00'))),
                        'estoque': variacao_venda.get('estoque', {}).get('quantidade', 0),
                    }
                    
                    # Usa o locale para formatação de moeda
                    preco_formatado = self.locale.toCurrencyString(float(self.produto_selecionado['preco_venda']))
                    
                    self.label_prod_nome.setText(f"{self.produto_selecionado['nome']} (Estoque: {self.produto_selecionado['estoque']})")
                    self.label_prod_preco.setText(preco_formatado)
                    self.btn_adicionar.setEnabled(True)
                    # Mantido para feedback visual, pode ser removido depois
                    # QMessageBox.information(self, "Sucesso", "Produto encontrado! Pronto para adicionar.") 
                else:
                    self.label_prod_nome.setText('Produto sem variações/estoque')
                    self.label_prod_preco.setText('R$ 0.00')
                    QMessageBox.warning(self, "Alerta", "Produto encontrado, mas sem variações vendáveis/estoque.")
                    
            elif response.status_code == 404:
                self.label_prod_nome.setText(f"ID {produto_id} não encontrado")
                self.label_prod_preco.setText('R$ 0.00')
                
            else:
                QMessageBox.critical(self, "Erro API", f"Erro ao buscar produto. Status: {response.status_code}")
                self.label_prod_nome.setText('ERRO DE SERVIDOR')

        except requests.exceptions.RequestException as e:
            self.label_prod_nome.setText('ERRO DE CONEXÃO')
            QMessageBox.critical(self, "Erro de Conexão", 
                                 f"Não foi possível conectar à API Django. Erro: {e}")

    # --- Métodos de Lógica (Os mesmos que você forneceu) ---
    
    def adicionar_ao_carrinho(self):
        if not self.produto_selecionado:
            QMessageBox.warning(self, "Alerta", "Busque um produto válido primeiro.")
            return

        try:
            qtd = int(self.input_qtd.text())
            if qtd <= 0:
                QMessageBox.warning(self, "Alerta", "Quantidade deve ser positiva.")
                return
        except ValueError:
            QMessageBox.critical(self, "Erro", "Quantidade inválida.")
            return

        item = {
            'id': self.produto_selecionado['variacao_id'],
            'nome': self.produto_selecionado['nome'],
            'preco_unitario': self.produto_selecionado['preco_venda'],
            'quantidade': qtd,
            'subtotal': self.produto_selecionado['preco_venda'] * qtd,
        }
        
        self.carrinho.append(item)
        self.atualizar_tabela_carrinho()
        
        self.input_busca.clear()
        self.input_qtd.setText('1')
        self.produto_selecionado = None
        self.btn_adicionar.setEnabled(False)
        self.label_prod_nome.setText('Nenhum')
        self.label_prod_preco.setText('R$ 0.00')
        
        # 2. Mensagem de Sucesso (para dar feedback claro)
        QMessageBox.information(self, "Item Adicionado", f"'{item['nome']}' (Qtd: {item['quantidade']}) adicionado ao carrinho. Procure o próximo item.")
        
        # 3. Retorna o foco para o campo de busca/código de barras
        self.input_busca.setFocus()
        # -----------------------------------------------


    def remover_do_carrinho(self):
        linhas_selecionadas = self.tabela_carrinho.selectedIndexes()
        if not linhas_selecionadas:
            QMessageBox.warning(self, "Alerta", "Selecione um item para remover.")
            return
        linha_para_remover = linhas_selecionadas[0].row()
        if 0 <= linha_para_remover < len(self.carrinho):
            del self.carrinho[linha_para_remover]
            self.atualizar_tabela_carrinho()
        

    def atualizar_tabela_carrinho(self):
        self.tabela_carrinho.setRowCount(len(self.carrinho))
        total_venda = Decimal('0.00')

        for i, item in enumerate(self.carrinho):
            subtotal = item['preco_unitario'] * item['quantidade']
            total_venda += subtotal
            
            # Formatação de preços para exibição
            preco_unit_str = self.locale.toString(float(item['preco_unitario']), 'f', 2)
            subtotal_str = self.locale.toString(float(subtotal), 'f', 2)

            self.tabela_carrinho.setItem(i, 0, QTableWidgetItem(str(item['id'])))
            self.tabela_carrinho.setItem(i, 1, QTableWidgetItem(item['nome']))
            self.tabela_carrinho.setItem(i, 2, QTableWidgetItem(str(item['quantidade'])))
            self.tabela_carrinho.setItem(i, 3, QTableWidgetItem(preco_unit_str))
            self.tabela_carrinho.setItem(i, 4, QTableWidgetItem(subtotal_str))
            
            # Alinha textos à direita para colunas monetárias
            self.tabela_carrinho.item(i, 2).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela_carrinho.item(i, 3).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela_carrinho.item(i, 4).setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

        total_formatado = self.locale.toCurrencyString(float(total_venda))
        self.label_total.setText(total_formatado) # Deixa o R$ pois o label é grande

    def finalizar_venda(self):
        if not self.carrinho:
            QMessageBox.warning(self, "Alerta", "Carrinho vazio. Adicione produtos antes de finalizar.")
            return
            
        total_venda = sum(item['subtotal'] for item in self.carrinho)
        
        itens_payload = [
            {
                'produto_variacao_id': item['id'],
                'quantidade': item['quantidade'],
                'preco_unitario': str(item['preco_unitario']), 
                'desconto_item': '0.00' 
            }
            for item in self.carrinho
        ]
        
        payload = {
            'valor_total': str(total_venda),
            'desconto_total': '0.00',
            'cliente_cpf_cnpj': self.input_cpf.text().strip(),
            'itens': itens_payload
        }

        try:
            url = f"{API_BASE_URL}vendas/"
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 201: 
                QMessageBox.information(self, "Sucesso!", f"Venda registrada com sucesso! ID: {response.json().get('numero_venda', 'N/A')}")
                self.carrinho = [] 
                self.atualizar_tabela_carrinho()
            elif response.status_code == 400: 
                erros = response.json()
                erro_msg = json.dumps(erros, indent=2, ensure_ascii=False)
                QMessageBox.critical(self, "Erro de Validação (400)", f"Falha ao registrar a venda. Erros:\n{erro_msg}")
            else:
                QMessageBox.critical(self, "Erro API", f"Falha no servidor. Status: {response.status_code}. Resposta: {response.text[:100]}...")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Erro de Conexão", f"Não foi possível conectar ao endpoint de Vendas. Erro: {e}")


if __name__ == '__main__':
    # ATENÇÃO: É necessário ter o servidor Django RODANDO e o produto de teste criado!
    app = QApplication(sys.argv)
    ex = PDVTesteApp()
    ex.show()
    sys.exit(app.exec_())