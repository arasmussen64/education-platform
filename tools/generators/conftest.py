"""Tell pytest there are no tests in this folder.

This is an archive (see README.md). pytest finds tests by importing files, and
importing one of these scripts runs it: a generator would write a whole topic
folder. So when pytest searches a folder for tests (`pytest`, `pytest tools`),
it must skip everything here, whatever a file is called.

This can't stop someone naming one of these files on the pytest command line;
pytest imports a file it is given by name. Don't do that.
"""

# pytest reads this name from a conftest.py and skips every path that matches.
# "*" matches everything in this folder and below it.
collect_ignore_glob = ["*"]
