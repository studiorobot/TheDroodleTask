set -e
set -u

# MAD_PATH=$(realpath `dirname $0`)
MAD_PATH=/Your-Workspace/Multi-Agents-Debate

python3 $MAD_PATH/code/debate4droodle.py \
    -I $MAD_PATH/data/Droodle/input.example.txt \
    -o $MAD_PATH/data/Droodle/output \
    -k Your-OpenAI-Api-Key