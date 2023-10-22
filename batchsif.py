import argparse
import os
import subprocess
import sys

from gooey import Gooey, GooeyParser


def usage():
    print("Usage: python <script.py> config_file")
    print("---------------------------------------")
    print("<config_file> : /home/long_read/LRS/script/Lrs_thal_pipeline2/source/lrs_thal.config")
    print("<note> : use to run long read THAL pipeline")
    print("---------------------------------------")
    print("author :Jc")
    sys.exit()

def check_args():
    if len(sys.argv) != 2 or not os.path.isfile(sys.argv[1]):
        usage()

def load_config():
    with open(sys.argv[1], 'r') as f:
        config = {}
        for line in f:
            if '=' in line:
                key, val = line.strip().split('=', 1)
                config[key] = val
        return config

def check_config(config):
    if 'VERSION' not in config or 'function_sh' not in config:
        print("ERROR: config file illegal; there is no VERSION or function_sh")
        usage()

def check_singularity(config):
    if 'singularity' in config and os.path.isfile(config['singularity']):
        print("Run singularity mode")
        if not os.path.isfile(config['singularity_img']):
            print("ERROR: singularity_img not exist: ", config['singularity_img'])
    else:
        if not os.path.isdir(config['pipeline_dir']):
            print("ERROR: pipeline_dir not exist: ", config['pipeline_dir'])

def prepare_output(config):
    os.makedirs(config['outdir'], exist_ok=True)
    back_config = os.path.join(config['outdir'], os.path.basename(sys.argv[1]) + ".back")
    with open(back_config, 'w') as f:
        for key, val in config.items():
            f.write(f"{key}={val}\n")

def main():
    check_args()
    config = load_config()
    check_config(config)
    check_singularity(config)
    prepare_output(config)

if __name__ == "__main__":
    parser = GooeyParser(description="My Cool GUI Program!")
    parser.add_argument('Filename', widget="FileChooser")
    parser.add_argument('Date', widget="DateChooser")
    args = parser.parse_args(sys.argv[1:])
    main()
