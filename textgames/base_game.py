import time
import pickle


class BaseGame:
    def __init__(self):
        self.exclude_states = None
        self.start_timestamp = None
        self.end_timestamp = None
        self.chat_log = None
        self.attempt_count = 0
        self.attempt_timestamps = None
        self.is_solved = None
        self.is_forfeited = None
        self.stats_filepath = None

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
        self.attempt_count = 0
        self.attempt_timestamps = []
        self.chat_log = []
        self.is_solved = False
        self.is_forfeited = False

    def attach_stats_output_(self, filepath):
        assert not self.stats_filepath
        self.stats_filepath = filepath

    def flush_stats_(self, user=None):
        if self.stats_filepath:
            with open(self.stats_filepath, mode='ab') as o:
                if user:
                    pickle.dump((time.time(), user), o)
                else:
                    pickle.dump((
                        time.time(),
                        self.attempt_count,
                        self.attempt_timestamps,
                        self.chat_log,
                        self.is_solved,
                        self.is_forfeited,
                    ), o)
            self.chat_log.clear()
            self.attempt_timestamps.clear()
        # won't flush if output filepath is unset

    def finish_stats_(self, forfeit: bool = False) -> None:
        assert not self.is_solved and not self.is_forfeited
        self.end_timestamp = time.time()
        if not forfeit:
            self.is_solved = True
        else:
            self.is_forfeited = True

    def generate_new_game(self, *args, **kwargs) -> None:
        self._generate_new_game(*args, **kwargs)
        self.init_stats_()

    def load_game(self, *args, **kwargs) -> None:
        self._load_game(*args, **kwargs)
        self.init_stats_()

    def get_prompt(self) -> str:
        prompt = self._get_prompt()
        self.chat_log.append((-2, prompt,))
        self.flush_stats_()
        return prompt

    def validate(self, answer: str) -> (bool, str):
        # print(self.start_timestamp, self.attempt_timestamps, self.is_solved, sep="\n", end="\n\n")
        self.attempt_count += 1
        self.attempt_timestamps.append(time.time())
        self.chat_log.append((-1, answer,))
        solved, val_msg = self._validate(answer)
        self.chat_log.append((solved, val_msg,))
        if solved:
            self.finish_stats_()
        self.flush_stats_()
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
        'start_timestamp', 'end_timestamp', 'chat_log', 'attempt_count', 'attempt_timestamps', 'is_solved',
        *(original_game.exclude_states or [])
    ]
    original_game_states = {k: v for k, v in vars(original_game).items() if k not in exclude_states}
    loaded_game_states = {k: v for k, v in vars(loaded_game).items() if k not in exclude_states}

    return (original_game_states == loaded_game_states) and (original_game.get_prompt() == loaded_game.get_prompt())
