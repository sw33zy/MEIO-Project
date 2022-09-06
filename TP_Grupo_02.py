import numpy as np
import math
import re

weeks = 50  # Nº de semanas a simular
i = 0.15 / weeks  # Taxa semanal de existencia
b = 115  # Preço unitario de um saco
t = 4  # Tamanho do periodo de revisão
revisao1 = 1  # Semana da primeira revisão (opcional)
C1 = i * b  # Custo de existencia semanal
C2 = 36  # Custo de quebra por elemento
C3 = 1500  # Custo de passagem de encomenda
pLT = [0.27, 0.53, 0.2]  # [p1,p2,p3]
LT = pLT[0] + 2 * pLT[1] + 3 * pLT[2]  # Tempo de entrega médio
pPerda = 0.4  # Probabilidade de quebra nas encomendas em atraso
inicioEpocaAlta = 23  # Inicio da epoca contigua
fimEpocaAlta = 45  # Inicio da epoca contigua
#
S_alta = S_baixa = s_alta = s_baixa = 0
# Procuras N(r_x, dv_x) , x E {alta,baixa}
r_alta = 642.8985506
dv_alta = 12.74816073
r_baixa = 462.0246047
dv_baixa = 16.01013738


# Objeto representativo de uma Semana
class Semana:
    lucro = custo = 0.0
    id = perdas = atrasos = vendas = stock = 0
    pedido = False
    chegada = False

    # Incializador de uma semana
    def __init__(self, id_):
        self.id = id_

    # Converte uma semana em uma linha de texto CSV
    def __str__(self):
        return ("" + str(self.id) + ";" +
                str(self.vendas) + ";" +
                str(self.stock) + ";" +
                str(self.pedido) + ";" +
                str(self.chegada) + ";-;" +
                str(self.lucro) + ";" + str(self.custo) + ";" +
                str(self.atrasos) + ";" + str(self.perdas) + ";"
                )

    # Limpa os dados atuais menos a identificação da semana e a procura da mesma
    def clean(self):
        self.perdas = self.atrasos = self.stock = 0
        self.lucro = self.custo = 0.0

    # Regista uma encomenda e os seus custos devolvendo por fim o tempo de demorará a chegar
    def encomendar(self):
        self.pedido = True
        self.custo += C3
        return np.random.choice([1, 2, 3], 1, pLT)[0]

    # Recebe uma encomenda e acresta-a ao stock
    def receber(self, inventario):
        self.chegada = True
        self.stock += inventario

    # Efetua as vendas da respetiva semana e respetiva contabilidade
    def negociar(self):
        # Se ainda nao estivermos em quebra
        if self.stock > 0:
            # Efetuar as vendas
            self.stock -= self.vendas
            # Se houve uma quebra no stock calcular as quebras
            if self.stock < 0:
                self.perdas = round(pPerda * abs(self.stock))
                self.stock += self.perdas
                self.atrasos = abs(self.stock)
            # Senão calcular o custo de posse dos elementos restantes
            else:
                self.custo += C1 * self.stock
        # Senão já estamos em quebra
        else:
            self.perdas = round(pPerda * self.vendas)
            self.atrasos = self.vendas - self.perdas
            self.stock -= self.atrasos
        self.custo += C2 * self.atrasos
        self.lucro = (self.vendas - self.perdas) * b - self.custo

    # Herdas o stock anterior (incluindo o que falta entregar)
    def herdar(self, week):
        self.stock += week.stock


# Inicializar a tabela da simulação
def init_table(stock_inicial):
    # Criar as instancias das semanas
    table = [Semana(i) for i in range(weeks + 1)]
    # Definir as vendas para as instancias criadas
    for i in range(1, weeks + 1):
        if inicioEpocaAlta <= i <= fimEpocaAlta:
            table[i].vendas = int(np.random.normal(r_alta, dv_alta, size=None))
        else:
            table[i].vendas = int(np.random.normal(r_baixa, dv_baixa, size=None))

    # Defenir o stock inicial (semana 0)
    table[0].stock = stock_inicial

    return table


# Elimina os dados simulados para se poder efetuar uma nova simulação sobre a mesma população
def cleanup_table(table):
    for i in range(1, weeks + 1):
        table[i].clean()
    return table


# Indica se a semana dada deve adotar a politica alta ou baixa
def politica_alta(week):
    anticipation = math.ceil(LT)
    return (inicioEpocaAlta - anticipation) <= week <= (fimEpocaAlta - anticipation)


# Efetua a simulação
def simulation(table, S_alta, S_baixa, s_alta, s_baixa, t, weeks):
    for index in range(1, weeks + 1):
        # Herdar o stock da semana anterior (e mais so que não sei como o C1 é aplicado sema a semana :') )
        table[index].herdar(table[index - 1])
        # Vender as unidades em procura
        table[index].negociar()
        # Se estamos no periodo de revisao
        if (index - revisao1) % t == 0:
            # Determinos os parametros para a epoca em que estamos
            if politica_alta(index):
                s = s_alta
                S = S_alta
            else:
                s = s_baixa
                S = S_baixa

            # Se o stock estiver abaixo do ponto predefinido
            if table[index].stock < s:
                # Encomendamos
                L = table[index].encomendar()
                # Receber a encomenda se a semanda de chegada ainda pertecer à simulação
                if index + L < weeks:
                    table[index + L].receber(S - table[index].stock)
    return table


# Lê dados do utilizador
def readFromUser():
    global S_alta, S_baixa, s_alta, s_baixa
    print("Simulação")
    S_alta = int(input("Insira o S da epoca alta: "))
    s_alta = int(input("Insira o s da epoca alta: "))
    S_baixa = int(input("Insira o S da epoca baixa: "))
    s_baixa = int(input("Insira o s da epoca baixa: "))


# Escreve a simulação num ficheiro CSV
def write(simcoiunt, table):
    name = 'simulacao' + str(simcoiunt) + '.csv'
    print("Resultado escrito no ficheiro", name)
    with open(name, 'w') as file:
        file.write("Semana;Vendas;Stock;Pedido;Chegada;-;lucro; Custo;Atrasos;Perdas;\n")
        for i in range(1, 51):
            # Substituir todos os pontos por virgulas (Para funcionar direito em EXCEL)
            # e escrever a linha da tabela no ficheiro
            file.write(re.sub(r'\.', r',', str(table[i])) + "\n")


# Main
# Algoritmo Base
simcount = 1
readFromUser()
table = init_table(s_baixa)  # Criar um possivel conjunto de vendas para o ano 2020
while True:
    table = cleanup_table(table)  # Limpar dados da simulação (se existirem)
    table = simulation(table, S_alta, S_baixa, s_alta, s_baixa, t, weeks)  # Efetuar a simulação
    write(simcount, table)  # Escrever o resultado num ficheiro
    simcount += 1  # Aumentar o nº da simulação
    # Se o utilizador nao insirir  s ou si ou sim ou S ou SI ou SIM ou Si ou sI ou sIM ou sIm então termina o programa
    if re.search(r'(?i:si?m?)',
                 input("Deseja fazer outra simulação com os mesmos dados de procura? (Sim/Não) ")) is None:
        break
    readFromUser()
