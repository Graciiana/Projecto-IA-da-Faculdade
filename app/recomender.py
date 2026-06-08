import time

from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

from app.database import (
    buscar_dados_para_treino,
    obter_itens_mais_populares
)


class MotorRecomendacao:

    def __init__(self):
        self.model_knn = NearestNeighbors(
            metric="cosine",
            algorithm="brute",
            n_neighbors=3,
            n_jobs=-1
        )

        self.user_item_matrix = None #guardará a matriz principal, bem elaborada, com colunas, linhas e valores
        self.features_matrix = None #guardará a matriz esparsa
        self.tempo_ultimo_treino = 0.0 #Tempo de treinamento do modelo


        #Treinando o modelo
    def treinar(self):
        inicio = time.time()

        def_ratings = buscar_dados_para_treino()

        if def_ratings.empty:
            return False

        self.user_item_matrix = def_ratings.pivot(
            index="item_id",
            columns="user_id",
            values="rating"
        ).fillna(0)

        self.features_matrix = csr_matrix(
            self.user_item_matrix.values
        )

        """fonece dados ao modelo para treinar o mesmo"""
        self.model_knn.fit(self.features_matrix)
        self.tempo_ultimo_treino = time.time() - inicio

        return True


    # Metodo para a recomendação
    def recomendar(
        self,
        item_id: int,
        n_recomendacoes: int = 3
    ):

        if (
            self.user_item_matrix is None
            or item_id not in self.user_item_matrix.index
        ):

            populares = obter_itens_mais_populares(
                n=n_recomendacoes
            )

            return {
                "estrategia":
                    "Cold Start (Itens Populares Globais)",

                "justificativa":
                    f"O item {item_id} não possui histórico suficiente no sistema.",

                "dados": populares
            }

        idx = self.user_item_matrix.index.get_loc(item_id)

        distancias, indices = self.model_knn.kneighbors(
            self.user_item_matrix.iloc[idx, :]
            .values.reshape(1, -1),

            n_neighbors=min(
                n_recomendacoes + 1,
                len(self.user_item_matrix)
            )
        )

        lista_recomendacoes = []

        for i in range(1, len(distancias.flatten())):

            vizinho_idx = indices.flatten()[i]

            item_recomendado_id = (
                self.user_item_matrix.index[vizinho_idx]
            )

            distancia_calculada = float(
                distancias.flatten()[i]
            )

            lista_recomendacoes.append({
                "item_id": int(item_recomendado_id),
                "distancia_cosseno":
                    round(distancia_calculada, 4)
            })

        return {
            "estrategia":
                "Filtragem Colaborativa baseada em Itens (K-NN)",

            "dados": lista_recomendacoes
        }