import argparse
import os
import platform
from junit_xml import TestSuite, TestCase
from tap13 import TAP13 as tap13


def map_yaml_to_junit(test):
    yaml = test.yaml or {}
    # Even though the name is `duration_ms` the value is in seconds.
    elapsed_sec = yaml.get('duration_ms', None)
    t = TestCase(test.description, classname=None, elapsed_sec=elapsed_sec)
    if test.result == 'ok':
        if test.directive in ['SKIP', 'TODO']:
            t.add_skipped_info(test.comment)
        else:
            t.stdout = test.comment

    elif test.result == 'not ok':
        err_code = yaml.get('exitcode', 0)
        err_severity = yaml.get('severity', '')
        err_output = yaml.get('stack', '')
        error_message = "{} ({})".format(err_severity, err_code)
        if err_severity == 'crashed' or err_code < 0:
            t.add_error_info(error_message, err_output, err_code)
        else:
            t.add_failure_info(error_message, err_output, err_code)

    return t


def parse(name, data):
    tap_parser = tap13()
    tap_parser.parse(data)
    junit_tests = [map_yaml_to_junit(t) for t in tap_parser.tests]
    return TestSuite(name, junit_tests, platform.node())


def convert(in_file, out_file):
    input_file = os.path.splitext(in_file.name)[0]
    data = in_file.read()
    result = parse(input_file, data)
    TestSuite.to_file(out_file, [result], prettyprint=True, encoding='utf-8')


def main():
  arg_parser = argparse.ArgumentParser('tap2junit')
  arg_parser.add_argument('--input', '-i', type=argparse.FileType('r'), help='path to tap13 file', required=True)
  arg_parser.add_argument('--output', '-o', type=argparse.FileType('w'), help='output file name', required=True)
  args = arg_parser.parse_args()
  convert(args.input, args.output)


if __name__ == "__main__":
  main()