# %%
import os
import time
import pandas as pd
import gradio as gr
import hashlib
from io import BytesIO

from textgames import GAME_NAMES, LEVEL_IDS, LEVELS, new_game, preload_game, game_filename
from textgames.islands.islands import Islands
from textgames.sudoku.sudoku import Sudoku
from textgames.crossword_arranger.crossword_arranger import CrosswordArrangerGame
from textgames.ordering_text.ordering_text import OrderingTextGame


# %%
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


# %%
def declare_components(demo, greet):
    with gr.Row():
        with gr.Column(scale=1):
            m = gr.Markdown("Welcome to TextGames!", elem_id="md-greeting")
            logout_btn = gr.Button("Logout", link="/logout", variant='huggingface', size='sm', elem_id="btn-logout")
        with gr.Column(scale=2):
            solved_games_df = gr.DataFrame(headers=[g.split('\t', 1)[0] for g in GAME_NAMES], label="Finished Games",
                                           interactive=False, elem_id="df-solved-games")
    game_radio = gr.Radio(GAME_NAMES, label="Game", elem_id="radio-game-name")
    level_radio = gr.Radio(LEVELS, label="Level", elem_id="radio-level-name")
    new_game_btn = gr.Button("Start Game", elem_id="btn-start-game")
    render_toggle = gr.Checkbox(False, visible=False, interactive=False)

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
        lambda: gr.update(interactive=False), None, [new_game_btn],
    ).then(
        check_played_game, [solved_games, uid_state], [solved_games, solved_games_df]
    ).then(
        lambda: gr.update(interactive=True), None, [new_game_btn],
    )

    return (
        (m, logout_btn, solved_games_df, game_radio, level_radio, new_game_btn, render_toggle),
        (session_state, is_solved, solved_games, user_state, uid_state),
    )


# %%
_cksm_methods, _cksm_methods_str = (
    [hashlib.md5, hashlib.sha1], "md5Checksum, sha1Checksum",
    # [hashlib.md5, hashlib.sha1, hashlib.sha256], "md5Checksum, sha1Checksum, sha256Checksum",
)
_folder_id = "1qStKuVerAQPsXagngfzlNg8PdAR5hupA"
_creds_dict = {
  "type": "service_account",
  "project_id": os.getenv("GOOGLE_AUTH_CREDS_PROJECT_ID", ""),
  "private_key_id": os.getenv("GOOGLE_AUTH_CREDS_PRIVATE_KEY_ID", ""),
  "private_key": f"-----BEGIN PRIVATE KEY-----\n{os.getenv('GOOGLE_AUTH_CREDS_PRIVATE_KEY', '')}\n-----END PRIVATE KEY-----".replace("\\n", "\n"),
  "client_email": os.getenv("GOOGLE_AUTH_CREDS_CLIENT_EMAIL", ""),
  "client_id": os.getenv("GOOGLE_AUTH_CREDS_CLIENT_ID", ""),
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": os.getenv("GOOGLE_AUTH_CREDS_CLIENT_X509_CERT_URL", ""),
  "universe_domain": "googleapis.com"
}
_creds, _ = google.auth.load_credentials_from_dict(_creds_dict)
_service = build("drive", "v3", credentials=_creds)
_files = _service.files()


#%%
css = """
#lintao-helper-btn {background: darkgreen; color: white;}
.lintao-cell-highlight {background: var(--border-color-primary);}
//.lintao-border {border-style: solid; border-color: var(--body-text-color-subdued);}
"""


# %%
js_remove_input_helper = """(s) => {
        var el = document.getElementById('lintao-container');
        if (el) el.remove();
        return s;
    }"""

# %%
js_solved_games_df_and_remove_footers = """() => {
        var solvedGamesDf = document.getElementById("df-solved-games");
        var tables = solvedGamesDf.getElementsByTagName("table");
        for (let i = 0; i < tables.length; ++i) {
            tables[i].style.overflowY = "clip";
            tables[i].style.overflowX = "auto";
        }
        var footers = document.getElementsByTagName("footer");
        for (let i = 0; i < footers.length; ++i) {
            // footers[i].style.visibility = 'hidden';
            footers[i].remove();
        }
    }"""


