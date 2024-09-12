import time


class BaseGame:
    def __init__(self):
        self.start_timestamp = None
        self.chat_log = None
        self.attempt_timestamps = None
        self.is_solved = None

    @staticmethod
    def get_game_name() -> str:
        raise NotImplementedError()

    def _generate_new_game(self, *args, **kwargs) -> None:
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
