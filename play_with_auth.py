import os

os.environ.setdefault("GRADIO_SERVER_PORT", "1080")
# os.environ.setdefault("TEXTGAMES_SHOW_HIDDEN_LEVEL", "1")
os.environ.setdefault("TEXTGAMES_LOADGAME_DIR", "problemsets")
os.environ.setdefault("TEXTGAMES_LOADGAME_ID", "42")
os.environ.setdefault("TEXTGAMES_MOCKUSER", "")
favicon_path = "textgames-scrabble-black2-ss.png"

#%%
from textgames import GAME_IDS, GAME_NAMES, LEVEL_IDS, LEVELS, new_game
from play_gradio import start_new_game
from typing import Optional


#%%
import uvicorn
from fastapi import FastAPI, Depends, Request
from starlette.config import Config
from starlette.responses import RedirectResponse
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


@app.get('/')
def public(user: str = Depends(get_username)):
    if user:
        return RedirectResponse(url='/main-demo')
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
    return f"""
    Welcome to TextGames, {user['name']}!<br />
    <<{user['email']}>> ({'' if user['email_verified'] else 'NON-'}verified email)
    """, user


with gr.Blocks(title="TextGames") as login_demo:
    gr.Markdown("Welcome to TextGames!")
    # gr.Button("Login", link="/do-login")
    gr.LoginButton("Login", link="/do-login")

app = gr.mount_gradio_app(app, login_demo, path="/login")

with gr.Blocks(title="TextGames") as main_demo:
    m = gr.Markdown("Welcome to TextGames!")
    user_state = gr.State()
    main_demo.load(greet, None, [m, user_state])

    gr.Button("Logout", link="/logout")

    game_radio = gr.Radio(GAME_NAMES, label="Game", elem_id="radio-game-name")
    level_radio = gr.Radio(LEVELS, label="Level", elem_id="radio-level-name")
    new_game_btn = gr.Button("Start Game")
    new_game_btn.click(js="() => {var el = document.getElementById('lintao-container'); if (el) el.remove();}")
    io_history = None

    @gr.render(inputs=[game_radio, level_radio, user_state], triggers=[new_game_btn.click])
    def _start_new_game(game_name, level, user):
        start_new_game(game_name, level, user)


app = gr.mount_gradio_app(app, main_demo, path="/main-demo", auth_dependency=get_username)

if __name__ == '__main__':
    uvicorn.run(app, port=int(os.environ.get("GRADIO_SERVER_PORT", "8080")))
