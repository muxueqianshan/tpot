# -*- coding: utf-8 -*-

"""Copyright 2015-Present Randal S. Olson.

This file is part of the TPOT library.

TPOT is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

TPOT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with TPOT. If not, see <http://www.gnu.org/licenses/>.

"""

import subprocess
import sys
from contextlib import contextmanager
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import numpy as np

from tpot.driver import positive_integer, float_range, _get_arg_parser, _print_args, _read_data_file
from nose.tools import assert_raises
from unittest import TestCase


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def test_driver():
    """Assert that the TPOT driver outputs normal result in mode mode."""
    batcmd = "python -m tpot.driver tests/tests.csv -is , -target class -g 2 -p 2 -os 4 -cv 5 -s 45 -v 1"
    ret_stdout = subprocess.check_output(batcmd, shell=True)
    try:
        ret_val = float(ret_stdout.decode('UTF-8').split('\n')[-2].split(': ')[-1])
    except Exception:
        ret_val = -float('inf')
    assert ret_val > 0.0


def test_read_data_file():
    """Assert that _read_data_file raises ValueError when the targe column is missing."""
    # Mis-spelled target
    args_list = [
        'tests/tests.csv',
        '-is', ',',
        '-target', 'clas'   # typo for right target 'class'
    ]
    args = _get_arg_parser().parse_args(args_list)
    assert_raises(ValueError, _read_data_file, args=args)

    # Correctly spelled target
    args_list = [
        'tests/tests.csv',
        '-is', ',',
        '-target', 'class'
    ]
    args = _get_arg_parser().parse_args(args_list)
    input_data = _read_data_file(args)

    assert isinstance(input_data, np.recarray)


class ParserTest(TestCase):
    def setUp(self):
        self.parser = _get_arg_parser()

    def test_default_param(self):
        """Assert that the TPOT driver stores correct default values for all parameters."""
        args = self.parser.parse_args(['tests/tests.csv'])
        self.assertEqual(args.CROSSOVER_RATE, 0.1)
        self.assertEqual(args.DISABLE_UPDATE_CHECK, False)
        self.assertEqual(args.GENERATIONS, 100)
        self.assertEqual(args.INPUT_FILE, 'tests/tests.csv')
        self.assertEqual(args.INPUT_SEPARATOR, '\t')
        self.assertEqual(args.MAX_EVAL_MINS, 5)
        self.assertEqual(args.MUTATION_RATE, 0.9)
        self.assertEqual(args.NUM_CV_FOLDS, 5)
        self.assertEqual(args.NUM_JOBS, 1)
        self.assertEqual(args.OFFSPRING_SIZE, None)
        self.assertEqual(args.OUTPUT_FILE, '')
        self.assertEqual(args.POPULATION_SIZE, 100)
        self.assertEqual(args.RANDOM_STATE, None)
        self.assertEqual(args.SUBSAMPLE, 1.0)
        self.assertEqual(args.SCORING_FN, None)
        self.assertEqual(args.TARGET_NAME, 'class')
        self.assertEqual(args.TPOT_MODE, 'classification')
        self.assertEqual(args.VERBOSITY, 1)

    def test_print_args(self):
        """Assert that _print_args prints correct values for all parameters."""
        args = self.parser.parse_args(['tests/tests.csv'])
        with captured_output() as (out, err):
            _print_args(args)
        output = out.getvalue()
        expected_output = """
TPOT settings:
CONFIG_FILE\t=\tNone
CROSSOVER_RATE\t=\t0.1
GENERATIONS\t=\t100
INPUT_FILE\t=\ttests/tests.csv
INPUT_SEPARATOR\t=\t\t
MAX_EVAL_MINS\t=\t5
MAX_TIME_MINS\t=\tNone
MUTATION_RATE\t=\t0.9
NUM_CV_FOLDS\t=\t5
NUM_JOBS\t=\t1
OFFSPRING_SIZE\t=\t100
OUTPUT_FILE\t=\t
POPULATION_SIZE\t=\t100
RANDOM_STATE\t=\tNone
SCORING_FN\t=\taccuracy
SUBSAMPLE\t=\t1.0
TARGET_NAME\t=\tclass
TPOT_MODE\t=\tclassification
VERBOSITY\t=\t1

"""

        self.assertEqual(_sort_lines(expected_output), _sort_lines(output))


def _sort_lines(text):
    return '\n'.join(sorted(text.split('\n')))


def test_positive_integer():
    """Assert that the TPOT CLI interface's integer parsing throws an exception when n < 0."""
    assert_raises(Exception, positive_integer, '-1')


def test_positive_integer_2():
    """Assert that the TPOT CLI interface's integer parsing returns the integer value of a string encoded integer when n > 0."""
    assert 1 == positive_integer('1')


def test_positive_integer_3():
    """Assert that the TPOT CLI interface's integer parsing throws an exception when n is not an integer."""
    assert_raises(Exception, positive_integer, 'foobar')


def test_float_range():
    """Assert that the TPOT CLI interface's float range returns a float with input is in 0. - 1.0."""
    assert 0.5 == float_range('0.5')


def test_float_range_2():
    """Assert that the TPOT CLI interface's float range throws an exception when input it out of range."""
    assert_raises(Exception, float_range, '2.0')


def test_float_range_3():
    """Assert that the TPOT CLI interface's float range throws an exception when input is not a float."""
    assert_raises(Exception, float_range, 'foobar')