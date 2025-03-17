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
    #     lambda: [gr.update(interactive=False)]*2, None, [reset_sid_btn, new_game_btn]
    # ).then(
        lambda x: x, [reset_sid_checkbox], [reset_sid_checkbox],
        js="(x) => confirm('Only your best session is recorded on the leaderboard. Are you sure you want to start from the beginning? (cannot be undone)')"
    # ).then(
    #     lambda: [gr.update(interactive=True)]*2, None, [reset_sid_btn, new_game_btn]
    )

    def _resetting(confirmed, user):
        uid = user.get('email', None) if isinstance(user, dict) else None
        if not uid:
            gr.Warning("You need to log in first!")
        elif confirmed:
            user['sid'] = get_sid(uid, force_generate_sid=True)
            gr.Info("Successfully resets the game with new session. Enjoy the game! 💪")
        return user, False
    reset_sid_checkbox.change(
        lambda: [gr.update(interactive=False)]*3, None, [logout_btn, reset_sid_btn, new_game_btn]
    ).then(
        _resetting, [reset_sid_checkbox, user_state], [user_state, reset_sid_checkbox]
    ).then(
        check_played_game, [user_state, solved_games, solved_games_df], [solved_games, solved_games_df]
    ).then(
        lambda: [gr.update(interactive=True)]*3, None, [logout_btn, reset_sid_btn, new_game_btn]
    )


    @gr.render(inputs=[game_radio, level_radio, user_state, session_state, uid_state], triggers=[render_toggle.change])
    def _start_new_game(game_name, level, user, _session_state, _uid_state):
        if _session_state in [1, 2]:
            start_new_game(game_name, level, session_state, is_solved, solved_games, user=user, uid=_uid_state)

#%%
with (demo.route("Leaderboards", "/leaderboards") as demo_leaderboard):
    # gr.Markdown("Under Construction. Will be available soon.")
    def reload_leaderboard():
        ret_leaderboards = {}

        def add_dummies():
            return pd.DataFrame({
                'User': ['dummy'],
                'Solved': [sorted([g.split('\t', 1)[0] for g in GAME_NAMES])],
                'Attempts': [888],
                'Time': [8888.8888],
            })

        def sort_df(_cur_df):
            return _cur_df.sort_values(["Solved", "Attempts", "Time"], key=lambda c: {
                    "Solved": lambda s: -s.apply(len),
                }.get(c.name, lambda s: s)(c))

        if not os.path.exists(_leaderboards):
            for lv in ['1', '2', '3']:
                ret_leaderboards[lv] = add_dummies()

        else:
            datas = []
            with open(_leaderboards, "r", encoding="utf8") as f:
                for line in f:
                    datas.append(json.loads(line))
            concat = [{'Level': d['difficulty_level'], 'User': d['uid'], 'Session': d['sid'],
                       'Solved': d['game_name'].split('\t', 1)[0], 'Attempts': d['turns'], "Time": d['ed'] - d['st']
                       } for d in datas]
            df_leaderboards_all = pd.DataFrame(concat)

            def get_best(_cur_df):
                def _per_session(_df):
                    best = _df.groupby("Solved").apply(
                        lambda _df: _df.sort_values(["Attempts", "Time"]).iloc[0]
                    ).reset_index(drop=True)
                    ret = pd.DataFrame({
                        "Solved": [sorted(best.Solved.unique())], "Attempts": best.Attempts.sum(), "Time": best.Time.sum(),
                    })
                    return ret
                flat = _cur_df.groupby("Session").apply(_per_session)
                return sort_df(flat).iloc[0]

            for lv in ['1', '2', '3']:
                cur_df = df_leaderboards_all.loc[df_leaderboards_all.Level.eq(lv)].groupby("User").apply(get_best)
                cur_df = (
                    (sort_df(cur_df.reset_index()) if len(cur_df) else add_dummies()).rename({"Attempts": "Turns"}, axis=1)
                    .rename_axis("Rank").reset_index()
                )
                cur_df["Rank"] = list(range(1, len(cur_df)+1))
                ret_leaderboards[lv] = cur_df

        return ret_leaderboards

    df_leaderboards = {}

    # for lv, tab_name in [('1', "🚅 Easy"), ('2', "🚀 Medium"), ('3', "🛸 Hard")]:
    with gr.Tab("🚅 Easy") as tab1:
        lb_df_1 = gr.DataFrame(label="Rankings", col_count=(5, 'fixed'), interactive=False, show_search='filter')
        tab1.select(lambda: df_leaderboards['1'], None, [lb_df_1])
    with gr.Tab("🚀 Medium") as tab2:
        lb_df_2 = gr.DataFrame(label="Rankings", col_count=(5, 'fixed'), interactive=False, show_search='filter')
        tab2.select(lambda: df_leaderboards['2'], None, [lb_df_2])
    with gr.Tab("🛸 Hard") as tab3:
        lb_df_3 = gr.DataFrame(label="Rankings", col_count=(5, 'fixed'), interactive=False, show_search='filter')
        tab3.select(lambda: df_leaderboards['3'], None, [lb_df_3])

    def onload(progress=gr.Progress()):
        global df_leaderboards
        df_leaderboards = reload_leaderboard()
        return df_leaderboards['1']
    demo_leaderboard.load(onload, None, [lb_df_1])


#%%
# demo.launch()
demo.launch(
    favicon_path=favicon_path if os.path.exists(favicon_path) else None,
    show_api=False, enable_monitoring=False, pwa=False,
)


#%%

#%%


#%%


#%%


#%%


#%%
