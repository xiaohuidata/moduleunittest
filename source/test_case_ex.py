#!/bin/bash/python
import sys, unittest, traceback, re

class TestCaseEx(unittest.TestCase):

    err_prefix = '<<'
    err_postfix = '>>'
    unequal = '!='

    def assertEqualex(self, first, second, msg = None):
        try:
            self.assertEqual(first, second)
        except self.failureException, err:
            if msg:
                print msg
            raise self.failureException, err


    def exc_info_print(self):
        exctype, excvalue, tb = sys.exc_info()
        traceback.print_exc()

        print '\n\n>>>>> Exception information that can be ignored  >>>>>>'
        raise exctype


    def except_print(self, first, second, err, msg = None):
        if msg:
                print msg, err_prefix, first , unequal, second, err_postfix
        else:
            print err_prefix, first , unequal, second, err_postfix
        raise self.failureException, err


class GetTestCase(object):
    def get_class_name(class_file_name):
        class_name = ''
        test_lines = os.popen('grep class %s' % class_file_name).read().splitlines()
        for class_line in test_lines:
            class_name = class_line.split()[1].split('(')[0]
        return class_name

    def get_test(class_file_name):
        list_test = []
        test_lines = os.popen('grep def %s | grep " test_"' % class_file_name).read().splitlines()
        for test_line in test_lines:
            begin = test_line.find(' test_', 2) + 1
            end = test_line.find('(self):', 8)
            test = test_line[begin : end]
            list_test.append(test)
        return list_test


    """
    dir_name
    base_dir
    postfix
    """
    
    def get_test_case(dir_name, base_dir, postfix):
        if not os.path.isdir(dir_name):
            print 'source dir file'
            sys.exit()

        list_file_name = os.listdir(dir_name)
        dict_test_file = {}
        for file_name in list_file_name:
            postfix_len = len(postfix)
            if len(file_name) <= postfix_len:
                continue

            if file_name[-postfix_len:] == postfix:
                moudel_data = __import__(file_name[:-3])
                class_name = get_class_name(dir_name+'/'+file_name)
                if class_name:
                    source_file_name = base_dir + '/' + file_name[:-postfix_len] + '_test.py'
                    list_test = get_test(source_file_name)
                    dict_test_file[(file_name[:-3])] = {'file_name' : file_name,
                                                        'class_name' : class_name,
                                                        'moudel_data' : moudel_data,
                                                        'test' : list_test }

        return dict_test_file


class TestParser(object):
    SECTCRE = re.compile(r'\[(?P<header>[^]]+)\]')

    def __init__(self):
        self._sections = []
        self._test_case = {}

    def _read(self, fp, fpname):
        cursect = None
        optname = None
        lineno = 0
        e = None
        while True:
            line = fp.readline()
            if not line:
                break
            lineno = lineno +1
            # comment or blank line?
            if line.strip() == '' or line[0] in '#:':
                continue
            if line.split(None, 1)[0].lower() == 'rem' and line[0] in "rR":
                continue
            else:
                mo = self.SECTCRE.match(line)
                if mo:
                    sectname = mo.group('header')
                    if not self._test_case.has_key(sectname):
                        self._test_case[sectname] = []
                        self._sections.append(sectname)
                    cursect = self._test_case[sectname]
                else:
                    value = (line.lstrip().split())[0]
                    cursect.append(value)

    def read(self, filenames):
        if isinstance(filenames, basestring):
            filenames = [filenames]
        read_ok = []
        for filename in filenames:
            try:
                fp = open(filename)
            except IOError:
                continue
            self._read(fp, filename)
            fp.close()
            read_ok.append(filename)
        return read_ok

    def sections(self):
        return self._sections

    def test_case(self, section):
        list_test = self._test_case[section]
        return list_test


    def source_test_case(test_case_file):
        dict_test_case = {}

        if not os.path.isfile(test_case_file):
            print 'Without this file.'
            sys.exit()

        test_parser = TestParser()
        test_parser.read(test_case_file)

        for section in test_parser.sections():
            list_test = test_parser.test_case(section)
            dict_test_case[section] = list_test

        if not dict_test_case:
            print 'no test case'
            sys.exit()

        return dict_test_case
