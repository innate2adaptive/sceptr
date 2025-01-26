"""
SCEPTR is a small, fast, and performant TCR representation model for alignment-free TCR analysis.
The root module provides easy access to SCEPTR through a functional API which uses the default model.
"""


from sceptr import variant
from sceptr.model import Sceptr, ResidueRepresentations
from numpy import ndarray
from pandas import DataFrame
from typing import Optional


__version__ = "1.1.0-post2"


_DEFAULT_MODEL: Optional[Sceptr] = None
_USE_HARDWARE_ACCELERATION = True


def calc_cdist_matrix(anchors: DataFrame, comparisons: DataFrame) -> ndarray:
    """
    Generate a cdist matrix between two collections of TCRs.

    Parameters
    ----------
    anchors : DataFrame
        DataFrame specifying the first (anchor) collection of input TCRs.
        It must be in the :ref:`prescribed format <data_format>`.

    comparisons : DataFrame
        DataFrame specifying the second (comparison) collection of input TCRs.
        It must be in the :ref:`prescribed format <data_format>`.

    Returns
    -------
    ndarray
        A 2D numpy ndarray representing a cdist matrix between TCRs from `anchors` and `comparisons`.
        The returned array will have shape :math:`(X, Y)` where :math:`X` is the number of TCRs in `anchors` and :math:`Y` is the number of TCRs in `comparisons`.
    """
    return _get_default_model().calc_cdist_matrix(anchors, comparisons)


def calc_pdist_vector(instances: DataFrame) -> ndarray:
    r"""
    Generate a pdist vector of distances between each pair of TCRs in the input data.

    Parameters
    ----------
    instances : DataFrame
        DataFrame specifying the input TCRs.
        It must be in the :ref:`prescribed format <data_format>`.

    Returns
    -------
    ndarray
        A 1D numpy ndarray representing a pdist vector of distances between each pair of TCRs in `instances`.
        The returned array will have shape :math:`(\frac{1}{2}N(N-1),)`, where :math:`N` is the number of TCRs in `instances`.
    """
    return _get_default_model().calc_pdist_vector(instances)


def calc_vector_representations(instances: DataFrame) -> ndarray:
    """
    Map TCRs to their corresponding vector representations.

    Parameters
    ----------
    instances : DataFrame
        DataFrame specifying the input TCRs.
        It must be in the :ref:`prescribed format <data_format>`.

    Returns
    -------
    ndarray
        A 2D numpy ndarray object where every row vector corresponds to a row in `instances`.
        The returned array will have shape :math:`(N, 64)` where :math:`N` is the number of TCRs in `instances`.
    """
    return _get_default_model().calc_vector_representations(instances)


def calc_residue_representations(instances: DataFrame) -> ResidueRepresentations:
    """
    Map each TCR to a set of amino acid residue-level representations.
    The residue-level representations are the output of the penultimate self-attention layer, as also used by the :py:func:`~sceptr.variant.average_pooling` variant when generating TCR receptor-level representations.

    Parameters
    ----------
    instances : DataFrame
        DataFrame specifying the input TCRs.
        It must be in the :ref:`prescribed format <data_format>`.

    Returns
    -------
    :py:class:`~sceptr.model.ResidueRepresentations`
        An array of representation vectors for each amino acid residue in the tokenised forms of the input TCRs.
        For details on how to interpret/use this output, please refer to the documentation for :py:class:`~sceptr.model.ResidueRepresentations`.
    """
    return _get_default_model().calc_residue_representations(instances)


def use_hardware_acceleration() -> None:
    """
    Instruct SCEPTR to detect and use available hardware acceleration, such as CUDA or MPS.
    
    While hardware acceleration is toggled on by default, it can be turned off manually by calling :py:func:`sceptr.ignore_hardware_acceleration`.
    This function allows you to turn the setting back on.

    .. note ::
        Toggling this setting will affect the behaviour of the :ref:`functional API <functional_api>` and any new :ref:`variants <model_variants>` instantiated after the fucntion call.
        However, any variants instantiated before the call will remain unaffected.
        To move model variant instances across devices, use :py:meth:'sceptr.model.Sceptr.use_hardware_acceleration'.
    """
    global _USE_HARDWARE_ACCELERATION
    _USE_HARDWARE_ACCELERATION = True

    if _DEFAULT_MODEL is not None:
        _DEFAULT_MODEL.use_hardware_acceleration()


def ignore_hardware_acceleration() -> None:
    """
    Instruct SCEPTR to ignore hardware acceleration options and only use the CPU.
    
    By default, SCEPTR will look for available hardware acceleration devices such as CUDA- or MPS-enabled GPUs and perform computations there.
    However, in some cases it may be favourable to explicitly keep models on the CPU (e.g. a CUDA-enabled GPU is available but does not have sufficient VRAM for your use case).
    This function is useful for such scenarios.
    This setting can be reversed using :py:func:`sceptr.use_hardware_acceleration`.

    .. note ::
        Toggling this setting will affect the behaviour of the :ref:`functional API <functional_api>` and any new :ref:`variants <model_variants>` instantiated after the fucntion call.
        However, any variants instantiated before the call will remain unaffected.
        To move model variant instances across devices, use :py:meth:'sceptr.model.Sceptr.ignore_hardware_acceleration'.
    """
    global _USE_HARDWARE_ACCELERATION
    _USE_HARDWARE_ACCELERATION = False

    if _DEFAULT_MODEL is not None:
        _DEFAULT_MODEL.ignore_hardware_acceleration()


def _get_default_model() -> Sceptr:
    global _DEFAULT_MODEL

    if _DEFAULT_MODEL is None:
        _DEFAULT_MODEL = variant.default()

    return _DEFAULT_MODEL
