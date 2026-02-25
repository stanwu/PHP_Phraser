import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

import php_analyzer


class TestPhpAnalyzer(unittest.TestCase):
    def test_sanitize_php_ignores_strings_and_comments(self):
        code = """<?php
// if ($a) { }
# elseif ($b) { }
/* else { } */
$x = "if ($a) { }";
$y = 'else { }';
if ($real) { echo "ok"; }
"""
        sanitized = php_analyzer.sanitize_php(code)
        # Only the real `if` should remain matchable.
        keywords = [m.group(1).lower() for m in php_analyzer.KEYWORD_RE.finditer(sanitized)]
        self.assertEqual(keywords, ["if"])

    def test_analyze_brace_nesting_and_conditions(self):
        php = """<?php
if ($a) {
  if ($b && ($c)) {
    echo "x";
  } else {
    echo "y";
  }
} elseif ($d) {
  echo "z";
} else {
  echo "w";
}
"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = root / "sample.php"
            p.write_text(php, encoding="utf-8")
            rel, rep = php_analyzer.analyze_php_file(p, root)

        self.assertEqual(rel, "sample.php")
        # Correct branch count: outer if, inner if, inner else, outer elseif, outer else = 5
        self.assertEqual(rep.total_branches, 5)
        self.assertGreaterEqual(rep.max_depth, 2)

        blocks = rep.blocks
        self.assertEqual(blocks[0].type, "if")
        self.assertEqual(blocks[0].line, 2)
        self.assertEqual(blocks[0].condition, "$a")
        self.assertEqual(blocks[0].if_nesting_depth, 1)

        self.assertEqual(blocks[1].type, "if")
        self.assertEqual(blocks[1].line, 3)
        self.assertIn("$b", blocks[1].condition)
        self.assertEqual(blocks[1].if_nesting_depth, 2)

        self.assertEqual(blocks[2].type, "else")
        self.assertEqual(blocks[2].line, 5)

        self.assertEqual(blocks[3].type, "elseif")
        self.assertEqual(blocks[3].line, 8)
        self.assertEqual(blocks[3].condition, "$d")

        self.assertEqual(blocks[4].type, "else")
        self.assertEqual(blocks[4].line, 10)

    def test_analyze_alt_syntax_depth(self):
        php = """<?php
if ($a):
  if ($b):
    echo "x";
  endif;
else:
  echo "y";
endif;
"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = root / "alt.php"
            p.write_text(php, encoding="utf-8")
            _, rep = php_analyzer.analyze_php_file(p, root)

        # outer if, inner if, outer else => 3
        self.assertEqual(rep.total_branches, 3)
        self.assertEqual(rep.max_depth, 2)

    def test_function_grouping_counts_branches(self):
        php = """<?php
if ($g) { echo "g"; }

function foo($x) {
  if ($x) { echo "x"; }
  else { echo "y"; }
}
"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = root / "fn.php"
            p.write_text(php, encoding="utf-8")
            _, rep = php_analyzer.analyze_php_file(p, root)

        self.assertEqual(rep.total_branches, 3)  # global if + if + else in foo
        self.assertEqual(len(rep.functions), 1)
        self.assertEqual(rep.functions[0].name, "foo")
        self.assertEqual(rep.functions[0].total_branches, 2)
        self.assertEqual(rep.functions[0].max_depth, 1)

    def test_main_writes_json(self):
        php = """<?php
if ($a) { echo "x"; }
"""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "a.php").write_text(php, encoding="utf-8")
            cwd = Path.cwd()
            try:
                # run main in temp output dir
                os.chdir(td)
                buf_out = StringIO()
                buf_err = StringIO()
                with redirect_stdout(buf_out), redirect_stderr(buf_err):
                    rc = php_analyzer.main([str(root)])
                self.assertEqual(rc, 0)
                out = Path("analysis_report.json")
                self.assertTrue(out.exists())
                data = json.loads(out.read_text(encoding="utf-8"))
                self.assertEqual(data["summary"]["total_files"], 1)
                self.assertEqual(data["summary"]["total_branches"], 1)
                self.assertIn("a.php", data["files"])
            finally:
                os.chdir(cwd)


if __name__ == "__main__":
    unittest.main()
