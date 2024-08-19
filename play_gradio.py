#%%
import os
os.environ.setdefault("TEXTGAMES_SHOW_HIDDEN_LEVEL", "1")
os.environ.setdefault("GRADIO_SERVER_PORT", "1080")

#%%
import time
import gradio as gr
from play import GAME_IDS, GAME_NAMES, LEVEL_IDS, LEVELS, new_game


#%%
with (gr.Blocks() as demo):
    # input_text = gr.Textbox(label="input")
    game_radio = gr.Radio(GAME_NAMES,label="Game")
    level_radio = gr.Radio(LEVELS, label="Level")
    new_game_btn = gr.Button("Start New Game")

    cur_game_start = gr.State()
    new_game_btn.click(lambda: time.time(), None, cur_game_start)

    io_history = None

    def calc_time_elapsed(start_time, cur_text, is_solved):
        if not is_solved:
            return f"Time Elapsed (sec): {time.time() - start_time:8.1f}"
        else:
            return cur_text

    @gr.render(inputs=[game_radio, level_radio], triggers=[new_game_btn.click])
    def start_new_game(game_name, level):
        global io_history
        if game_name is None or level is None:
            raise gr.Error("please choose both Game & Level")
        cur_game_id = GAME_IDS[GAME_NAMES.index(game_name)]
        difficulty_level = LEVEL_IDS[LEVELS.index(level)]

        is_solved = gr.State(False)

        elapsed_text = gr.Textbox("N/A", label=f"{game_name}", info=f"{level}",)
        gr.Timer(.3).tick(calc_time_elapsed, [cur_game_start, elapsed_text, is_solved], [elapsed_text])

        cur_game = new_game(cur_game_id, difficulty_level)

        def add_msg(new_msg, prev_msg):
            user_input = '\n'.join(new_msg.split())
            solved, val_msg = cur_game.validate(user_input)
            response = ("Correct" if solved else "Bad") + " guess\n" + val_msg
            new_io_history = prev_msg + [f"Guess>\n{new_msg}", "Prompt>\n" + response]
            return (
                ("" if not solved else gr.Textbox("Thank you for playing!", interactive=False)),
                new_io_history, "\n\n".join(new_io_history), solved
            )

        io_history = gr.State(["Prompt>\n" + cur_game.get_prompt()])
        io_textbox = gr.Textbox("\n\n".join(io_history.value), label="Prompt>", interactive=False)
        textarea = gr.Textbox(label="Guess>", lines=5, info=f"(Shift + Enter to submit)")
        textarea.submit(add_msg, [textarea, io_history], [textarea, io_history, io_textbox, is_solved])


demo.launch()


#%%


#%%


#%%


