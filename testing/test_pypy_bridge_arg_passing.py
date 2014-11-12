from testing.test_interpreter import BaseTestInterpreter
import pytest

class TestPyPyBridgeArgPassing(BaseTestInterpreter):

    # XXX REF
    def test_php2py_obj_by_val(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f(x):
                x.v = 1337
            EOD;

            $f = embed_py_func($src);

            class A {
                function __construct($v) {
                    $this->v = $v;
                }
            };

            $in = new A(666);
            $f($in);
            echo $in->v;
        ''')
        assert php_space.int_w(output[0]) == 1337

    def test_php2py_str_by_val_func(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f(s):
                s = s.replace("1", "x")
            EOD;

            $f = embed_py_func($src);

            $in = "123";
            $f($in);
            echo $in;
        ''')
        assert php_space.str_w(output[0]) == "123" # i.e. unchanged

    def test_php2py_str_by_ref_func(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            @php_refs("s")
            def f(s):
                s = s.replace("1", "x")
            EOD;

            $f = embed_py_func($src);

            $in = "123";
            $f($in);
            echo $in;
        ''')
        assert php_space.str_w(output[0]) == "x23"

    def test_php2py_mixed_key_array_by_val_func(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f(ary):
                ary["x"] = "y"
            EOD;

            $f = embed_py_func($src);
            $in = array("x" => "x");
            $f($in);
            echo $in["x"];
        ''')
        assert php_space.str_w(output[0]) == "x"

    def test_php2py_mixed_key_array_by_val_func_global(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f(ary):
                ary["x"] = "y"
            EOD;

            embed_py_func_global($src);
            $in = array("x" => "x");
            f($in);
            echo $in["x"];
        ''')
        assert php_space.str_w(output[0]) == "x"

    def test_php2py_mixed_key_array_by_ref_func_global(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            @php_refs("ary")
            def f(ary):
                ary["x"] = "y"
            EOD;

            embed_py_func_global($src);
            $in = array("x" => "x");
            f($in);
            echo $in["x"];
        ''')
        assert php_space.str_w(output[0]) == "y"

    def test_php2py_mixed_key_array_by_val_method(self):
        php_space = self.space
        output = self.run('''
            class A {};

            $src = <<<EOD
            def f(self, ary):
                ary["x"] = "y"
            EOD;
            embed_py_meth("A", $src);

            $a = new A();

            $in = array("x" => "x");
            $a->f($in);
            echo $in["x"];
        ''')
        assert php_space.str_w(output[0]) == "x"

    def test_php2py_mixed_key_array_by_ref_method(self):
        php_space = self.space
        output = self.run('''
            class A {};

            $src = <<<EOD
            @php_refs("ary")
            def f(self, ary):
                ary["x"] = "y"
            EOD;
            embed_py_meth("A", $src);

            $a = new A();

            $in = array("x" => "x");
            $a->f($in);
            echo $in["x"];
        ''')
        assert php_space.str_w(output[0]) == "y"

    def test_php2py_mixed_key_array_by_ref(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            @php_refs("ary")
            def f(ary):
                ary["x"] = "y"
            EOD;

            $f = embed_py_func($src);
            $in = array("x" => "x");
            $f($in);
            echo $in["x"];
        ''')
        assert php_space.str_w(output[0]) == "y"

    def test_php2py_int_key_array_by_val(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f(ary):
                ary_l = ary.as_list()
                ary_l[0] = "a"
            EOD;

            $f = embed_py_func($src);
            $in = array("x");
            $f($in);
            echo $in[0];
        ''')
        assert php_space.str_w(output[0]) == "x"

    def test_php2py_int_key_array_by_ref(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            @php_refs("ary")
            def f(ary):
                ary_l = ary.as_list()
                ary_l[0] = "a"
            EOD;

            $f = embed_py_func($src);
            $in = array("x");
            $f($in);
            echo $in[0];
        ''')
        assert php_space.str_w(output[0]) == "a"

    def test_php2py_int_key_array_by_val2(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f(ary):
                ary_l = ary.as_list()
                ary_l.append("a")
            EOD;

            $f = embed_py_func($src);
            $in = array("x");
            $f($in);
            echo count($in);
            echo $in[0];
        ''')
        assert php_space.int_w(output[0]) == 1
        assert php_space.str_w(output[1]) == "x"

    def test_php2py_int_key_array_by_ref2(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            @php_refs("ary")
            def f(ary):
                ary_l = ary.as_list()
                ary_l.append("a")
            EOD;

            $f = embed_py_func($src);
            $in = array("x");
            $f($in);
            echo count($in);
            echo $in[0];
            echo $in[1];
        ''')
        assert php_space.int_w(output[0]) == 2
        assert php_space.str_w(output[1]) == "x"
        assert php_space.str_w(output[2]) == "a"

    def test_php2py_existing_ref_by_val_func(self, php_space):
        output = self.run('''
        function takes_ref(&$x) {
            $src = "def mutate_ref(y): y = 666";
            $mutate_ref = embed_py_func($src);
            $mutate_ref($x);
            echo $x;
        }

        $a = 1;
        takes_ref($a);
        echo $a;
        ''')
        assert php_space.int_w(output[0]) == 1
        assert php_space.int_w(output[1]) == 1

    def test_php2py_existing_ref_by_ref_func(self, php_space):
        output = self.run('''
        function takes_ref(&$x) {
            $src = "@php_refs('y')\ndef mutate_ref(y): y = 666";
            $mutate_ref = embed_py_func($src);
            $mutate_ref($x);
            echo $x;
        }

        $a = 1;
        takes_ref($a);
        echo $a;
        ''')
        assert php_space.int_w(output[0]) == 666
        assert php_space.int_w(output[1]) == 666

    def test_php2py_int_by_ref_func(self, php_space):
        output = self.run('''
        $src = "@php_refs('y')\ndef mutate_ref(y): y = 666";
        $mutate_ref = embed_py_func($src);

        $a = 1;
        $mutate_ref($a);
        echo $a;
        ''')
        assert php_space.int_w(output[0]) == 666


    def test_php2py_int_by_ref_unary_op(self, php_space):
        output = self.run('''
        $src = "@php_refs('y')\ndef mutate_ref(y): y = -y";
        $mutate_ref = embed_py_func($src);

        $a = 1;
        $mutate_ref($a);
        echo $a;
        ''')
        assert php_space.int_w(output[0]) == -1

    def test_php2py_int_by_ref_binary_op(self, php_space):
        output = self.run('''
        $src = "@php_refs('y')\ndef mutate_ref(y): y = y + 1";
        $mutate_ref = embed_py_func($src);

        $a = 1;
        $mutate_ref($a);
        echo $a;
        ''')
        assert php_space.int_w(output[0]) == 2

    def test_php2py_int_by_ref_binary_op2(self, php_space):
        output = self.run('''
        $src = "@php_refs('y')\ndef mutate_ref(y): y = 1 + y";
        $mutate_ref = embed_py_func($src);

        $a = 1;
        $mutate_ref($a);
        echo $a;
        ''')
        assert php_space.int_w(output[0]) == 2

    def test_php2py_int_by_ref_binary_op3(self, php_space):
        output = self.run('''
        $src = "@php_refs('y', 'z')\ndef mutate_ref(y, z): y = y + z";
        $mutate_ref = embed_py_func($src);

        $a = 1;
        $b = 2;
        $mutate_ref($a, $b);
        echo $a;
        ''')
        assert php_space.int_w(output[0]) == 3

    def test_php2py_existing_ref_by_val2(self, php_space):
        output = self.run('''
        function takes_ref(&$x) {
            $src = "def mutate_ref(y): y = y + 1";
            $mutate_ref = embed_py_func($src);
            $mutate_ref($x);
            echo $x;
        }

        $a = 1;
        takes_ref($a);
        echo $a;
        ''')
        assert php_space.int_w(output[0]) == 1
        assert php_space.int_w(output[1]) == 1

    def test_php2py_existing_ref_by_ref2(self, php_space):
        output = self.run('''
        function takes_ref(&$x) {
            $src = "@php_refs('y')\ndef mutate_ref(y): y = y + 1";
            $mutate_ref = embed_py_func($src);
            $mutate_ref($x);
            echo $x;
        }

        $a = 1;
        takes_ref($a);
        echo $a;
        ''')
        assert php_space.int_w(output[0]) == 2
        assert php_space.int_w(output[1]) == 2

    @pytest.mark.xfail
    def test_php2py_mutible_binop_on_ref(self, php_space):
        output = self.run('''
        $src = <<<EOD
        @php_refs('x', 'y')
        def mutate_ref(x, y):
            x, y = x.as_list(), y.as_list()
            x += y
        EOD;
        $mutate_ref = embed_py_func($src);

        $a = array("1");
        $b = array("2");
        $mutate_ref($a, $b);

        foreach ($a as $x) {
                echo $x;
        }
        ''')
        assert php_space.int_w(output[0]) == 1
        assert php_space.int_w(output[1]) == 2

    # ---

    def test_py2php_list_by_val(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f():
                l = [1,2,3]
                g(l)
                return l[0]
            EOD;

            function g($l) { $l[0] = 666; }

            $f = embed_py_func($src);
            $r = $f();
            echo $r;
        ''')
        assert php_space.int_w(output[0]) == 1

    def test_py2php_list_by_ref(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f():
                l = PHPRef([1,2,3])
                g(l)
                return l.deref()[0]
            EOD;

            function g(&$l) { $l[0] = 666; }

            $f = embed_py_func($src);
            $r = $f();
            echo $r;
        ''')
        assert php_space.int_w(output[0]) == 666

    def test_py2php_dict_by_val(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f():
                d = { "a" : "b", "b": "c" }
                g(d)
                return d["a"]
            EOD;

            function g($d) { $d["a"] = "z"; }

            $f = embed_py_func($src);
            $r = $f();
            echo $r;
        ''')
        assert php_space.str_w(output[0]) == "b"

    def test_py2php_dict_by_ref2(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f():
                d = { "a" : "b", "b": "c" }
                d_ref = PHPRef(d)
                g(d_ref)
                return d_ref.deref()["a"]
            EOD;

            function g(&$d) { $d["a"] = "z"; }

            $f = embed_py_func($src);
            $r = $f();
            echo $r;
        ''')
        assert php_space.str_w(output[0]) == "z"


    def test_py2php_int_by_val(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f():
                i = 1
                g(i)
                return i
            EOD;

            function g($i) { $i = 666; }

            $f = embed_py_func($src);
            $r = $f();
            echo $r;
        ''')
        assert php_space.int_w(output[0]) == 1

    def test_py2php_int_by_ref(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f():
                i = PHPRef(1337)
                g(i)
                return i.deref()
            EOD;

            function g(&$i) { $i = 666; }

            $f = embed_py_func($src);
            $r = $f();
            echo $r;
        ''')
        assert php_space.int_w(output[0]) == 666

    def test_py2php_obj_by_val(self):
        """note that it is the object id that is by value.
        the object is not copied like an array"""
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f(a1, a2):
                swap_local(a1, a2)
                return [a1, a2]
            EOD;

            $f = embed_py_func($src);

            class C {
                function __construct($v) {
                    $this->v = $v;
                }
            };

            function swap_local($o1, $o2) {
                $tmp = $o1;
                $o1 = $o2;
                $o2 = $tmp;
            }

            $c1 = new C(1);
            $c2 = new C(2);

            $arr = $f($c1, $c2);
            echo $arr[0]->v;
            echo $arr[1]->v;
        ''')
        # they should not swap
        assert php_space.int_w(output[0]) == 1
        assert php_space.int_w(output[1]) == 2

    def test_py2php_obj_by_ref(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f(a1, a2):
                p1, p2 = PHPRef(a1), PHPRef(a2)
                swap(p1, p2)
                return [p1.deref(), p2.deref()]
            EOD;

            $f = embed_py_func($src);

            class C {
                function __construct($v) {
                    $this->v = $v;
                }
            };

            function swap(&$o1, &$o2) {
                $tmp = $o1;
                $o1 = $o2;
                $o2 = $tmp;
            }

            $c1 = new C(1);
            $c2 = new C(2);

            $arr = $f($c1, $c2);
            echo $arr[0]->v;
            echo $arr[1]->v;
        ''')
        assert php_space.int_w(output[0]) == 2
        assert php_space.int_w(output[1]) == 1

    def test_py2php_str_by_val(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f():
                i = "old"
                g(i)
                return i
            EOD;

            function g($s) { $s = "new"; }

            $f = embed_py_func($src);
            $r = $f();
            echo $r;
        ''')
        assert php_space.str_w(output[0]) == "old"

    def test_py2php_str_by_val2(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f():
                i = "old"
                g(i)
                return i
            EOD;

            function g($s) { $s[0] = "x"; }

            $f = embed_py_func($src);
            $r = $f();
            echo $r;
        ''')
        assert php_space.str_w(output[0]) == "old"

    def test_py2php_str_by_ref(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f():
                i = PHPRef("old")
                g(i)
                return i.deref()
            EOD;

            function g(&$s) { $s = "new"; }

            $f = embed_py_func($src);
            $r = $f();
            echo $r;
        ''')
        assert php_space.str_w(output[0]) == "new"

    def test_py2php_str_by_ref2(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f():
                i = PHPRef("old")
                g(i)
                return i.deref()
            EOD;

            function g(&$s) { $s[0] = "x"; }

            $f = embed_py_func($src);
            $r = $f();
            echo $r;
        ''')
        assert php_space.str_w(output[0]) == "xld"

    def test_py2php_pref_to_non_ref_is_error(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f():
                i = PHPRef("old")
                try:
                    g(i) # is an error since we passed a ref to a non-ref arg
                    return "No exception!"
                except BridgeError as e:
                    return e.message
            EOD;

            function g($s) {}

            $f = embed_py_func($src);
            $r = $f();
            echo($r);
        ''')
        assert(php_space.str_w(output[0]) ==
                "Arg 1 of PHP func 'g' is pass by value")

    def test_py2php_value_to_ref_is_error(self):
        php_space = self.space
        output = self.run('''
            $src = <<<EOD
            def f():
                i = "old"
                try:
                    g(i) # is an error since we passed a ref to a non-ref arg
                    return "No exception!"
                except BridgeError as e:
                    return e.message
            EOD;

            function g(&$s) {}

            $f = embed_py_func($src);
            $r = $f();
            echo($r);
        ''')
        assert(php_space.str_w(output[0]) ==
                "Arg 1 of PHP func 'g' is pass by reference")
