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
fp_user_auth = f"{os.getenv('TEXTGAMES_OUTPUT_DIR', '.')}/textgames_userauth.tsv"
# fp_user_auth_id = "13RLyxV3ys5DGgRIJt5_tO-ILllJ1LDPGasobagZyVLU"
fp_user_auth_mime_type = "text/tab-separated-values"
os.makedirs(os.getenv('TEXTGAMES_OUTPUT_DIR', '.'), exist_ok=True)


#%%
def file_based_auth(username, password):
    if os.getenv('TEXTGAMES_MOCKUSER', ''):
        return True
    download_from_drive(fp_user_auth, mime_type=fp_user_auth_mime_type)
    df_auth = pd.read_csv(fp_user_auth, sep="\t").dropna(how="any")
    return len(df_auth.loc[(df_auth.EMAIL == username) & (df_auth.PASSWORD == password)]) > 0


#%%
def greet(request: gr.Request):
    email = os.getenv('TEXTGAMES_MOCKUSER', '')
    if email:
        user = {'email': email, 'name': "mockuser"}
    else:
        df_auth = pd.read_csv(fp_user_auth, sep="\t").dropna(how="any").drop_duplicates(subset=['EMAIL'])
        r = df_auth.loc[df_auth.EMAIL == request.username].iloc[0]
        user = {'email': r.EMAIL, 'name': r.NAME}
    return f"""
        Welcome to TextGames, {user['name']}!<br/><{user['email'].replace('@', '{at}')}>
    """, user, user['email']

    # return f"""
    #     Welcome to TextGames, {user['name']}!<br />
    #     <{user['email'].replace('@', '{at}')}> ({'' if user['email_verified'] else 'NON-'}verified email)
    # """, None, None


#%%
with gr.Blocks(title="TextGames", css=css, delete_cache=(3600, 3600)) as demo:
    ((m, logout_btn, solved_games_df, game_radio, level_radio, new_game_btn, render_toggle),
     (session_state, is_solved, solved_games, user_state, uid_state),
     ) = declare_components(demo, greet)

    @gr.render(inputs=[game_radio, level_radio, user_state, session_state, uid_state], triggers=[render_toggle.change])
    def _start_new_game(game_name, level, user, _session_state, _uid_state):
        if _session_state in [1, 2]:
            start_new_game(game_name, level, session_state, is_solved, solved_games, user=user, uid=_uid_state)

demo.launch(
    auth=file_based_auth,
    favicon_path=favicon_path if os.path.exists(favicon_path) else None,
    share=True,
    show_api=False,
)


#%%


#%%


#%%