# %%
js_island = """
function island() {{
    const grid_N = {N},
          grid_px = 40;

    const container = document.createElement('div');
    container.style.display = 'grid';
    container.style.gridTemplateColumns = container.style.gridTemplateRows = `repeat(${{grid_N}}, ${{grid_px}}px)`;
    container.style.gap = '1px';
    container.style.border = '2px solid';
    container.style.width = 'max-content';
    container.style.margin = '5px 0px 5px 40px';
    container.style.padding = '1px';
    container.id = 'lintao-container';

    for (let i = 0; i < grid_N; ++i) {{
        for (let j = 0; j < grid_N; ++j) {{
            const cell = document.createElement('div');
            cell.textContent = '.';
            cell.style.width = cell.style.height = `${{grid_px}}px`;
            cell.style.display = 'flex';
            cell.style.alignItems = 'center';
            cell.style.justifyContent = 'center';
            cell.style.fontSize = `${{grid_px/2}}px`;
            cell.style.border = '1px solid var(--body-text-color-subdued)';
            cell.style.cursor = 'pointer';
            cell.id = `lintao-cell-${{i}}-${{j}}`;

            // Toggle between '#', 'o', and '.'
            cell.addEventListener('click', () => {{
                if (cell.textContent === '.') {{
                    cell.textContent = '#';
                }} else if (cell.textContent === '#') {{
                    cell.textContent = 'o';
                }} else if (cell.textContent === 'o') {{
                    cell.textContent = '.';
                }} else {{
                    alert(`The clicked cell has unknown value of '${{cell.textContent}}'.`)
                }}
            }});

            container.appendChild(cell);
        }}
    }}    
    // return container;

    // var gradioContainer = document.querySelector('.gradio-container');
    // gradioContainer.insertBefore(container, gradioContainer.firstChild);

    var submitRow = document.getElementById("lintao-submit-row");
    submitRow.parentElement.insertBefore(container, submitRow);
}}
"""

js_island_submit = """
function island_submit(textarea, io_history) {{
    const container = document.getElementById("lintao-container")
    if (container === null) return [textarea, io_history];
    const grid_N = {N};
    var ret = "";
    for (let i = 0; i < grid_N; ++i) {{
        if (i > 0) ret += '\\n';
        for (let j = 0; j < grid_N; ++j) {{
            ret += document.getElementById(`lintao-cell-${{i}}-${{j}}`).textContent;
        }}
    }}
    return [ret, io_history];
}}
"""


