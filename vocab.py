import sys
import os
import argparse  # option parsing
import re  # regular expression
import codecs
import text
usage = 'Convert from text to integer format.'


### Global variables ###


### Class declarations ###


### Function declarations ###
def process_command_line():
    """
    Return a 1-tuple: (args list).
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """

    parser = argparse.ArgumentParser(description=usage)  # add description
    # positional arguments
    parser.add_argument('in_file', metavar='in_file', type=str, help='input file')
    parser.add_argument('vocab_file', metavar='vocab_file', type=str, help='output vocab file')

    # optional arguments
    parser.add_argument('--freq', dest='freq', type=int, default=-1, help='freq cutoff (default=-1, i.e., no cutoff)')
    parser.add_argument('--size', dest='size', type=int, default=-1,
                        help='vocab size cutoff (default=-1, i.e., no cutoff)')

    args = parser.parse_args()
    return args


def check_dir(vocab_file):
    dir_name = os.path.dirname(vocab_file)

    if dir_name != '' and os.path.exists(dir_name) == False:
        sys.stderr.write('! Directory %s doesn\'t exist, creating ...\n' % dir_name)
        os.makedirs(dir_name)


def clean_line(line):
    """
    Strip leading and trailing spaces
    """

    line = re.sub('(^\s+|\s$)', '', line);
    return line


def process_files(in_file, vocab_file, freq, size):
    """
    Read data from in_file, and output to vocab_file
    """

    sys.stderr.write('# in_file = %s, vocab_file = %s, freq=%d, size=%d\n' % (in_file, vocab_file, freq, size))

    # load/create vocab
    (words, vocab_map, vocab_size) = text.get_vocab(in_file, vocab_file, freq, size)
    sys.stderr.write('# vocab_size=%d\n' % (vocab_size))


if __name__ == '__main__':
    process_files("./val/pos/train.q", "./val/pos/vocab.q", -1, 50000)
    process_files("./val/pos/train.a", "./val/pos/vocab.a", -1, 50000)