# -*- coding: utf-8 -*-
import giterm.textutils as textutils


def setup():
    pass


def teardown():
    pass


def test_shorten():
    string = 'Hi, this is a long string that should be shorten.'
    new_string, num_raw_bytes = textutils.shorten(string, size=18)

    assert len(new_string) == 18
    assert num_raw_bytes == 49  # raw_bytes(new_string) or raw_bytes(string)?
    assert new_string == 'Hi, this is a l...'


def test_blocks():
    text = '''@@ -118,6 +118,7 @@ def git_submodules():

 def git_tags():
     data = run('git tag')
+    # If Git >= 2.3.3 'git log --date-order --tags --simplify-by-decoration \
--pretty=format:"%d"'
     return data


@@ -135,8 +136,6 @@ def git_diff(path):
             error = 0
     else:
         data = data[4:]
-    # import cursutils
-    # cursutils.debug()
     if error:
         raise Exception('Error executing "' + cmd + '" (error = ' + \
str(error))
    '''.split('\n')

    blocks = textutils.blocks(text, lambda x: x and x.startswith('@@'))

    assert len(list(blocks)) == 2


def test_remove_superfluous_alineas():
    text = '''
             error = 0
     else:
         data = data[4:]
-    # import cursutils
-    # cursutils.debug()
     if error:
         raise Exception('Error executing "' + cmd + '" (error = ' + \
str(error))'''.split('\n')

    expected_text = '''
         error = 0
 else:
     data = data[4:]
-# import cursutils
-# cursutils.debug()
 if error:
     raise Exception('Error executing "' + cmd + '" (error = ' + \
str(error))'''.split('\n')

    assert textutils.remove_superfluous_alineas(text) == expected_text


def test_tabs_to_spaces():
    text = '''
\t\t\t error = 0
\t else:
\t\t data = data[4:]
-    # import cursutils
-    # cursutils.debug()
\t if error:
\t\t raise Exception('Error executing "' + cmd + '" (error = ' + \
str(error))'''

    expected_text = '''
             error = 0
     else:
         data = data[4:]
-    # import cursutils
-    # cursutils.debug()
     if error:
         raise Exception('Error executing "' + cmd + '" (error = ' + \
str(error))'''

    assert textutils.tabs_to_spaces(text, num_spaces=4) == expected_text


def test_lstrip_hunk():
    text = '''
             error = 0
     else:
         data = data[4:]
-    # import cursutils
-    # cursutils.debug()
     if error:
         raise Exception('Error executing "' + cmd + '" (error = ' + \
str(error))'''.split('\n')

    expected_text = '''
         error = 0
 else:
     data = data[4:]
-# import cursutils
-# cursutils.debug()
 if error:
     raise Exception('Error executing "' + cmd + '" (error = ' + \
str(error))'''.split('\n')

    assert textutils.lstrip_hunk(text, offset=4) == expected_text


def test_get_new_minimum_alinea():
    text_a = '+    a'
    text_b = '-b'
    text_c = '   c'

    assert textutils.get_new_minimum_alinea(
        text_a,
        previous_alinea=5,
        num_ignored_chars=1) == 4

    assert textutils.get_new_minimum_alinea(
        text_a,
        previous_alinea=2,
        num_ignored_chars=1) == 2

    assert textutils.get_new_minimum_alinea(
        text_b,
        previous_alinea=1,
        num_ignored_chars=1) == 0

    assert textutils.get_new_minimum_alinea(
        text_b,
        previous_alinea=2,
        num_ignored_chars=0) == 0

    assert textutils.get_new_minimum_alinea(
        text_c,
        previous_alinea=2,
        num_ignored_chars=0) == 2
