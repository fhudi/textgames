#%%
import os
os.environ.setdefault("GRADIO_SERVER_PORT", "1080")
os.environ.setdefault("TEXTGAMES_SHOW_HIDDEN_LEVEL", "1")
os.environ.setdefault("TEXTGAMES_LOADGAME_DIR", "problemsets")
os.environ.setdefault("TEXTGAMES_LOADGAME_ID", "42")
os.environ.setdefault("TEXTGAMES_MOCKUSER", "")
favicon_path = "textgames-scrabble-black2-ss.png"

#%%
import time
import gradio as gr
from textgames import GAME_IDS, GAME_NAMES, LEVEL_IDS, LEVELS, new_game, preload_game


#%%
from textgames.islands.islands import Islands
js_island = """
function island() {{
    const grid_N = {N},
          grid_px = 40;

    const container = document.createElement('div');
    container.style.display = 'grid';
    container.style.gridTemplateColumns = container.style.gridTemplateRows = `repeat(${{grid_N}}, ${{grid_px}}px)`;
    container.style.gap = '1px';
    container.style.border = '2px solid black';
    container.style.width = 'max-content';
    container.style.margin = '5px 0px 5px 40px';
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
            cell.style.border = '1px solid gray';
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
    
    var submitBtn = document.getElementById("lintao-submit-btn");
    submitBtn.parentElement.insertBefore(container, submitBtn);
    
    var helperBtn = document.getElementById("lintao-helper-btn");
    helperBtn.style.display = 'none';
}}
"""


