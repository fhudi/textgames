---
title: textgames
app_file: play_with_hf.py
sdk: gradio
sdk_version: 5.17.1
python_version: 3.11.8

hf_oauth: true
---
# TextGames

## Play on Hosted Servers

- HuggingFace Space

    https://huggingface.co/spaces/fhudi/textgames
    (login required)

## Play on localhost

- Setup
    ```
    ❱❱❱ pip install -r requirements.txt
    ```

- Play (Terminal)
    ```
    ❱❱❱ python play.py
    ```

- Play (Web UI)
    ```
    ❱❱❱ pip install gradio
    ❱❱❱ GRADIO_SERVER_PORT=1080  python play_gradio.py
    ```
    Open `localhost:1080` to access.

---

## Extras

- Optional Environment Varibles
    ```
    TEXTGAMES_SHOW_HIDDEN_LEVEL=1
    ```
