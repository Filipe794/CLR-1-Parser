from readTable import get_rows,rulesDict
from graphviz import Digraph

class TreeNode:
    def __init__(self, symbol):
        self.symbol = symbol
        self.children = [] # lista de filhos, uma regra de derivação pode gerar 1 ou mais simbolos

    def add_child(self, child):
        self.children.append(child)
    
    def get_last_child(self): # função que remove o ultimo filho do nó, vai ser usada pra construir a arvore
        if self.children:
            return self.children.pop()
        return None
    
    def get_children(self): # retorna a lista de filhos
        return self.children

    def generate_graphviz(self, graph=None, parent_id=None): # gera o png da arvore (está sendo tratada como grafo)
        if graph is None:
            graph = Digraph(format='png')
            graph.attr(rankdir='TB')  # Top to Bottom

        # ID único com base no símbolo e no endereço de memória
        node_id = f"{self.symbol}_{id(self)}"

        # adiciona o nó atual ao grafo
        graph.node(node_id, self.symbol)

        for child in self.children:
            child_id = f"{child.symbol}_{id(child)}"  
            graph.edge(node_id, child_id)  # Conecta o nó atual ao filho
            child.generate_graphviz(graph, node_id)

        return graph
    
def generate_parse_tree(rows, rulesDict):
    tree = TreeNode("root") # nó auxiliar, apenas pra ter por onde começar a adicionar
    
    for row in rows:
        action = row['action'] # recupera ação da linha atual da tabela
        current_input = row['input'] # entrada atual (token)
        
        if action.startswith('s'):  # Shift
            simbol = current_input[0]  # o primeiro token da entrada
            
            # cria uma folha para o símbolo
            node = TreeNode(simbol)
            tree.add_child(node)
            
            # avança na leitura da entrada
            row['input'].pop(0)
        
        elif action.startswith('r'):  # Reduce
            
            rule_num = int(action[1:])  # pegando o nmr da regra -> r6 vira 6
            rule = rulesDict[rule_num] # recuperando a regra no dicionario de Regras
            
            head = rule.head  # símbolo à esquerda da produção
            product = rule.product  # parte direita da produção
            
            # nó para o símbolo da cabeça da produção
            parent = TreeNode(head)
            
            children = []
            for _ in range(len(product)):
                # remove o ultimo filho do nó pai que está na arvore
                child_node = tree.get_last_child()
                
                # e adiciona no parent que está sendo criado agr
                children.append(child_node)
            
            # adiciona os filhos correspondentes aos símbolos da produção
            for child_node in reversed(children):
                parent.add_child(child_node)
    
            # A ordem da produção funciona de forma que
            # o último símbolo da produção será o primeiro nó filho a ser adicionado ao nó pai
            
            # se na lista de filhos do pai estiver [T * F]
            # quando remover, sem inverter, vai ficar [F * T]
            # por isso o reverse

            # Adiciona o resultado da produção de volta na árvore
            tree.add_child(parent)
            
        elif action == "acc":  # Aceitar
            break
    
    # Removendo o nó auxiliar Root da árvore
    root = tree.get_children()[0]
    root.symbol = root.symbol
    
    return root

entrada = "id*id+id*id"

rows = get_rows(entrada, rulesDict)
root = generate_parse_tree(rows, rulesDict)

graph = root.generate_graphviz()
# Salvando o grafo como um arquivo PNG
graph.render("graph_output", format="png", cleanup=True)