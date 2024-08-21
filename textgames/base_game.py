class BaseGame:
    @staticmethod
    def get_game_name() -> str:
        raise NotImplementedError()

    def generate_new_game(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def get_prompt(self) -> str:
        raise NotImplementedError()

    def validate(self, answer: str) -> (bool, str):
        raise NotImplementedError()
