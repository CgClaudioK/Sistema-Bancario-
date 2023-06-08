import re
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime
import textwrap

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []
    
    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)
    
    def adicionar_contas(self, conta):
        self.contas.append(conta)

class Pessoa_fisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
        self._data_criacao = datetime.now()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico
    
    def saque(self, valor):
        saldo_atual = self.saldo
        excedeu_saldo = valor > saldo_atual

        if  excedeu_saldo:
            print("Saldo Insuficiente para efetuar o saque")
        elif valor > 0:
            self._saldo -= valor
            print(f"Saque no valor de: R${valor:.2f} efetuado com sucesso\n")
            return True
        else:
            print("Operação falhou, tente novamente")
        return False

    def depositar(self, valor):
        if valor > 0:
            print("Deposito realizado com sucesso no valor de:" , valor)
            self._saldo += valor
        else: 
            print("Depósito com valores incorretos, tente novamente")
            return False
        return True 
class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques
    
    def saque(self, valor):
        num_saque_diario = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"]==Saque.__name__]
        )
        excedeu_limite = valor > self._limite
        excedeu_saques = num_saque_diario >= self._limite_saques

        if excedeu_limite:
            print("Operação Falhou! O valor do saque excede o limite")
        
        elif excedeu_saques:
            print("Limite diário de saques excedido, tente novamente amanhã!")
        
        else:
            return super().saque(valor)
        
        return False
        
    def __str__(self):
        return  f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

class Historico:
    def __init__(self):
        self._transacoes = []

    @property

    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                "tipo":transacao.__class__.__name__,
                "valor":transacao.valor,
                "data":datetime.now().strftime("%d/%m/%Y, %H:%M:%S"),
            }

        )

class Transacao(ABC):
    @property
    @abstractproperty
    def valor(self):
        pass
    
    @abstractclassmethod
    def registrar(self,conta):
        pass

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.saque(self.valor)

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

def menu():
    menu = """    
    Selecione a Opção desejada
    ===================
    [c] -> Cadastro novo user
    [n] -> Criar CC
    [lc]-> Listar CC
    [d] -> Depósito
    [s] -> Saque
    [e] -> Extrato
    [q] -> Quit
    

    ====================
            
            ==>"""
    return input(menu)

def filtrar_clientes(cpf, clientes):
    usuarios_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\nCliente não possui conta, crie uma")
        return
    return cliente.contas[0]

def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("\n Cliente não encontrado!")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado!")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)

def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_clientes(cpf, clientes)

    if not cliente:
        print("\nCliente não encontrado!")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n=======EXTRATO BANCÁRIO SICREDI========")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")

def cadastro_usuarios(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_clientes(cpf, clientes)

    if cliente:
        print("\nJá possui usuário com esse CPF!")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd/mm/aaaa): ")
    endereco = input("Informe o endereço (logradouro, numero, bairro, cidade/sigla estado): ")

    cliente = Pessoa_fisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    clientes.append(cliente)
    print("=== Usuário criado com sucesso! ===")

def nova_conta(numero_conta,clientes,contas):
    cpf = input("Informe o CPF do usuário: ")
    cliente = filtrar_clientes(cpf, clientes)
    if not cliente:
            print("\nUsuário não encontrado, fluxo de criação de conta encerrado!")
            return
    conta=ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)
    print(f"Conta {numero_conta} criada com sucesso para o usuário {cliente.nome}")



def listar_contas(contas):
    for conta in contas:
         print("=" * 100)
         print(textwrap.dedent(str(conta)))



def main():
    contas = []
    clientes = []
    while True:

        opcao = menu()

        if opcao == "d": 
            depositar(clientes)
        
        elif opcao == "s": 
            sacar(clientes)
            
        elif opcao == "e": 
            exibir_extrato(clientes)

        elif opcao == "c":
            cadastro_usuarios(clientes)

        elif opcao == "n":
             numero_conta = len(contas) + 1
             conta = nova_conta(numero_conta,clientes, contas)
             if conta:
                contas.append(conta)
             

        elif opcao == "lc":
            listar_contas(contas)
            
        elif opcao == "q":
            print("Quit")
            break

        else: 
            print("Opção escolhida é inválida, tente novamente")

main()