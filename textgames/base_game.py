class BaseGame:
    def generate_new_game(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def get_prompt(self) -> str:
        raise NotImplementedError()

    def validate(self, answer: str) -> bool:
        raise NotImplementedError()
