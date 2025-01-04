#%%
import os
os.environ.setdefault("GRADIO_SERVER_PORT", "1080")
# os.environ.setdefault("TEXTGAMES_SHOW_HIDDEN_LEVEL", "1")
os.environ.setdefault("TEXTGAMES_LOADGAME_DIR", "problemsets")
os.environ.setdefault("TEXTGAMES_LOADGAME_ID", "42")
os.environ.setdefault("TEXTGAMES_MOCKUSER", "")
favicon_path = "textgames-scrabble-black2-ss.png"

#%%
import gradio as gr
from textgames import GAME_NAMES, LEVELS
from play_helper import start_new_game, check_to_start_new_game, session_state_change_fn


#%%
def greet():
    return f"Welcome to TextGames! (Mock-User: {os.getenv('TEXTGAMES_MOCKUSER', '')})"


#%%
with gr.Blocks(title="TextGames") as demo:
    with gr.Row():
        with gr.Column(scale=4):
            m = gr.Markdown("Welcome to TextGames!")
        with gr.Column(scale=1):
            logout_btn = gr.Button("Logout", link="/logout", variant='huggingface', interactive=False)
    demo.load(greet, None, [m])

    cur_game_start = gr.BrowserState()
    session_state = gr.State(0)    # 0: menu selection, 1: game is ongoing, 2: game is solved.
    is_solved = gr.State(0)

    game_radio = gr.Radio(GAME_NAMES, label="Game", elem_id="radio-game-name")
    level_radio = gr.Radio(LEVELS, label="Level", elem_id="radio-level-name")
    new_game_btn = gr.Button("Start New Game")

    session_state.change(
        lambda s: session_state_change_fn(s, 2, 0, 1, 0),
        [session_state], [game_radio, level_radio, new_game_btn],
        js="(s) => {var el = document.getElementById('lintao-container'); if (el) el.remove(); return s;}",
    )
    new_game_btn.click(
        check_to_start_new_game, [game_radio, level_radio], [session_state],
    )

    render_toggle = gr.Checkbox(False, visible=False, interactive=False)
    session_state.change(lambda s, r: (not r if s in [0, 1] else r), [session_state, render_toggle], [render_toggle])

    @gr.render(inputs=[game_radio, level_radio, session_state], triggers=[render_toggle.change])
    def _start_new_game(game_name, level, _session_state):
        if _session_state in [1, 2]:
            start_new_game(game_name, level, session_state, is_solved)

demo.launch(favicon_path=favicon_path if os.path.exists(favicon_path) else None)


#%%


#%%


#%%


