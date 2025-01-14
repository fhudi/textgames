import os

os.environ.setdefault("GRADIO_SERVER_PORT", "1080")
# os.environ.setdefault("TEXTGAMES_SHOW_HIDDEN_LEVEL", "1")
os.environ.setdefault("TEXTGAMES_LOADGAME_DIR", "problemsets")
os.environ.setdefault("TEXTGAMES_LOADGAME_ID", "42")
os.environ.setdefault("TEXTGAMES_MOCKUSER", "")
os.environ.setdefault("TEXTGAMES_OUTPUT_DIR", "user_outputs")
favicon_path = "textgames-scrabble-black2-ss.png"

#%%
from textgames import GAME_NAMES, LEVELS
from play_helper import declare_components, start_new_game, check_to_start_new_game,\
    session_state_change_fn, js_solved_games_df_and_remove_footers, js_remove_input_helper, solved_games_change_fn, check_played_game
from typing import Optional
import hashlib


#%%
css = """
#lintao-helper-btn {background: darkgreen;}
"""


#%%
import uvicorn
from fastapi import FastAPI, Depends, Request
from starlette.config import Config
from starlette.responses import RedirectResponse, FileResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError
import gradio as gr

app = FastAPI()

# Replace these with your own OAuth settings
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
SECRET_KEY = os.environ.get("SECRET_KEY", "a_very_secret_key")

# Set up OAuth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

_HASHER = (hashlib.blake2b, {"digest_size": 16, "key": SECRET_KEY.encode('utf-8')})


def _hash_msg(msg):
    m = _HASHER[0](**_HASHER[1])
    m.update(msg)
    return m.hexdigest()


# Dependency to get the current user
def get_user(request: Request) -> Optional[dict]:
    if user := request.session.get('user'):
        return user
    elif username := os.getenv("TEXTGAMES_MOCKUSER", ""):
        return {'name': username, 'email': username, 'email_verified': False}
    else:
        return


def get_username(request: Request):
    user = get_user(request)
    if user:
        return user['email']
    return None


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)


@app.get('/')
def public(user: str = Depends(get_username)):
    if user:
        return RedirectResponse(url='/TextGames')
    else:
        return RedirectResponse(url='/login')


@app.route('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    if os.getenv('TEXTGAMES_MOCKUSER', ''):
        os.environ['TEXTGAMES_MOCKUSER'] = ''
    return RedirectResponse(url='/')


@app.route('/do-login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    # If your app is running on https, you should ensure that the
    # `redirect_uri` is https, e.g. uncomment the following lines:
    #
    # from urllib.parse import urlparse, urlunparse
    # redirect_uri = urlunparse(urlparse(str(redirect_uri))._replace(scheme='https'))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.route('/auth')
async def auth(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse(url='/')
    request.session['user'] = dict(access_token)["userinfo"]
    return RedirectResponse(url='/')


def greet(request: gr.Request):
    user = get_user(request.request)
    # uid = ('1' if user['email_verified'] else '0') + f"{int(time.time()*10):x}_"[-8:] + _hash_msg(user['email'])
    uid = _hash_msg(user['email'].encode('utf-8'))
    return f"""
    Welcome to TextGames, {user['name']}!<br />
    <{user['email'].replace('@', '{at}')}> ({'' if user['email_verified'] else 'NON-'}verified email)
    """, user, uid


with gr.Blocks(title="TextGames") as login_demo:
    gr.Markdown("Welcome to TextGames!")
    # gr.Button("Login", link="/do-login")
    gr.Button("🚪\tLogin", link="/do-login", icon=None)

app = gr.mount_gradio_app(app, login_demo, path="/login")

with gr.Blocks(title="TextGames", css=css, delete_cache=(3600, 3600)) as demo:
    m, logout_btn, solved_games_df, game_radio, level_radio, new_game_btn, render_toggle = declare_components()

    # cur_game_start = gr.BrowserState()
    session_state = gr.State(0)    # 0: menu selection, 1: game is ongoing, 2: game is solved.
    is_solved = gr.State(0)
    solved_games = gr.State({g: [] for _, g in game_radio.choices})
    user_state = gr.State()
    uid_state = gr.State()

    session_state.change(
        lambda s: session_state_change_fn(s, 2, 0, 2, 0),
        [session_state], [game_radio, level_radio, new_game_btn, logout_btn], js=js_remove_input_helper,
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


app = gr.mount_gradio_app(app, demo, path="/TextGames", auth_dependency=get_username)

if __name__ == '__main__':
    uvicorn.run(app, port=int(os.environ.get("GRADIO_SERVER_PORT", "8080")))


#%%


#%%

