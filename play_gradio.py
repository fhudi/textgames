#%%
import os
# os.environ.setdefault("GRADIO_SERVER_PORT", "1080")
# os.environ.setdefault("TEXTGAMES_SHOW_HIDDEN_LEVEL", "1")
os.environ.setdefault("TEXTGAMES_LOADGAME_DIR", "problemsets")
os.environ.setdefault("TEXTGAMES_LOADGAME_ID", "42")
os.environ.setdefault("TEXTGAMES_MOCKUSER", "")
os.environ.setdefault("TEXTGAMES_OUTPUT_DIR", "user_outputs")
favicon_path = "textgames-scrabble-black2-ss.png"

#%%
from play_helper import css, declare_components, start_new_game, download_from_drive
import pandas as pd
import gradio as gr


#%%
def greet():
    email = os.getenv('TEXTGAMES_MOCKUSER', '')
    _m = f"Welcome to TextGames!<br/>({'Mock-User: ' if email else 'no user'}{email})"
    if email:
        return _m, {'email': email, 'email_verified': "mockuser"}, email
    else:
        return _m, None, f"{int(time.time()*10):x}"


#%%
with gr.Blocks(title="TextGames", css=css, delete_cache=(3600, 3600)) as demo:
    ((m, logout_btn, solved_games_df, game_radio, level_radio, new_game_btn, render_toggle),
     (session_state, is_solved, solved_games, user_state, uid_state),
     ) = declare_components(demo, greet)

    @gr.render(inputs=[game_radio, level_radio, user_state, session_state, uid_state], triggers=[render_toggle.change])
    def _start_new_game(game_name, level, user, _session_state, _uid_state):
        if _session_state in [1, 2]:
            start_new_game(game_name, level, session_state, is_solved, solved_games, user=user, uid=_uid_state)

demo.launch(favicon_path=favicon_path if os.path.exists(favicon_path) else None)


#%%


#%%


#%%