js_island_submit = """
function island_submit(textarea, io_history) {{
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


#%%
from textgames.sudoku.sudoku import Sudoku

js_sudoku = """
function sudoku() {{
    const N = {N};
    const grid_N = N*N;
          grid_px = 40;

    const container = document.createElement('div');
    container.style.display = 'grid';
    container.style.gridTemplateColumns = container.style.gridTemplateRows = `repeat(${{grid_N}}, ${{grid_px}}px)`;
    container.style.gap = '1px';
    container.style.border = '2px solid white';
    container.style.width = 'max-content';
    container.style.margin = '5px 0px 5px 40px';
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
            cell.style.border = '1px solid #c0c0c0';
            cell.style.backgroundColor = 'black'
            cell.style.cursor = 'pointer';
            cell.id = `lintao-cell-${{i}}-${{j}}`;
            
            //cell.style.color = 'black';
            //cell.style.outline = 'none';
    
            if (j % N === 0) cell.style.borderLeft = `${{grid_px/10}}px solid white`;
            if (j % N === (N-1)) cell.style.borderRight = `${{grid_px/10}}px solid white`;
            if (i % N === 0) cell.style.borderTop = `${{grid_px/10}}px solid white`;
            if (i % N === (N-1)) cell.style.borderBottom = `${{grid_px/10}}px solid white`;
    
            // Allow only numbers 1-9 or A-I
            cell.addEventListener('input', (e) => {{
                if ((N === 2  &&  (!/^[1-4A-D]$/.test(e.target.value))) || 
                    (N === 3  &&  (!/^[1-9A-I]$/.test(e.target.value)))) {{
                    e.target.value = '';
                }}
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
                cell.style.backgroundColor = '#b0b6bb';
            }} else {{
                cell.style.backgroundColor = 'black';
            }}
        }}
    }});

    container.addEventListener('focusout', () => {{
        for (let i = 0; i < grid_N * grid_N; i++) {{
            container.children[i].style.backgroundColor = 'black';
        }}
    }});

    var submitBtn = document.getElementById("lintao-submit-btn");
    submitBtn.parentElement.insertBefore(container, submitBtn);
    
    var helperBtn = document.getElementById("lintao-helper-btn");
    helperBtn.style.display = 'none';
}}
"""


js_sudoku_submit = """
function sudoku_submit(textarea, io_history) {{
    const N = {N};
    const grid_N = N*N;
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


#%%
from textgames.crossword_arranger.crossword_arranger import CrosswordArrangerGame

js_crossword = """
function crossword() {{
    const grid_N = {N};
          grid_px = 40;

    const container = document.createElement('div');
    container.style.display = 'grid';
    container.style.gridTemplateColumns = container.style.gridTemplateRows = `repeat(${{grid_N}}, ${{grid_px}}px)`;
    container.style.gap = '1px';
    container.style.border = '2px solid white';
    container.style.width = 'max-content';
    container.style.margin = '5px 0px 5px 40px';
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
            cell.style.border = '1px solid #c0c0c0';
            cell.style.backgroundColor = 'black'
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

    var submitBtn = document.getElementById("lintao-submit-btn");
    submitBtn.parentElement.insertBefore(container, submitBtn);
    
    var helperBtn = document.getElementById("lintao-helper-btn");
    helperBtn.style.display = 'none';
}}
"""


js_crossword_submit = """
function crossword_submit(textarea, io_history) {{
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


#%%
from textgames.ordering_text.ordering_text import OrderingTextGame

js_ordering = """
function ordering() {{          
    const listContainer = document.createElement('ul');
    listContainer.style.listStyle = 'none';
    listContainer.style.padding = '0';
    listContainer.style.width = '20em';
    listContainer.style.border = '2px solid white';
    listContainer.style.margin = '5px 0px 5px 40px';
    listContainer.id = 'lintao-container';
    
    document.body.appendChild(listContainer);
    
    const items = {items};
    
    items.forEach((itemText, index) => {{
        const listItem = document.createElement('li');
        listItem.textContent = itemText;
        listItem.draggable = true;
        listItem.style.padding = '10px';
        listItem.style.border = '1px solid #c0c0c0';
        listItem.style.margin = '3px';
        listItem.style.backgroundColor = 'black';
        listItem.style.cursor = 'grab';
        listItem.id = `lintao-item-${{index}}`;
    
        // Drag and drop events
        listItem.addEventListener('dragstart', (e) => {{
            const draggedIndex = Array.from(listContainer.children).indexOf(listItem);
            e.dataTransfer.setData('text/plain', draggedIndex);
            listItem.style.backgroundColor = '#1f1811';
        }});
    
        listItem.addEventListener('dragover', (e) => {{
            e.preventDefault();
            listItem.style.backgroundColor = '#303030';
        }});
    
        listItem.addEventListener('dragleave', () => {{
            listItem.style.backgroundColor = 'black';
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
    
            listItem.style.backgroundColor = 'black';
        }});
    
        listItem.addEventListener('dragend', () => {{
            listItem.style.backgroundColor = 'black';
        }});
    
        listContainer.appendChild(listItem);
    }});
    
    var submitBtn = document.getElementById("lintao-submit-btn");
    submitBtn.parentElement.insertBefore(listContainer, submitBtn);
    
    var helperBtn = document.getElementById("lintao-helper-btn");
    helperBtn.style.display = 'none';
}}
"""


js_ordering_submit = """
function ordering_submit(textarea, io_history) {{
    var ret = "";
    const container = 
    document.getElementById("lintao-container").childNodes.forEach(
        (c, i) => {{
            if (i>0) ret += '\\n';
            ret += c.textContent;
        }}
    )
    return [ret, io_history];
}}
"""


#%%
def _calc_time_elapsed(start_time, cur_text, is_solved):
    if not is_solved:
        return f"Time Elapsed (sec): {time.time() - start_time:8.1f}"
    else:
        return cur_text


#%%
def start_new_game(game_name, level, user=None, show_timer=False):
    global io_history, cur_game_start, new_game_btn
    # cur_game_id = GAME_IDS[GAME_NAMES.index(game_name)]
    difficulty_level = LEVEL_IDS[LEVELS.index(level)]

    is_solved = gr.State(False)

    if show_timer:
        elapsed_text = gr.Textbox("N/A", label=f"{game_name}", info=f"{level}", )
        gr.Timer(.3).tick(_calc_time_elapsed, [cur_game_start, elapsed_text, is_solved], [elapsed_text])

    if user is None and os.getenv("TEXTGAMES_MOCKUSER", ""):
        user = {'email': os.getenv("TEXTGAMES_MOCKUSER", "")}

    cur_game = (
        new_game(game_name, difficulty_level)
        if user is None else
        preload_game(game_name, difficulty_level, user)
    )

    def add_msg(new_msg, prev_msg):
        user_input = '\n'.join(new_msg.split())
        solved, val_msg = cur_game.validate(user_input)
        response = ("Correct" if solved else "Bad") + " guess\n" + val_msg
        new_io_history = prev_msg + [f"Guess>\n{new_msg}", "Prompt>\n" + response]
        return (
            ("" if not solved else gr.Textbox("Thank you for playing!", interactive=False)),
            new_io_history, "\n\n".join(new_io_history), solved,
        )

    io_history = gr.State(["Prompt>\n" + cur_game.get_prompt()])
    io_textbox = gr.Textbox("\n\n".join(io_history.value), label="Prompt>", interactive=False)
    textarea = gr.Textbox(label="Guess>", lines=5, info=f"(Shift + Enter to submit)")
    textarea.submit(add_msg, [textarea, io_history], [textarea, io_history, io_textbox, is_solved])
    js_submit = "(a,b) => [a,b]"
    if any([isinstance(cur_game, cls) for cls in (Islands, Sudoku, CrosswordArrangerGame, OrderingTextGame)]):
        if isinstance(cur_game, Islands):
            js, js_submit = js_island.format(N=cur_game.N), js_island_submit.format(N=cur_game.N)
        elif isinstance(cur_game, Sudoku):
            js, js_submit = js_sudoku.format(N=cur_game.srn), js_sudoku_submit.format(N=cur_game.srn)
        elif isinstance(cur_game, CrosswordArrangerGame):
            js, js_submit = js_crossword.format(N=cur_game.board_size), js_crossword_submit.format(
                N=cur_game.board_size)
        elif isinstance(cur_game, OrderingTextGame):
            js, js_submit = js_ordering.format(items=f"{cur_game.words}"), js_ordering_submit.format()
        else:
            raise NotImplementedError(cur_game)
        showhide_helper_btn = gr.Button("Show Input Helper (disabling manual input)", elem_id="lintao-helper-btn")
        showhide_helper_btn.click(lambda: gr.update(interactive=False), None, textarea, js=js)
    submit_btn = gr.Button("Submit", elem_id="lintao-submit-btn")
    submit_btn.click(add_msg, [textarea, io_history], [textarea, io_history, io_textbox, is_solved], js=js_submit)

#%%
def check_to_start_new_game(game_name, level):
    print(game_name, level)
    if game_name is None or level is None:
        raise gr.Error("please choose both Game & Level")
    return time.time(), 1



#%%
with gr.Blocks(title="TextGames") as demo:
    m = gr.Markdown("Welcome to TextGames!")
    demo.load(lambda: f"Welcome to TextGames! (Mock-User: {os.getenv('TEXTGAMES_MOCKUSER', '')})", None, [m])
    gr.Button("Logout", link="/logout", interactive=False)

    cur_game_start = gr.BrowserState()
    session_state = gr.State(0)    # 0: menu selection, 1: game on-going

    game_radio = gr.Radio(GAME_NAMES, label="Game", elem_id="radio-game-name")
    level_radio = gr.Radio(LEVELS, label="Level", elem_id="radio-level-name")
    new_game_btn = gr.Button("Start New Game")
    new_game_btn.click(
        check_to_start_new_game, [game_radio, level_radio], [cur_game_start, session_state],
        js="(g, l) => {var el = document.getElementById('lintao-container'); if (el) el.remove(); return [g, l];}",
    )

    io_history = None

    @gr.render(inputs=[game_radio, level_radio, session_state], triggers=[session_state.change])
    def _start_new_game(game_name, level, _session_state):
        if _session_state == 1:
            start_new_game(game_name, level)


#%%
if __name__ == "__main__":
    demo.launch(favicon_path=favicon_path if os.path.exists(favicon_path) else None)


#%%


#%%


#%%


