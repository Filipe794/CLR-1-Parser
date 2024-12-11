import pandas as pd


# Lê o arquivo CSV e prepara o dicionário da tabela de parsing
df = pd.read_csv('table.csv')
df.set_index(df.columns[0], inplace=True)
dicionario = df.to_dict(orient='index')
for state, actions in dicionario.items():
    for readingSimb, action in actions.items():
        if pd.isna(action):
            dicionario[state][readingSimb] = None


# PILHA
class Stack:
    def __init__(self):
        self.content = []

    def push(self, input):
        if isinstance(input, list):
            self.content.extend(input)  # Adiciona todos os elementos da lista
        else:
            self.content.append(input)  # Adiciona apenas um elemento

    def pop(self, n=1):
        if n > len(self.content):
            raise IndexError("ERRO: Tentativa de remover mais elementos do que a pilha contém.")
        else:
            self.content = self.content[:-n]

    def top(self):
        if len(self.content) > 0:
            return self.content[-1]
        else:
            return None

    def copyContent(self):
        return self.content.copy()

    def __str__(self):
        return f"Stack({self.content})"


# REGRAS DE PRODUÇÃO
class Rule:
    def __init__(self, head: str, product: list):
        self.head = head
        self.product = product

    def __str__(self):
        product_str = " ".join(self.product)
        return f"{self.head} -> {product_str}"

    def __len__(self):
        return len(self.product)


# Função para buscar a ação na tabela
def get_action(state: int, readingSimb: str):
    action = dicionario.get(state, {}).get(readingSimb)
    return action if action else None


# Terminais e Não terminais
terminals = ["id", "+", "*", "(", ")", "$"]
nonTerminals = ["E", "T", "F"]

# Regras de Produção
rulesDict = {
    1: Rule("E", ["T", "+", "E"]),
    2: Rule("E", ["T"]),
    3: Rule("T", ["F", "*", "T"]),
    4: Rule("T", ["F"]),
    5: Rule("F", ["(", "E", ")"]),
    6: Rule("F", ["id"]),
}


# Retorna os PASSOS da análise sintática
def get_rows(input:str, rules:dict):
    find_i = False
    cadeia = []

    # Converte a string em uma lista de TOKENS
    for char in input:
        # TRATAMENTO PARA O "id"
        if char not in terminals:
            if find_i == True:
                if char == "d":
                    cadeia.append("id")
                    find_i = False
                else:
                    raise Exception(f"erro léxico no token {char}")
            else:
                if char == "i":
                    find_i = True
                else:
                    raise Exception(f"erro léxico no token {char}")
        # CASO GERAL
        else:
            cadeia.append(char)
    cadeia.append("$")

    # Pilhas de estado e símbolos
    stateStack = Stack()
    simbolStack = Stack()

    # Inicialização
    stateStack.push(0)  # Estado inicial
    pointer = 0  # Apontador para a entrada
    action = None

    rows = [] #Passos da Análise

    # Loop do parser
    while action != 'acc':
        currentState = stateStack.top()  # estado atual
        currentSymbol = cadeia[pointer]  # símbolo atual (entrada)
        action = get_action(currentState, currentSymbol)

        rows.append({
        "state-stack": stateStack.copyContent(),
        "simbol-stack": simbolStack.copyContent(),
        "input": cadeia[(pointer):],
        "action": action,
        })

        if action is None:
            raise Exception(f"erro sintático no estado {currentState} com o símbolo '{currentSymbol}'")

        if action.startswith('s'):  # Shift
            nextState = int(action[1:])  # Obtém o próximo estado
            stateStack.push(nextState)  # Empilha o próximo estado
            simbolStack.push(currentSymbol)  # Empilha o símbolo atual
            pointer += 1  # Avança na entrada

        elif action.startswith('r'):  # Reduce
            ruleNumber = int(action[1:])  # Obtém o número da regra
            rule = rules[ruleNumber]  # Obtém a regra de produção

            # Remove os símbolos da pilha
            for _ in rule.product:
                stateStack.pop()
                simbolStack.pop()

            # Adiciona o não-terminal da regra na pilha
            simbolStack.push(rule.head)

            # Move para o estado resultante da redução (GOTO)
            gotoState = get_action(stateStack.top(), rule.head)
            if gotoState is None:
                raise Exception(f"Erro sintático no GOTO para '{rule.head}' no estado {stateStack.top()}")

            stateStack.push(int(gotoState))  # Empilha o estado do GOTO

        elif action == 'acc':  # Accept
            # print("Cadeia aceita!")
            break

        

    # print("Parsing concluído com sucesso.")
    return rows