import argparse
import os
import sys
import traceback

from tests import *

import client
import wan

GREEN = '\033[92m'
RED = '\033[91m'
CLEAR = '\033[0m'

def run_test(test_function, middlebox_module, for_part_1):
    """ Runs the given test, and returns 1 if the test was successful."""
    test_name = test_function.__name__
    try:
        print "Running", test_name
        test_function(middlebox_module, for_part_1)
        print "{}Test {} passed{}".format(GREEN, test_name, CLEAR)
        return 1
    except Exception:
        print "{}Test {} failed:\n{}{}".format(RED, test_name, traceback.format_exc(), CLEAR)
        return 0

def main():
    parser = argparse.ArgumentParser(description="CS168 Project 4 Tests")
    parser.add_argument(
        "--middlebox-name", dest="middlebox_name",
        required=True, type=str, action="store",
        help="Name of module that contains a WanOptimizer class to test; " +
        "e.g., to test the middlebox for part 1, pass in simple_wan_optimizer.")
    parser.add_argument(
        "--run-all",
        dest="run_all",
        action="store_true")
    parser.add_argument(
        "--send-less-than-one-block",
        dest="send_less_than_one_block",
        action="store_true")
    parser.add_argument(
        "--send-exactly-one-block",
        dest="send_exactly_one_block",
        action="store_true")
    parser.add_argument(
        "--send-exactly-one-block-both-directions",
        dest="send_exactly_one_block_both_directions",
        action="store_true")
    parser.add_argument(
        "--send-multiple-different-blocks",
        dest="send_multiple_different_blocks",
        action="store_true")
    parser.add_argument(
        "--one-client-with-multiple-receivers",
        dest="one_client_with_multiple_receivers",
        action="store_true")
    parser.add_argument(
        "--send-one-file",
        dest="send_one_file",
        action="store_true")
    parser.add_argument(
        "--send-multiple-files",
        dest="send_multiple_files",
        action="store_true")
    parser.add_argument(
        "--send-image-file",
        dest="send_image_file",
        action="store_true")
    parser.add_argument(
        "--data-reduction-same-files",
        dest="data_reduction_same_files",
        action="store_true")
    parser.add_argument(
        "--data-reduction-same-files-small",
        dest="data_reduction_same_files_small",
        action="store_true")
    parser.add_argument(
        "--data-reduction-suffixed-files",
        dest="data_reduction_suffixed_files",
        action="store_true")
    parser.add_argument(
        "--data-reduction-prefixed-files",
        dest="data_reduction_prefixed_files",
        action="store_true")
    parser.add_argument(
        "--data_reduction_prefixed_files_small",
        dest="data_reduction_prefixed_files_small",
        action="store_true")
    parser.add_argument(
        "--data-reduction-random-edits-file",
        dest="data_reduction_random_edits_file",
        action="store_true")
    parser.add_argument(
        "--verify-data-is-sent-incrementally",
        dest="verify_data_is_sent_incrementally",
        action="store_true")
    parser.add_argument(
        "--verify-middlebox-handles-interleaved-data",
        dest="verify_middlebox_handles_interleaved_data",
        action="store_true")

    args = parser.parse_args()
    if args.middlebox_name.endswith(".py"):
        print ("Do not include the .py suffix in the middlebox-name " +
            "argument.  Please re-run with the correct argument.")
        sys.exit()
    middlebox_module = __import__(args.middlebox_name)
    testing_part_1 = "simple" in args.middlebox_name

    total_tests = 0
    passed_tests = 0
    if args.send_less_than_one_block or args.run_all:
        passed_tests += run_test(
            simple_tests.send_less_than_one_block,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.send_exactly_one_block or args.run_all:
        passed_tests += run_test(
            simple_tests.send_exactly_one_block,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.send_exactly_one_block_both_directions or args.run_all:
        passed_tests += run_test(
            simple_tests.send_exactly_one_block_both_directions,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.send_multiple_different_blocks or args.run_all:
        passed_tests += run_test(
            simple_tests.send_multiple_different_blocks,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.one_client_with_multiple_receivers or args.run_all:
        passed_tests += run_test(
            simple_tests.one_client_with_multiple_receivers,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.send_one_file or args.run_all:
        test_module = send_one_file
        passed_tests += run_test(
            test_module.send_one_file,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.send_multiple_files or args.run_all:
        test_module = send_multiple_files
        passed_tests += run_test(
            test_module.send_multiple_files,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.send_image_file or args.run_all:
        test_module = send_image_file
        passed_tests += run_test(
            test_module.send_image_file,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.data_reduction_same_files or args.run_all:
        test_module = data_reduction_same_files
        passed_tests += run_test(
            test_module.data_reduction_same_files,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.data_reduction_same_files_small or args.run_all:
        test_module = data_reduction_same_files_small
        passed_tests += run_test(
            test_module.data_reduction_same_files_small,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.data_reduction_suffixed_files or args.run_all:
        test_module = data_reduction_suffixed_files
        passed_tests += run_test(
            test_module.data_reduction_suffixed_files,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.data_reduction_prefixed_files or args.run_all:
        test_module = data_reduction_prefixed_files
        passed_tests += run_test(
            test_module.data_reduction_prefixed_files,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.data_reduction_prefixed_files_small or args.run_all:
        test_module = data_reduction_prefixed_files_small
        passed_tests += run_test(
            test_module.data_reduction_prefixed_files_small,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.data_reduction_random_edits_file or args.run_all:
        test_module = data_reduction_random_edits_file
        passed_tests += run_test(
            test_module.data_reduction_random_edits_file,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.verify_data_is_sent_incrementally or args.run_all:
        test_module = verify_data_is_sent_incrementally
        passed_tests += run_test(
            test_module.verify_data_is_sent_incrementally,
            middlebox_module,
            testing_part_1)
        total_tests += 1
    if args.verify_middlebox_handles_interleaved_data or args.run_all:
        test_module = verify_middlebox_handles_interleaved_data
        passed_tests += run_test(
            test_module.verify_middlebox_handles_interleaved_data,
            middlebox_module,
            testing_part_1)
        total_tests += 1

    if passed_tests == total_tests:
        print "{}Success! Passed {}/{} tests{}".format(GREEN, passed_tests, total_tests, CLEAR)
    else:
        print "{}Failed {}/{} tests{}".format(RED, total_tests - passed_tests, total_tests, CLEAR)

    files = os.listdir('.')
    for file in files:
        if file.endswith("_output"):
            os.remove(file)

if __name__ == "__main__":
    main()