# %%
js_sudoku = """
function sudoku() {{
    const N = {N};
    const grid_N = N*N,
          grid_px = 50,
          border_px = 2;
    const mat = {mat};

    let is_numeric_sudoku = false;
    for (let i = 0; i < grid_N; ++i) {{
        for (let j = 0; j < grid_N; ++j) {{
            if (/^\\d$/.test(mat[i][j])) {{
                is_numeric_sudoku = true;
                break;
            }}
        }}
    }}

    const container = document.createElement('div');
    container.style.display = 'grid';
    container.style.gridTemplateColumns = container.style.gridTemplateRows = `repeat(${{grid_N}}, ${{grid_px}}px)`;
    container.style.border = `${{border_px}}px solid`;
    container.style.width = 'max-content';
    container.style.margin = '5px 0px 5px 40px';
    container.style.padding = '0px';
    container.id = 'lintao-container';

    // Generate the grid
    const highlightClass = 'lintao-cell-highlight';
    for (let i = 0; i < grid_N; ++i) {{
        for (let j = 0; j < grid_N; ++j) {{
            const cell = document.createElement('div');
            cell.type = 'text';
            cell.maxLength = 1;
            cell.style.width = cell.style.height = `${{grid_px}}px`;
            cell.style.display = 'flex';
            cell.style.alignItems = 'center';
            cell.style.justifyContent = 'center';
            cell.style.textAlign = 'center';
            cell.style.fontSize = `${{grid_px/2}}px`;
            cell.style.border = '1px solid var(--body-text-color-subdued)';
            cell.style.margin = '0px';
            //cell.style.outline = 'none';
            //cell.style.color = 'var(--body-text-color)';
            //cell.style.backgroundColor = 'black';
            cell.id = `lintao-cell-${{i}}-${{j}}`;

            if (mat[i][j] != '_') {{
                cell.textContent = mat[i][j];
                cell.style.color = 'var(--block-title-text-color)';
                cell.disabled = true;
            }} else {{
                cell.style.cursor = 'pointer';
                cell.contentEditable = "true";
            }}


            if (j % N === 0) cell.style.borderLeft = `${{border_px}}px solid var(--body-text-color)`;
            if (j % N === (N-1)) cell.style.borderRight = `${{border_px}}px solid var(--body-text-color)`;
            if (i % N === 0) cell.style.borderTop = `${{border_px}}px solid var(--body-text-color)`;
            if (i % N === (N-1)) cell.style.borderBottom = `${{border_px}}px solid var(--body-text-color)`;

            // Allow only numbers 1-9 or A-I
            cell.addEventListener('input', (e) => {{
                if ((N === 2  &&  (!(is_numeric_sudoku?/^[1-4]$/:/^[A-Da-d]$/).test(e.target.textContent))) || 
                    (N === 3  &&  (!(is_numeric_sudoku?/^[1-9]$/:/^[A-Ia-i]$/).test(e.target.textContent)))) {{
                    e.target.textContent = '';
                }}
                e.target.textContent = e.target.textContent.toUpperCase();
            }});

            container.appendChild(cell);
        }}
    }}

    container.addEventListener('focusin', (e) => {{
        const index = Array.from(container.children).indexOf(e.target);
        if (index === -1) return;

        const row = Math.floor(index / grid_N);
        const col = index % grid_N;

        for (let i = 0; i < grid_N * grid_N; ++i) {{
            const cell = container.children[i];
            const currentRow = Math.floor(i / grid_N);
            const currentCol = i % grid_N;

            if (currentRow === row || currentCol === col || (Math.floor(currentRow / N) === Math.floor(row / N) && Math.floor(currentCol / N) === Math.floor(col / N))) {{
                cell.classList.add(highlightClass);
            }} else {{
                cell.classList.remove(highlightClass);
            }}
        }}
    }});

    container.addEventListener('focusout', () => {{
        for (let i = 0; i < grid_N * grid_N; i++) {{
            container.children[i].classList.remove(highlightClass);
        }}
    }});

    var submitRow = document.getElementById("lintao-submit-row");
    submitRow.parentElement.insertBefore(container, submitRow);
}}
"""

js_sudoku_submit = """
function sudoku_submit(textarea, io_history) {{
    const container = document.getElementById("lintao-container")
    if (container === null) return [textarea, io_history];
    const N = {N};
    const grid_N = N*N;
    var ret = "";
    for (let i = 0; i < grid_N; ++i) {{
        if (i > 0) ret += '\\n';
        for (let j = 0; j < grid_N; ++j) {{
            ret += document.getElementById(`lintao-cell-${{i}}-${{j}}`).textContent;
        }}
    }}
    return [ret, io_history];
}}
"""


