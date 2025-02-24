from __future__ import annotations

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
from play_helper import css, declare_components, start_new_game, check_played_game, download_from_drive, upload_to_drive, _leaderboards
import pandas as pd
import gradio as gr
import random
import json
from textgames import GAME_NAMES


#%%
os.makedirs(os.getenv('TEXTGAMES_OUTPUT_DIR', '.'), exist_ok=True)


#%%
def generate_sid(fp):
    rand_int = random.randint(0, 1000)
    with open(fp, "w", encoding="utf8") as f:
        f.write(f"session_{rand_int:04}\n")
    upload_to_drive(fp, mime_type="text/plain", update=True)


#%%
def get_sid(uid, force_generate_sid=False):
    fp = f"{os.getenv('TEXTGAMES_OUTPUT_DIR')}/{uid}_sid.txt"
    if force_generate_sid:
        generate_sid(fp)
    if not os.path.exists(fp):
        download_from_drive(fp, mime_type="text/plain", compare_checksum=False)
    if not os.path.exists(fp):
        generate_sid(fp)
    with open(fp, "r", encoding="utf8") as f:
        sid = [_ for _ in f][-1]
    return sid.strip()


#%%
def greet(request: gr.OAuthProfile | None):
    user = {'email': os.getenv('TEXTGAMES_MOCKUSER', ''), 'name': ""}
    if request is not None:
        user = {'email': request.username, 'name': request.name, 'sid': get_sid(request.username)}
    return f"""
        Welcome to TextGames, {user['name'] or 'please login'}!
    """, user, user['email']


#%%
with gr.Blocks(title="TextGames", css=css, delete_cache=(3600, 3600)) as demo:
    ((m, logout_btn, solved_games_df, game_radio, level_radio, new_game_btn, render_toggle, reset_sid_btn),
     (session_state, is_solved, solved_games, user_state, uid_state),
     ) = declare_components(demo, greet, use_login_button=True)
    logout_btn.activate()

    reset_sid_checkbox = gr.Checkbox(False, visible=False, interactive=False)
    reset_sid_btn.click(
        lambda: [gr.update(interactive=False)]*2, None, [reset_sid_btn, new_game_btn]
    ).then(
        lambda x: x, [reset_sid_checkbox], [reset_sid_checkbox],
        js="(x) => confirm('Reset Progress? (cannot be undone)')"
    ).then(
        lambda: [gr.update(interactive=True)]*2, None, [reset_sid_btn, new_game_btn]
    )

    def _resetting(confirmed, user):
        uid = user.get('email', None) if isinstance(user, dict) else None
        if not uid:
            gr.Warning("You need to log in first!")
        elif confirmed:
            user['sid'] = get_sid(uid, force_generate_sid=True)
        return user, False
    reset_sid_checkbox.change(
        lambda: [gr.update(interactive=False)]*3, None, [logout_btn, reset_sid_btn, new_game_btn]
    ).then(
        _resetting, [reset_sid_checkbox, user_state], [user_state, reset_sid_checkbox]
    ).then(
        check_played_game, [solved_games, user_state], [solved_games, solved_games_df]
    ).then(
        lambda: [gr.update(interactive=True)]*3, None, [logout_btn, reset_sid_btn, new_game_btn]
    )


    @gr.render(inputs=[game_radio, level_radio, user_state, session_state, uid_state], triggers=[render_toggle.change])
    def _start_new_game(game_name, level, user, _session_state, _uid_state):
        if _session_state in [1, 2]:
            start_new_game(game_name, level, session_state, is_solved, solved_games, user=user, uid=_uid_state)

#%%
with demo.route("Leaderboards", "/leaderboard") as demo_leaderboard:
    gr.Markdown("Under Construction. Will be available soon.")
    leaderboards = []
    for tab in ["🚅 Easy", "🚀 Medium", "🛸 Hard"]:
        with gr.Tab(tab):
            leaderboards.append(gr.DataFrame(label="Rankings"))

    # if os.path.exists(_leaderboards):
    #     datas = []
    #     with open(_leaderboards, "r", encoding="utf8") as f:
    #         for line in f:
    #             datas.append(json.loads(line))
    #     concat = [{'Level': d['difficulty_level'], 'User': d['uid'], 'Game': d['game_name'].split('\t', 1)[0], 'Attempts': d['turns'],
    #                "Time": d['ed'] - d['st']} for d in datas]
    # else:
    def add_dummies():
        return pd.DataFrame({
            'User': ['dummy'],
            'Solved': [' '.join([g.split('\t', 1)[0] for g in GAME_NAMES])],
            'Attempts': [8],
            'Time': [7200.8],
        })
    for l in leaderboards:
        demo_leaderboard.load(add_dummies, None, [l])


#%%
# demo.launch()
demo.launch(
    favicon_path=favicon_path if os.path.exists(favicon_path) else None,
    show_api=False,
)


