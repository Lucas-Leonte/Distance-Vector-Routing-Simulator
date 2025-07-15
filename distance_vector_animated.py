import copy
import matplotlib.pyplot as plt
import networkx as nx

# ================================
# CLASSE NODO DELLA RETE
# ================================
class Nodo:
    def __init__(self, nome):
        """
        Inizializza un nodo con un nome identificativo e una lista dei suoi vicini.
        La tabella di routing sarà popolata in seguito.
        """
        self.nome = nome
        self.vicini = {}  # Mappa dei nodi vicini: {nome_nodo: costo collegamento}
        self.tabella_routing = {}  # Mappa destinazione -> (next_hop, distanza)

    def inizializza_tabella(self, tutti_i_nodi):
        """
        Inizializza la tabella di routing:
        - Distanza 0 verso sé stesso.
        - Distanza nota verso i vicini.
        - Distanza infinita verso tutti gli altri nodi (non ancora conosciuti).
        """
        self.tabella_routing = {}
        for nodo in tutti_i_nodi:
            if nodo == self.nome:
                self.tabella_routing[nodo] = (self.nome, 0)  # Verso se stesso: distanza 0
            elif nodo in self.vicini:
                self.tabella_routing[nodo] = (nodo, self.vicini[nodo])  # Verso vicino diretto: costo noto
            else:
                self.tabella_routing[nodo] = (None, float('inf'))  # Verso sconosciuti: distanza infinita

    def invia_vettore(self):
        """
        Prepara il proprio Distance Vector, ovvero un dizionario
        con la distanza minima nota verso ogni nodo.
        Questo è ciò che viene "inviato" ai vicini.
        """
        return {dest: dist for dest, (_, dist) in self.tabella_routing.items()}

    def aggiorna_tabella(self, mittente, vettore):
        """
        Aggiorna la propria tabella di routing in base al Distance Vector ricevuto
        da un nodo vicino (mittente).
        """
        modificato = False
        costo_verso_mittente = self.vicini[mittente]  # Costo per raggiungere chi ci ha mandato il vettore

        for destinazione, distanza_mittente in vettore.items():
            nuova_distanza = costo_verso_mittente + distanza_mittente  # Costo passando per il mittente
            _, distanza_corrente = self.tabella_routing[destinazione]

            # Se la nuova distanza è migliore, aggiorno la tabella
            if nuova_distanza < distanza_corrente:
                self.tabella_routing[destinazione] = (mittente, nuova_distanza)
                modificato = True  # Indico che ho aggiornato qualcosa
        return modificato

    def stampa_tabella(self):
        """
        Stampa in modo leggibile la tabella di routing di questo nodo.
        Ogni riga mostra la distanza minima nota per raggiungere ogni nodo.
        """
        print(f"\nTabella di routing del nodo {self.nome}:")
        print("Destinazione | Next Hop | Distanza")
        for destinazione, (next_hop, distanza) in self.tabella_routing.items():
            if distanza != float('inf'):
                print(f"{destinazione:^12} | {next_hop:^8} | {distanza:^8}")
            else:
                print(f"{destinazione:^12} | {'--':^8} | {'INF':^8}")

# ================================
# DISEGNO DEL GRAFO
# ================================
def disegna_grafo(nodi, G, pos, iterazione):
    plt.clf()
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1000, font_weight='bold')
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)

    for nome, nodo in nodi.items():
        info = ""
        for dest, (via, costo) in nodo.tabella_routing.items():
            if costo < float('inf'):
                info += f"{dest}:{via},{costo}  "
        x, y = pos[nome]
        plt.text(x, y - 0.15, info.strip(), fontsize=8, ha='center', bbox=dict(facecolor='white', alpha=0.6))

    plt.title(f"Distance Vector - Iterazione {iterazione}")
    plt.pause(1.5)  # Tempo di pausa tra le iterazioni

# ================================
# FUNZIONE DI SIMULAZIONE GLOBALE
# ================================
def simula(nodi, G, pos, max_iter=10):
    """
    Simula il funzionamento del Distance Vector Routing.
    Ogni nodo condivide il proprio vettore con i vicini,
    e aggiorna la tabella se trova percorsi più brevi.

    max_iter: numero massimo di iterazioni prima di fermarsi (per sicurezza)
    """
    tutti_i_nomi = list(nodi.keys())

    # Ogni nodo inizializza la propria tabella di routing
    for nodo in nodi.values():
        nodo.inizializza_tabella(tutti_i_nomi)

    for iterazione in range(max_iter):
        print(f"\n=== Iterazione {iterazione + 1} ===")
        aggiornamenti = 0  # Conta quanti aggiornamenti sono avvenuti

        # Creo una copia dei nodi per evitare problemi durante l'iterazione
        snapshot = copy.deepcopy(nodi)

        for nome, nodo in snapshot.items():
            vettore = nodo.invia_vettore()  # Ottengo il vettore da inviare ai vicini
            for vicino in nodo.vicini:
                aggiornato = nodi[vicino].aggiorna_tabella(nome, vettore)
                if aggiornato:
                    aggiornamenti += 1

        # Stampo la situazione aggiornata
        for nodo in nodi.values():
            nodo.stampa_tabella()

        # Visualizzo la rete graficamente ad ogni iterazione
        disegna_grafo(nodi, G, pos, iterazione + 1)

        # Se non ci sono stati aggiornamenti, la rete è "convergente"
        if aggiornamenti == 0:
            print("\nConvergenza raggiunta: le rotte non cambiano più.")
            break

# ================================
# SETUP DELLA RETE
# ================================
def main():
    # Creo i nodi della rete: possono rappresentare router o switch
    nodi = {
        'A': Nodo('A'),
        'B': Nodo('B'),
        'C': Nodo('C'),
        'D': Nodo('D')
    }

    # Definisco la topologia: chi è connesso con chi, e a quale costo
    nodi['A'].vicini = {'B': 1, 'C': 4}        # Nodo A è collegato a B (1) e C (4)
    nodi['B'].vicini = {'A': 1, 'C': 2, 'D': 7}
    nodi['C'].vicini = {'A': 4, 'B': 2, 'D': 1}
    nodi['D'].vicini = {'B': 7, 'C': 1}

    # Costruzione grafo visuale
    G = nx.Graph()
    for nome, nodo in nodi.items():
        G.add_node(nome)
        for vicino, costo in nodo.vicini.items():
            G.add_edge(nome, vicino, weight=costo)

    pos = nx.spring_layout(G, seed=42)

    plt.figure(figsize=(10, 6))
    simula(nodi, G, pos)
    plt.show()

# Punto di ingresso dello script
if __name__ == "__main__":
    main()