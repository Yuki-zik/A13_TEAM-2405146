# Usage como_cli.py <input_file> <output_file> <singer> <keyshift> <steps>
# CLI tool
#
# This tool only calls accelerate launch "%work_dir%/bins/svc/inference.py", as run.sh does

import os
import sys
import shutil
from os.path import join, abspath, exists

args = sys.argv
if len(args) != 6:
    print(
        "Usage: como_cli.py <input_folder> <output_folder> <singer> <keyshift> <steps>"
    )
    sys.exit(1)

input_file = args[1]
output_file = args[2]
singer = args[3]
keyshift = args[4]
steps = args[5]  #! TODO

# Environs
exp_dir = abspath("egs/svc/DiffComoSVC")
work_dir = abspath(".")

os.environ["WORK_DIR"] = work_dir
os.environ["PYTHONPATH"] = work_dir
os.environ["PYTHONIOENCODING"] = "UTF-8"

gpu = "-1"  # Disable CUDA because we are requested to infer on CPU
exp_config = join(exp_dir, "exp_config.json")
infer_expt_dir = join(work_dir, "MAINMODEL", "comosvc")
infer_vocoder_dir = join(work_dir, "pretrained", "bigvgan")
infer_target_speaker = singer
infer_key_shift = keyshift
infer_source = join("data", "input")  # Amphion/data/input
infer_output_dir = join("data", "output")  # Amphion/data/output

data_input = infer_source
data_output = infer_output_dir

shutil.rmtree(data_input, ignore_errors=True)
shutil.rmtree(data_output, ignore_errors=True)
os.makedirs(data_input, exist_ok=True)
os.makedirs(data_output, exist_ok=True)
shutil.copy(input_file, join(data_input, "input.wav"))

# CUDA_VISIBLE_DEVICES=$gpu accelerate launch "$work_dir"/bins/svc/inference.py \
#     --config $exp_config \
#     --acoustics_dir $infer_expt_dir \
#     --vocoder_dir $infer_vocoder_dir \
#     --target_singer $infer_target_speaker \
#     --trans_key $infer_key_shift \
#     --source $infer_source \
#     --output_dir $infer_output_dir  \
#     --log_level debug

os.environ["CUDA_VISIBLE_DEVICES"] = gpu
inferpy = join(work_dir, "bins", "svc", "inference.py")
cmd = (
    f'accelerate launch "{inferpy}"'
    f' --config "{exp_config}"'
    f' --acoustics_dir "{infer_expt_dir}"'
    f' --vocoder_dir "{infer_vocoder_dir}"'
    f" --target_singer {infer_target_speaker}"
    f" --trans_key {infer_key_shift}"
    f' --source "{infer_source}"'
    f' --output_dir "{infer_output_dir}"'
    f" --log_level debug"
)
print(">>>", cmd)
cmd_err = os.system(cmd)
if cmd_err != 0:
    print(f"\nAmphion infer errorno: {cmd_err}")
    sys.exit(cmd_err)

# move ./data/output/* to output_folder use python
for file in os.listdir(data_output):
    shutil.copy(join(data_output, file), output_file)
    break
