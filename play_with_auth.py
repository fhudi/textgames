import os

# os.environ.setdefault("GRADIO_SERVER_PORT", "1080")
# os.environ.setdefault("TEXTGAMES_SHOW_HIDDEN_LEVEL", "1")
os.environ.setdefault("TEXTGAMES_LOADGAME_DIR", "problemsets")
os.environ.setdefault("TEXTGAMES_LOADGAME_ID", "42")
os.environ.setdefault("TEXTGAMES_MOCKUSER", "")
os.environ.setdefault("TEXTGAMES_OUTPUT_DIR", "user_outputs")
os.environ.setdefault("TEXTGAMES_HASH_USER", "")
favicon_path = "textgames-scrabble-black2-ss.png"

#%%
from play_helper import css, declare_components, start_new_game
from typing import Optional
import gradio as gr
import hashlib


#%%
import uvicorn
from fastapi import FastAPI, Depends, Request
from starlette.config import Config
from starlette.responses import RedirectResponse, FileResponse
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth, OAuthError

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
    if isinstance(msg, str):
        msg = msg.encode('utf-8')
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

    from urllib.parse import urlparse, urlunparse
    redirect_uri = urlunparse(urlparse(str(redirect_uri))._replace(scheme='https'))
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
    uid = _hash_msg(user['email']) if os.getenv("TEXTGAMES_HASH_USER", "") else user['email']
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
    ((m, logout_btn, solved_games_df, game_radio, level_radio, new_game_btn, render_toggle),
     (session_state, is_solved, solved_games, user_state, uid_state),
     ) = declare_components(demo, greet)

    @gr.render(inputs=[game_radio, level_radio, user_state, session_state, uid_state], triggers=[render_toggle.change])
    def _start_new_game(game_name, level, user, _session_state, _uid_state):
        if _session_state in [1, 2]:
            start_new_game(game_name, level, session_state, is_solved, solved_games, user=user, uid=_uid_state)


app = gr.mount_gradio_app(app, demo, path="/TextGames", auth_dependency=get_username)

if __name__ == '__main__':
    uvicorn.run(app,
                port=int(os.getenv("GRADIO_SERVER_PORT", "7860")),
                host=os.getenv("UVICORN_SERVER_HOST", "127.0.0.1"),
                ssl_keyfile=os.getenv("SSL_KEYFILE", None),
                ssl_certfile=os.getenv("SSL_CERTFILE", None),
                )


#%%


#%%