# %%
js_crossword = """
function crossword() {{
    const grid_N = {N},
          grid_px = 50;

    const container = document.createElement('div');
    container.style.display = 'grid';
    container.style.gridTemplateColumns = container.style.gridTemplateRows = `repeat(${{grid_N}}, ${{grid_px}}px)`;
    container.style.gap = '1px';
    container.style.border = '2px solid';
    container.style.width = 'max-content';
    container.style.margin = '5px 0px 5px 40px';
    container.style.padding = '1px';
    container.id = 'lintao-container';

    // Generate the grid
    for (let i = 0; i < grid_N; ++i) {{
        for (let j = 0; j < grid_N; ++j) {{
            const cell = document.createElement('input');
            //cell.textContent = '';
            cell.type = 'text';
            cell.maxLength = 1;
            cell.style.width = cell.style.height = `${{grid_px}}px`;
            cell.style.display = 'flex';
            cell.style.alignItems = 'center';
            cell.style.justifyContent = 'center';
            cell.style.textAlign = 'center';
            cell.style.fontSize = `${{grid_px/2}}px`;
            cell.style.border = '1px solid var(--body-text-color-subdued)';
            cell.style.backgroundColor = 'var(--body-background-fill)';
            cell.style.cursor = 'pointer';
            cell.id = `lintao-cell-${{i}}-${{j}}`;

            // Allow only a-z
            cell.addEventListener('input', (e) => {{
                if (!/^[a-z]$/.test(e.target.value)) {{
                    e.target.value = '';
                }}
            }});

            container.appendChild(cell);
        }}
    }}

    var submitRow = document.getElementById("lintao-submit-row");
    submitRow.parentElement.insertBefore(container, submitRow);
}}
"""

js_crossword_submit = """
function crossword_submit(textarea, io_history) {{
    const container = document.getElementById("lintao-container")
    if (container === null) return [textarea, io_history];
    const grid_N = {N};
    var ret = "";
    for (let i = 0; i < grid_N; ++i) {{
        if (i > 0) ret += '\\n';
        for (let j = 0; j < grid_N; ++j) {{
            ret += document.getElementById(`lintao-cell-${{i}}-${{j}}`).value;
        }}
    }}
    return [ret, io_history];
}}
"""


# %%
js_ordering = """
function ordering() {{          
    const listContainer = document.createElement('ul');
    listContainer.style.listStyle = 'none';
    listContainer.style.padding = '0';
    listContainer.style.width = '20em';
    listContainer.style.border = '2px solid';
    listContainer.style.margin = '5px 0px 5px 40px';
    listContainer.id = 'lintao-container';

    document.body.appendChild(listContainer);

    const items = {items};

    items.forEach((itemText, index) => {{
        const listItem = document.createElement('li');
        listItem.textContent = itemText;
        listItem.draggable = true;
        listItem.style.padding = '10px';
        listItem.style.border = '1px solid';
        listItem.style.margin = '3px';
        //listItem.style.backgroundColor = 'var(--body-background-fill)';
        listItem.style.cursor = 'grab';
        listItem.id = `lintao-item-${{index}}`;

        // Drag and drop events
        listItem.addEventListener('dragstart', (e) => {{
            const draggedIndex = Array.from(listContainer.children).indexOf(listItem);
            e.dataTransfer.setData('text/plain', draggedIndex);
            listItem.style.backgroundColor = 'var(--block-background-fill)';
        }});

        listItem.addEventListener('dragover', (e) => {{
            e.preventDefault();
            listItem.style.backgroundColor = 'var(--border-color-primary)';
        }});

        listItem.addEventListener('dragleave', () => {{
            listItem.style.backgroundColor = 'var(--body-background-fill)';
        }});

        listItem.addEventListener('drop', (e) => {{
            e.preventDefault();
            const draggedIndex = e.dataTransfer.getData('text/plain');
            const draggedItem = listContainer.children[draggedIndex];
            const targetIndex = Array.from(listContainer.children).indexOf(listItem);
            console.log(draggedIndex, draggedItem, targetIndex);

            if (draggedIndex !== targetIndex) {{
                listContainer.insertBefore(draggedItem, targetIndex > draggedIndex ? listItem.nextSibling : listItem);
            }}

            listItem.style.backgroundColor = 'var(--body-background-fill)';
        }});

        listItem.addEventListener('dragend', () => {{
            listItem.style.backgroundColor = 'var(--body-background-fill)';
        }});

        listContainer.appendChild(listItem);
    }});

    var submitRow = document.getElementById("lintao-submit-row");
    submitRow.parentElement.insertBefore(listContainer, submitRow);
}}
"""

js_ordering_submit = """
function ordering_submit(textarea, io_history) {{
    const container = document.getElementById("lintao-container")
    if (container === null) return [textarea, io_history];
    var ret = "";
    container.childNodes.forEach(
        (c, i) => {{
            if (i>0) ret += '\\n';
            ret += c.textContent;
        }}
    )
    return [ret, io_history];
}}
"""


