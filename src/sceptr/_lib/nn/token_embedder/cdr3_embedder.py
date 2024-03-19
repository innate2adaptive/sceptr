import math
import torch
from torch import Tensor
from torch.nn import Embedding

from sceptr._lib.nn.data.tokeniser.token_indices import (
    DefaultTokenIndex,
    AminoAcidTokenIndex,
    Cdr3CompartmentIndex,
)
from sceptr._lib.nn.token_embedder.token_embedder import TokenEmbedder
from sceptr._lib.nn.token_embedder.simple_relative_position_embedding import (
    SimpleRelativePositionEmbedding,
)
from sceptr._lib.nn.token_embedder.sin_position_embedding import SinPositionEmbedding
from sceptr._lib.nn.token_embedder.one_hot_token_index_embedding import (
    OneHotTokenIndexEmbedding,
)


MAX_PLAUSIBLE_CDR_LENGTH = 100


class Cdr3Embedder(TokenEmbedder):
    def __init__(self, embedding_dim: int) -> None:
        super().__init__()

        self._embedding_dim = embedding_dim

        self.token_embedding = Embedding(
            num_embeddings=len(AminoAcidTokenIndex),
            embedding_dim=embedding_dim,
            padding_idx=DefaultTokenIndex.NULL,
        )
        self.position_embedding = SinPositionEmbedding(
            num_embeddings=MAX_PLAUSIBLE_CDR_LENGTH, embedding_dim=embedding_dim
        )
        self.compartment_embedding = Embedding(
            num_embeddings=len(Cdr3CompartmentIndex),
            embedding_dim=embedding_dim,
            padding_idx=DefaultTokenIndex.NULL,
        )

    def forward(self, tokenised_tcrs: Tensor) -> Tensor:
        token_component = self.token_embedding.forward(tokenised_tcrs[:, :, 0])
        position_component = self.position_embedding.forward(tokenised_tcrs[:, :, 1])
        compartment_component = self.compartment_embedding.forward(
            tokenised_tcrs[:, :, 3]
        )

        all_components_summed = (
            token_component + position_component + compartment_component
        )

        return all_components_summed * math.sqrt(self._embedding_dim)


class Cdr3EmbedderWithRelativePositions(TokenEmbedder):
    def __init__(self, embedding_dim: int) -> None:
        super().__init__()

        self._embedding_dim = embedding_dim

        self._token_embedding = Embedding(
            num_embeddings=len(AminoAcidTokenIndex),
            embedding_dim=embedding_dim,
            padding_idx=DefaultTokenIndex.NULL,
        )
        self._position_embedding = SimpleRelativePositionEmbedding()
        self._compartment_embedding = OneHotTokenIndexEmbedding(Cdr3CompartmentIndex)

    def forward(self, tokenised_tcrs: Tensor) -> Tensor:
        token_component = self._token_embedding.forward(tokenised_tcrs[:, :, 0])
        position_component = self._position_embedding.forward(tokenised_tcrs[:, :, 1:3])
        compartment_component = self._compartment_embedding.forward(
            tokenised_tcrs[:, :, 3]
        )
        all_components_stacked = torch.concatenate(
            [token_component, position_component, compartment_component], dim=-1
        )
        return all_components_stacked * math.sqrt(self._embedding_dim)
