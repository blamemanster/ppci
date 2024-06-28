from ...common import CompilerError


def make_comma_or(parts):
    parts = list(map(lambda x: '"{}"'.format(x), parts))
    if len(parts) > 1:
        last = parts[-1]
        first = parts[:-1]
        return ", ".join(first) + " or " + last
    else:
        return "".join(parts)


class RecursiveDescentParser:
    """ Base class for recursive descent parsers """

    def __init__(self):
        self.token = None  # The current token under cursor
        self.tokens = None  # Iterable of tokens
        self._look_ahead = []
        self._last_loc = None

    def init_lexer(self, tokens):
        """ 用给定的标记初始化解析器(迭代器) """
        self.tokens = tokens
        self.token = next(self.tokens, None)
        self._look_ahead = []

    def error(self, msg, loc=None):
        """ 在当前位置引发错误 """
        if loc is None:
            if self.token is None:
                if self._last_loc is None:
                    loc = None
                else:
                    loc = self._last_loc
            else:
                loc = self.token.loc
        raise CompilerError(msg, loc)

    @property
    def current_location(self):
        return self.token.loc

    # Lexer helpers:
    def consume(self, typ=None):
        """ 断言下一个标记是type，如果是，则返回它。
            如果type是列表或元组，则使用给定类型之一。
            如果未给出type，则使用下一个令牌。
        """
        if typ is None:
            typ = self.peek
        #如果 typ 参数本身不是列表、元组或集合类型，则将其放入一个列表中。
        #这样做是为了确保 expected_types 变量始终是一个列表
        expected_types = typ if isinstance(typ, (list, tuple, set)) else [typ]

        if self.peek in expected_types:
            return self.next_token()
        else:
            expected = make_comma_or(expected_types)
            self.error('Expected {0}, got "{1}"'.format(expected, self.peek))

    def has_consumed(self, typ):
        """ 检查预判标记是否为type类型，如果是，则吃掉标记并返回true """
        if self.peek == typ:
            self.consume()
            return True
        return False

    def next_token(self):
        """ 前进到下一个元素 """
        tok = self.token
        if self._look_ahead:
            self.token = self._look_ahead.pop(0)
        else:
            self.token = next(self.tokens, None)

        if self.token is None and tok is not None:
            self._last_loc = tok.loc

        return tok

    def not_impl(self, msg=""):  # pragma: no cover
        """ Call this function when parsing reaches unimplemented parts """
        raise CompilerError("Not implemented " + msg, loc=self.token.loc)

    @property
    def peek(self):
        """查看下一个要解析的标记，但不要弹出它"""
        if self.token:
            return self.token.typ

    def look_ahead(self, amount):
        """ Take a look at x tokens ahead """
        if amount > 0:
            while len(self._look_ahead) < amount:
                next_token = next(self.tokens, None)
                if next_token is None:
                    return
                self._look_ahead.append(next_token)
            return self._look_ahead[amount - 1]
        else:
            return self.token

    @property
    def at_end(self):
        return self.peek is None