# %%
def _calc_time_elapsed(start_time, cur_text, is_solved):
    if not is_solved:
        return f"Time Elapsed (sec): {time.time() - start_time:8.1f}"
    else:
        return cur_text


# %%
def _get_file_output(game_name, level_id, fn_prefix):
    fd = os.getenv('TEXTGAMES_OUTPUT_DIR', '.')
    os.makedirs(fd, exist_ok=True)
    return f"{fd}/{fn_prefix}_-_{game_filename(game_name)}_{level_id}.pkl"


# %%
def _is_checksum_same(fp_out, matches=None, mime_type="application/octet-stream"):
    if matches is None:
        matches = _files.list(
            q=f"'{_folder_id}' in parents and mimeType='{mime_type}' and name = '{fp_out.rsplit('/', 1)[-1]}'",
            fields=f"files(name, id, {_cksm_methods_str})",
        ).execute()['files']
    if not os.path.exists(fp_out):
        return None, None, matches
    with open(fp_out, "rb") as o:
        _local = BytesIO(o.read()).getvalue()
    _local_hash = [m(_local).hexdigest() for m in _cksm_methods]
    for i, match in enumerate(matches):
        if all(a == b for a, b in zip(_local_hash, [match[k] for k in _cksm_methods_str.split(", ")])):
            return True, i, matches
    return False, -1, matches


# %%
def upload_to_drive(fp_out, matches=None, mime_type="application/octet-stream", compare_checksum=True):
    if compare_checksum:
        same_checksum, _, _ = _is_checksum_same(fp_out, matches, mime_type)
        # same_checksum, _, _ = _is_checksum_same(
        #     fp_out, **{k: v for k, v in [('matches', matches), ('mime_type', mime_type)] if v})
        if same_checksum:
            return
    fn = fp_out.rsplit("/", 1)[-1]
    file_metadata = {"name": fn, "parents": [_folder_id]}
    media = MediaFileUpload(fp_out)
    try:
        _files.create(body=file_metadata, media_body=media).execute()
    except HttpError as error:
        msg = f"Failed to upload the file, error: {error}"
        print(msg)
        gr.Error(msg)


# %%
def download_from_drive(fp_out, matches=None, mime_type="application/octet-stream", compare_checksum=True):
    if compare_checksum and os.path.exists(fp_out):
        same_checksum, i, matches = _is_checksum_same(fp_out, matches, mime_type)
        if same_checksum:
            return
    if matches is None:
        _, _, matches = _is_checksum_same(fp_out, matches, mime_type)
    if len(matches) == 0:
        return
    else:
        if len(matches) > 1:
            gr.Warning(f"Multiple matches found! {fp_out.rsplit('/', 1)[-1].split('_-_', 1)[-1]}")
        b_io, request = BytesIO(), _files.get_media(fileId=matches[0]['id'])
        downloader = MediaIoBaseDownload(b_io, request)
        if os.path.exists(fp_out):
            print(f"Deleting and re-download... ({fp_out})")
            os.remove(fp_out)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            with open(fp_out, "ab") as o:
                o.write(b_io.getvalue())


