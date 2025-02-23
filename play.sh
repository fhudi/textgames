cur_datetime="$(date '+%Y%m%d_%H%M%S')";
echo "Current Time: ${cur_datetime}";
python -u play_gradio.py  |  tee "log/run_${cur_datetime}.log"
