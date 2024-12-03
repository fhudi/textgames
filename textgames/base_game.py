import time


class BaseGame:
    def __init__(self):
        self.exclude_states = None
        self.start_timestamp = None
        self.chat_log = None
        self.attempt_timestamps = None
        self.is_solved = None

    @staticmethod
    def get_game_name() -> str:
        raise NotImplementedError()

    def _generate_new_game(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def _load_game(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def _get_prompt(self) -> str:
        raise NotImplementedError()

    def _validate(self, answer: str) -> (bool, str):
        raise NotImplementedError()

    def init_stats_(self):
        self.start_timestamp = time.time()
        self.chat_log = []
        self.attempt_timestamps = []
        self.is_solved = False

    def generate_new_game(self, *args, **kwargs) -> None:
        self._generate_new_game(*args, **kwargs)
        self.init_stats_()

    def load_game(self, *args, **kwargs) -> None:
        self._load_game(*args, **kwargs)
        self.init_stats_()

    def get_prompt(self) -> str:
        prompt = self._get_prompt()
        self.chat_log.append((-2, prompt,))
        return prompt

    def validate(self, answer: str) -> (bool, str):
        # print(self.start_timestamp, self.attempt_timestamps, self.is_solved, sep="\n", end="\n\n")
        self.chat_log.append((-1, answer,))
        self.attempt_timestamps.append(time.time())
        solved, val_msg = self._validate(answer)
        self.chat_log.append((solved, val_msg,))
        return solved, val_msg

    def is_game_reloadable(self) -> bool:
        return _is_game_reloadable(self)


def _is_game_reloadable(original_game: BaseGame) -> bool:
    loaded_game = original_game.__class__()
    try:
        loaded_game.load_game(original_game.get_prompt())
    except NotImplementedError:
        print("..... lhooooo: Load Game not implemented .....\n")
        return False
    exclude_states = [
        "possible_ans", "rules", "num_rules", "WORD_LIST", "MULTI_WORD_LIST", "multi_word", 'start_timestamp', 'chat_log', 'attempt_timestamps', 'is_solved',
        *(original_game.exclude_states or [])
    ]
    original_game_states = {k: v for k, v in vars(original_game).items() if k not in exclude_states}
    loaded_game_states = {k: v for k, v in vars(loaded_game).items() if k not in exclude_states}

    for k in original_game_states.keys():
        if isinstance(original_game_states[k], list):
            try:
                original_game_states[k].sort()
                loaded_game_states[k].sort()
            except:
                print("ignore the sort")
    return (original_game_states == loaded_game_states) and (original_game.get_prompt() == loaded_game.get_prompt())
