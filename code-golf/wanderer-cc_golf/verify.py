import argparse
from code_golf_utils import verify_program, load_examples

parser = argparse.ArgumentParser()
parser.add_argument("--task-num", type=int, default=4)
parser.add_argument("--program-path", type=str, default="workdir/example.py")

args = parser.parse_args()

examples = load_examples(args.task_num)
program_path = args.program_path
res = verify_program(examples, program_path)