# %%
def start_new_game(game_name, level, session_state_component, is_solved_component, solved_games_component,
                   user=None, show_timer=False, uid=None):
    # cur_game_id = GAME_IDS[GAME_NAMES.index(game_name)]
    difficulty_level = LEVEL_IDS[LEVELS.index(level)]

    # if show_timer:
    #     elapsed_text = gr.Textbox("N/A", label=f"{game_name}", info=f"{level}", )
    #     gr.Timer(.3).tick(_calc_time_elapsed, [cur_game_start, elapsed_text, is_solved_component], [elapsed_text])

    fp_out = _get_file_output(game_name, difficulty_level, uid)
    cur_game = (
        new_game(game_name, difficulty_level)
        if user is None else
        preload_game(game_name, difficulty_level, user)
    )
    cur_game.attach_stats_output_(fp_out)
    cur_game.flush_stats_(user_info_to_flush=user)

    def add_msg(new_msg, prev_msg):
        if len(new_msg) > 200:
            new_msg = new_msg[:200]
            gr.Warning("your input is too long! It has been truncated.")
        user_input = '\n'.join(new_msg.split())
        solved, val_msg = cur_game.validate(user_input)
        response = ("Correct guess" if solved else "Bad guess (Wrong Answer)") + "\n" + val_msg
        new_io_history = prev_msg + [f"Guess>\n{new_msg}", "Prompt>\n" + response]
        return (
            ("" if not solved else gr.Textbox("Thank you for playing!", interactive=False)),
            new_io_history, "\n\n".join(new_io_history), (1 if solved else 0),
        )

    gr.Markdown(
        """
        > ### ‼️ Do ***<span style="color:red">NOT</span>*** refresh this page. ‼️<br>
        > #### ⚠️ Refreshing the page equals "Give-up 😭" ⚠️
        """
    )
    showhide_helper_btn = gr.Button("Show Input Helper (disabling manual input)", elem_id="lintao-helper-btn")
    io_history = gr.State(["Prompt>\n" + cur_game.get_prompt()])
    io_textbox = gr.Textbox("\n\n".join(io_history.value), label="Prompt>", interactive=False)
    textarea = gr.Textbox(label="Guess>", lines=5, info=f"(Shift + Enter to submit)")
    textarea.submit(add_msg, [textarea, io_history], [textarea, io_history, io_textbox, is_solved_component])
    js_submit = "(a,b) => [a,b]"
    if any([isinstance(cur_game, cls) for cls in (Islands, Sudoku, CrosswordArrangerGame, OrderingTextGame)]):
        if isinstance(cur_game, Islands):
            js, js_submit = js_island.format(N=cur_game.N), js_island_submit.format(N=cur_game.N)
        elif isinstance(cur_game, Sudoku):
            sudoku_arr = str(list(map(lambda r: ''.join(map(str, r)), cur_game.mat)))
            js, js_submit = js_sudoku.format(N=cur_game.srn, mat=sudoku_arr), js_sudoku_submit.format(N=cur_game.srn)
        elif isinstance(cur_game, CrosswordArrangerGame):
            js, js_submit = js_crossword.format(N=cur_game.board_size), js_crossword_submit.format(
                N=cur_game.board_size)
        elif isinstance(cur_game, OrderingTextGame):
            js, js_submit = js_ordering.format(items=f"{cur_game.words}"), js_ordering_submit.format()
        else:
            raise NotImplementedError(cur_game)
        showhide_helper_btn.click(lambda: (gr.update(interactive=False), gr.update(interactive=False)), None,
                                  [textarea, showhide_helper_btn], js=js)
    else:
        showhide_helper_btn.interactive = showhide_helper_btn.visible = False

    with gr.Row(elem_id="lintao-submit-row"):
        submit_btn = gr.Button("Submit", elem_id="lintao-submit-btn", variant='primary', scale=3)
        give_up_btn = gr.Button("Give-up 😭", variant='stop', scale=1)
    finish_btn = gr.Button("🎉🎊 ~ Finish Game ~ 🎊🎉", variant='primary', visible=False, interactive=False)

    submit_btn.click(add_msg, [textarea, io_history], [textarea, io_history, io_textbox, is_solved_component],
                     js=js_submit)
    give_up_checkbox = gr.Checkbox(False, visible=False, interactive=False)
    give_up_btn.click(
        lambda x: x, [give_up_checkbox], [give_up_checkbox],
        js="(x) => confirm('🥹 Give-up? 💸')"
    )

    def _forfeiting(confirmed, _solved_games):
        if confirmed:
            gr.Info("Sad to see you go... Wrapping things up...")
            cur_game.finish_stats_(forfeit=True)
            if level in LEVELS and level not in _solved_games[game_name]:
                _solved_games[game_name].append(level)
            upload_to_drive(fp_out)
            return 0, _solved_games
        return 1, _solved_games
    give_up_checkbox.change(
        lambda: (gr.update(interactive=False), gr.update(interactive=False)), None, [submit_btn, give_up_btn]
    ).then(
        _forfeiting, [give_up_checkbox, solved_games_component], [session_state_component, solved_games_component]
    ).then(
        lambda: (gr.update(interactive=True), gr.update(interactive=True)), None, [submit_btn, give_up_btn]
    )

    def game_is_solved(_is_solved, _session_state, _solved_games, progress=gr.Progress()):
        if _is_solved:
            if level in LEVELS and level not in _solved_games[game_name]:
                _solved_games[game_name].append(level)
            return (
                2,
                gr.update(visible=False, interactive=False),
                gr.update(visible=False, interactive=False),
                _solved_games,
                gr.update(visible=True, interactive=False),
            )
        else:
            return (
                _session_state, gr.update(), gr.update(), _solved_games, gr.update()
            )

    def finalize_game(_is_solved):
        if _is_solved:
            gr.Info("Reporting... Please click the button when available...")
            upload_to_drive(fp_out)
            return gr.update(interactive=True)
        return gr.update()

    is_solved_component.change(
        game_is_solved,
        [is_solved_component, session_state_component, solved_games_component],
        [session_state_component, submit_btn, give_up_btn, solved_games_component, finish_btn],
    ).then(
        finalize_game, [is_solved_component], [finish_btn],
    )
    finish_btn.click(
        lambda: (0, 0), None, [session_state_component, is_solved_component]
    )


