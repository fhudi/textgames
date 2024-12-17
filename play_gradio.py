#%%
import os
os.environ.setdefault("TEXTGAMES_SHOW_HIDDEN_LEVEL", "1")
os.environ.setdefault("GRADIO_SERVER_PORT", "1080")
os.environ.setdefault("TEXTGAMES_LOADGAME_DIR", "problemsets")
os.environ.setdefault("TEXTGAMES_LOADGAME_ID", "42")

#%%
import time
import gradio as gr
from textgames import GAME_IDS, GAME_NAMES, LEVEL_IDS, LEVELS, new_game


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
    container.id = 'lintao-island-container';

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
with (gr.Blocks() as demo):
    # input_text = gr.Textbox(label="input")
    game_radio = gr.Radio(GAME_NAMES,label="Game")
    level_radio = gr.Radio(LEVELS, label="Level")
    new_game_btn = gr.Button("Start New Game")

    cur_game_start = gr.State()
    new_game_btn.click(lambda: time.time(), None, cur_game_start)

    io_history = None

    def calc_time_elapsed(start_time, cur_text, is_solved):
        if not is_solved:
            return f"Time Elapsed (sec): {time.time() - start_time:8.1f}"
        else:
            return cur_text

    @gr.render(inputs=[game_radio, level_radio], triggers=[new_game_btn.click])
    def start_new_game(game_name, level):
        global io_history
        if game_name is None or level is None:
            raise gr.Error("please choose both Game & Level")
        cur_game_id = GAME_IDS[GAME_NAMES.index(game_name)]
        difficulty_level = LEVEL_IDS[LEVELS.index(level)]

        is_solved = gr.State(False)

        elapsed_text = gr.Textbox("N/A", label=f"{game_name}", info=f"{level}",)
        gr.Timer(.3).tick(calc_time_elapsed, [cur_game_start, elapsed_text, is_solved], [elapsed_text])

        cur_game = new_game(game_name, difficulty_level)

        def add_msg(new_msg, prev_msg):
            user_input = '\n'.join(new_msg.split())
            solved, val_msg = cur_game.validate(user_input)
            response = ("Correct" if solved else "Bad") + " guess\n" + val_msg
            new_io_history = prev_msg + [f"Guess>\n{new_msg}", "Prompt>\n" + response]
            return (
                ("" if not solved else gr.Textbox("Thank you for playing!", interactive=False)),
                new_io_history, "\n\n".join(new_io_history), solved
            )

        io_history = gr.State(["Prompt>\n" + cur_game.get_prompt()])
        io_textbox = gr.Textbox("\n\n".join(io_history.value), label="Prompt>", interactive=False)
        textarea = gr.Textbox(label="Guess>", lines=5, info=f"(Shift + Enter to submit)")
        textarea.submit(add_msg, [textarea, io_history], [textarea, io_history, io_textbox, is_solved])
        if isinstance(cur_game, Islands):
            showhide_helper_btn = gr.Button("Show Input Helper", elem_id="lintao-helper-btn")
            submit_btn = gr.Button("Submit", elem_id="lintao-submit-btn")
            if isinstance(cur_game, Islands):
                js, js_submit = js_island.format(N=cur_game.N), js_island_submit.format(N=cur_game.N)
            else:
                raise NotImplementedError(cur_game)
            showhide_helper_btn.click(lambda: gr.update(interactive=False), None, textarea, js=js)
            submit_btn.click(add_msg, [textarea, io_history], [textarea, io_history, io_textbox, is_solved], js=js_submit)


demo.launch()


#%%


#%%


#%%


