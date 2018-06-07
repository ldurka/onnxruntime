import argparse
import lotus
import numpy as np
import os
import sys
from timeit import default_timer as timer

float_dict = {
    'tensor(float16)': 'float16',
    'tensor(float)': 'float32',
    'tensor(double)': 'float64'
}

integer_dict = {
    'tensor(int32)': 'int32',
    'tensor(int8)': 'int8',
    'tensor(uint8)': 'uint8',
    'tensor(int16)': 'int16',
    'tensor(uint16)': 'uint16',
    'tensor(int64)': 'int64',
    'tensor(uint64)': 'uint64'
}

# simple test program for loading onnx model, feeding all inputs and running the model num_iters times.
def main():
    parser = argparse.ArgumentParser(description='Simple Lotus Test Tool.')
    parser.add_argument('model_path', help='model path')
    parser.add_argument('num_iters', nargs='?', type=int, default=1000, help='model run iterations. default=1000')
    parser.add_argument('--debug', action='store_true', help='pause execution to allow attaching a debugger.')
    args = parser.parse_args()
    iters = args.num_iters

    if args.debug:
        print("Pausing execution ready for debugger to attach to pid: {}".format(os.getpid()))
        print("Press key to continue.")
        sys.stdin.read(1)

    sess = lotus.InferenceSession(args.model_path)

    feeds = {}
    for input_meta in sess.get_inputs():
        if input_meta.type in float_dict:
            feeds[input_meta.name] = np.random.rand(*input_meta.shape).astype(float_dict[input_meta.type])
        elif input_meta.type in integer_dict:
            feeds[input_meta.name] = np.random.uniform(high=1000, size=tuple(input_meta.shape).astype(integer_dict[input_meta.type]))
        elif input_meta.type == 'tensor(bool)':
            feeds[input_meta.name] = np.random.randint(2, size=tuple(input_meta.shape)).astype('bool')
        else:
            print("unsupported input type {} for input {}".format(input_meta.type, input_meta.name))
            sys.exit(-1)

    start = timer()
    for i in range(iters):
        sess.run([], feeds) # fetch all outputs
    end = timer()

    print('latency: {} ms'.format(((end - start)*1000)/iters))
    return 0

if __name__ == "__main__":
    sys.exit(main())