# %%
def check_to_start_new_game(game_name, level, user=None, uid=None):
    print(game_name, level)
    if game_name is None or level is None:
        raise gr.Error("please choose both Game & Level")
    fp = _get_file_output(game_name, LEVEL_IDS[LEVELS.index(level)], uid)
    if os.path.exists(fp):
        raise gr.Error(f"You have done this game already.<br/>{game_name} - {level}")
    if user is None:
        gr.Warning("no user, game will be generated randomly")
    # else:
    #     if not user['email_verified']:
    #         gr.Warning("please verify your email address")
    #     elif user['email_verified'] == "mockuser":
    #         gr.Info("game will load with a mocked-up user")
    return 1


# %%
def check_played_game(solved_games, uid, progress=gr.Progress()):
    matches = _files.list(
        q=f"'{_folder_id}' in parents and mimeType='application/octet-stream' and name contains '{uid}_-_'",
        fields=f"files(name, id, {_cksm_methods_str})",
    ).execute()['files']
    ret = dict()
    for game_name in solved_games.keys():
        cur = []
        for level, level_id in zip(LEVELS, LEVEL_IDS):
            fp_out = _get_file_output(game_name, level_id, uid)
            _matches = list(filter(lambda m: fp_out.endswith(m['name']), matches))
            if os.path.exists(fp_out):
                upload_to_drive(fp_out, _matches)
            else:
                download_from_drive(fp_out, _matches)
            if os.path.exists(fp_out):
                cur.append(level)
        ret[game_name] = cur
    return ret, gr.update()


# %%
def session_state_change_fn(_session_state, cnt_return_with_val=2, cnt_negate_with_val=0, cnt_return=1, cnt_negate=0):
    # print(f"Session state changed to {_session_state}")
    ret = (_session_state not in [1, 2])

    def up(positive, positive_reset_value=True):
        return (
            gr.update(interactive=True, value=None) if positive and positive_reset_value else
            gr.update(interactive=True) if positive else gr.update(interactive=False)
        )

    return ([up(ret, True) for _ in range(cnt_return_with_val)] +
            [up(not ret, True) for _ in range(cnt_negate_with_val)] +
            [up(ret, False) for _ in range(cnt_return)] +
            [up(not ret, False) for _ in range(cnt_negate)] +
            [])


# %%
def solved_games_change_fn(solved_games):
    def _icon(_):
        return _.split('\t', 1)[0]
    return pd.DataFrame({
        _icon(g): [" ".join(map(_icon, l))]
        for g, l in solved_games.items()
    })


# %%


# %%

