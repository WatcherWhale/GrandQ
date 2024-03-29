import chess
import numpy as np

from .State import State
from .Material import calculateMaterialValue
from .Mobility import totalMobility
from .Features import Features
from .PositionParser import scoreMatrix, getRowColumn


def utility(state: State, features: Features):
    value = 0

    # Checkmate
    if state.getBoard().is_checkmate():
        return 100
    # Stalemate
    elif state.getBoard().is_stalemate() or state.getBoard().is_insufficient_material() \
            or state.getBoard().is_seventyfive_moves() or state.getBoard().is_fivefold_repetition():
        return -30

    prevState, action = state.getPreviousState()

    # Castling
    if prevState.getBoard().is_castling(chess.Move.from_uci(action)):
        value += 2

    # In Check
    if state.getBoard().is_check():
        value += 2

    # Material Advantage
    value += calculateMaterialValue(state, state.getPlayer())
    value -= calculateMaterialValue(state, not state.getPlayer())

    # Mobility
    value += totalMobility(state.getBoard(), state.getPlayer())

    mirroredBoard = state.getBoard().copy()
    mirroredBoard.turn = not mirroredBoard.turn
    value -= totalMobility(mirroredBoard, not state.getPlayer())

    # Position Score matrix
    for piece_type in range(1, 7):
        for p in state.getBoard().pieces(piece_type, state.getPlayer()):
            m = np.asmatrix(scoreMatrix[piece_type - 1])
            flip = np.flipud(m)
            r, c = getRowColumn(p)
            value += flip[r, c]

        for p in state.getBoard().pieces(piece_type, not state.getPlayer()):
            m = np.asmatrix(scoreMatrix[piece_type - 1])
            r, c = getRowColumn(p)
            value -= m[r, c]

    return value + features.calculateFeatures(prevState, action)
