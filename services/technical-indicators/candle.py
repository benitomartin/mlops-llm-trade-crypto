from config import config
from loguru import logger
from quixstreams import State

MAX_CANDLES_IN_STATE = config.max_candles_in_state


def update_candles(candle: dict, state: State) -> dict:
    # Get the list of candles from our state
    candles = state.get('candles', default=[])  # We have a list of candles in the state

    # If the state is empty, we just append the latest candle to the list
    if not candles:
        candles.append(candle)

    elif same_window(candle, candles[-1]):
        # If the latest candle is in the same window as the previous one, we update/replace the last candle
        candles[-1] = candle
    else:
        # If the latest candle is in a new window, we append it to the list
        candles.append(candle)

    # If the total number of candles in the state is greater than the maximum number of
    # candles we want to keep, we remove the oldest candle from the list
    if len(candles) > MAX_CANDLES_IN_STATE:
        candles.pop(0)

    # TODO: we should check the candles have no missing windows
    # This can happen for low volume pairs. In this case, we could interpolate the missing windows

    logger.debug(f'Number of candles in state for {candle["pair"]}: {len(candles)}')

    # Update the state with the new list of candles
    state.set('candles', candles)

    return candle


def same_window(candle_1: dict, candle_2: dict) -> bool:
    """
    Check if the current candle is in the same window as the last candle
    Args:
        candle (dict): The current candle
        last_candle (dict): The last candle in the list
    Returns:
        True (bool): If the current candle is in the same window as the last candle, False otherwise
    """
    return (
        candle_1['window_start_ms'] == candle_2['window_start_ms']
        and candle_1['window_end_ms'] == candle_2['window_end_ms']
        and candle_1['pair'] == candle_2['pair']
    )
