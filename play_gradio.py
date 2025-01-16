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
import time
import gradio as gr
from play_helper import declare_components, start_new_game, check_to_start_new_game,\
    session_state_change_fn, js_solved_games_df_and_remove_footers, js_remove_input_helper, solved_games_change_fn, check_played_game


#%%
def greet():
    email = os.getenv('TEXTGAMES_MOCKUSER', '')
    _m = f"Welcome to TextGames!<br/>({'Mock-User: ' if email else 'no user'}{email})"
    if email:
        return _m, {'email': email, 'email_verified': "mockuser"}, email
    else:
        return _m, None, f"{int(time.time()*10):x}"


#%%
with gr.Blocks(title="TextGames", delete_cache=(3600, 3600)) as demo:
    m, logout_btn, solved_games_df, game_radio, level_radio, new_game_btn, render_toggle = declare_components()
    logout_btn.interactive = False

    # cur_game_start = gr.BrowserState()
    session_state = gr.State(0)    # 0: menu selection, 1: game is ongoing, 2: game is solved.
    is_solved = gr.State(0)
    solved_games = gr.State({g: [] for _, g in game_radio.choices})
    user_state = gr.State(None)
    uid_state = gr.State()

    session_state.change(
        session_state_change_fn,
        [session_state], [game_radio, level_radio, new_game_btn], js=js_remove_input_helper,
    )
    new_game_btn.click(check_to_start_new_game, [game_radio, level_radio, user_state, uid_state], [session_state])
    solved_games.change(solved_games_change_fn, solved_games, solved_games_df)
    session_state.change(lambda s, r: (not r if s in [0, 1] else r), [session_state, render_toggle], [render_toggle])

    demo.load(
        greet, None, [m, user_state, uid_state], js=js_solved_games_df_and_remove_footers
    ).then(
        check_played_game, [solved_games, uid_state], [solved_games]
    )

    @gr.render(inputs=[game_radio, level_radio, user_state, session_state, uid_state], triggers=[render_toggle.change])
    def _start_new_game(game_name, level, user, _session_state, _uid_state):
        if _session_state in [1, 2]:
            start_new_game(game_name, level, session_state, is_solved, solved_games, user=user, uid=_uid_state)

demo.launch(favicon_path=favicon_path if os.path.exists(favicon_path) else None)


#%%


#%%


#%%


