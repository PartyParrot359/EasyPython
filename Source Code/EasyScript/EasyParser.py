# -*- coding:utf-8 -*-
from EasyScript.EasyTokens import *
from EasyScript.EasyPyErrors import *
from EasyScript.EasyNodes import *


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        self.update_current_tok()
        return self.current_tok

    def reverse(self, amount=1):
        self.tok_idx -= amount
        self.update_current_tok()
        return self.current_tok

    def update_current_tok(self):
        if self.tok_idx >= 0 and self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]

    def parse(self):
        res = self.statements()
        if not res.error and self.current_tok.type != TT_EOF:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected '+','-','*','/','^',''==','!=','<','>','<=','>=','and' or 'or'"
                ))
        return res

    def statements(self):
        res = ParseResult()
        statements = []
        pos_start = self.current_tok.pos_start.copy()

        while self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

        statement = res.register(self.expr())
        if res.error:
            return res
        statements.append(statement)

        more_statements = True

        while True:
            newline_count = 0
            while self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()
                newline_count += 1
            if newline_count == 0:
                more_statements = False

            if not more_statements:
                break
            statement = res.try_register(self.expr())
            if not statement:
                self.reverse(res.to_reverse_count)
                more_statements = False
                continue
            statements.append(statement)
        return res.success(
            ListNode(statements, pos_start, self.current_tok.pos_end.copy()))

    def if_expr(self):
        res = ParseResult()
        all_class = res.register(self.if_expr_cases('if'))
        if res.error:
            return res
        cases, else_case = all_class
        return res.success(IFNode(cases, else_case))

    def if_expr_b(self):
        return self.if_expr_cases('elif')

    def if_expr_c(self):
        res = ParseResult()
        else_case = None

        if self.current_tok.matches(TT_KEYWORD, 'else'):
            res.register_advancement()
            self.advance()
            if self.current_tok.type == TT_NEWLINE:
                res.register_advancement()
                self.advance()

                statements = res.register(self.statements())
                if res.error:
                    return res
                else_case = (statements, True)

                if self.current_tok.matches(TT_KEYWORD, 'end'):
                    res.register_advancement()
                    self.advance()
                else:
                    return res.failure(
                        InvalidSyntaxError(self.current_tok.pos_start,
                                           self.current_tok.pos_end,
                                           "Expected 'end'"))
            else:
                expr = res.register(self.expr())
                if res.error:
                    return res
                else_case = (expr, False)

        return res.success(else_case)

    def if_expr_b_or_c(self):
        res = ParseResult()
        cases, else_case = [], None

        if self.current_tok.matches(TT_KEYWORD, 'elif'):
            all_cases = res.register(self.if_expr_b())
            if res.error:
                return res
            cases, else_case = all_cases

        else:
            else_case = res.register(self.if_expr_c())
            if res.error:
                return res
        return res.success((cases, else_case))

    def if_expr_cases(self, case_keyword):
        res = ParseResult()
        cases = []
        else_case = None
        if not self.current_tok.matches(TT_KEYWORD, case_keyword):
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end,
                                   f"Expected '{case_keyword}'"))

        res.register_advancement()
        self.advance()
        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT_KEYWORD, 'then'):
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end,
                                   "Expected 'then'"))

        res.register_advancement()
        self.advance()
        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()
            statements = res.register(self.statements())
            if res.error:
                return res
            cases.append((condition, statements, True))

            if self.current_tok.matches(TT_KEYWORD, 'end'):
                res.register_advancement()
                self.advance()
            else:
                all_cases = res.register(self.if_expr_b_or_c())
                if res.error:
                    return res
                new_cases, else_case = all_cases
                cases.extend(new_cases)
        else:
            expr = res.register(self.expr())
            if res.error:
                return res
            cases.append((condition, expr, False))

            all_cases = res.register(self.if_expr_b_or_c())
            if res.error:
                return res
            new_cases, else_case = all_cases
            cases.extend(new_cases)

        return res.success((cases, else_case))

    def if_expr_old(self):
        res = ParseResult()
        cases = []
        else_case = None

        if not self.current_tok.matches(TT_KEYWORD, 'if'):
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end, "Expected 'if'"))

        res.register_advancement()
        self.advance()

        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT_KEYWORD, 'then'):
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end,
                                   "Expected 'then'"))

        res.register_advancement()
        self.advance()

        expr = res.register(self.expr())
        if res.error:
            return res

        cases.append((condition, expr))

        while self.current_tok.matches(TT_KEYWORD, 'elif'):
            res.register_advancement()
            self.advance()

            condition = res.register(self.expr())
            if res.error:
                return res

            if not self.current_tok.matches(TT_KEYWORD, 'then'):
                return res.failure(
                    InvalidSyntaxError(self.current_tok.pos_start,
                                       self.current_tok.pos_end,
                                       "Expected 'then'"))

            res.register_advancement()
            self.advance()

            expr = res.register(self.expr())
            if res.error:
                return res
            cases.append((condition, expr))

        if self.current_tok.matches(TT_KEYWORD, 'else'):
            res.register_advancement()
            self.advance()

            else_case = res.register(self.expr())
            if res.error:
                return res

        return res.success(IFNode(cases, else_case))

    def for_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'for'):
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end, "Expected 'for'"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_IDENTIFIER:
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end,
                                   "Expected identifier"))

        var_name = self.current_tok
        res.register_advancement()
        self.advance()

        if self.current_tok.type != TT_EQ:
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end, "Expected '='"))

        res.register_advancement()
        self.advance()

        start_value = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT_KEYWORD, 'to'):
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end, "Expected 'to'"))

        res.register_advancement()
        self.advance()

        end_value = res.register(self.expr())
        if res.error:
            return res

        if self.current_tok.matches(TT_KEYWORD, 'step'):
            res.register_advancement()
            self.advance()

            step_value = res.register(self.expr())
            if res.error:
                return res

        else:
            step_value = None

        if not self.current_tok.matches(TT_KEYWORD, 'then'):
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end,
                                   "Expected 'then'"))

        res.register_advancement()
        self.advance()
        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advance()

            body = res.register(self.statements())
            if res.error:
                return res

            if not self.current_tok.matches(TT_KEYWORD, 'end'):
                return res.failure(
                    InvalidSyntaxError(self.current_tok.pos_start,
                                       self.current_tok.pos_end,
                                       "Expected 'end'"))

            res.register_advancement()
            self.advance()
            return res.success(
                ForNode(var_name, start_value, end_value, step_value, body,
                        True))

        body = res.register(self.expr())
        if res.error:
            return res
        return res.success(
            ForNode(var_name, start_value, end_value, step_value, body, False))

    def while_expr(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'while'):
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end,
                                   "Expected 'while'"))

        res.register_advancement()
        self.advance()
        condition = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT_KEYWORD, 'then'):
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end,
                                   "Expected 'then'"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_NEWLINE:
            res.register_advancement()
            self.advamce()

            body = res.register(self.statements())
            if res.error:
                return res

            if not self.current_tok.matches(TT_KEYWORD, 'end'):
                return res.failure(
                    InvalidSyntaxError(self.current_tok.pos_start,
                                       self.current_tok.pos_end,
                                       "Expected 'end'"))

            res.register_advancement()
            self.advance()
            return res.success(WhileNode(condition, body, True))

        body = res.register(self.expr())
        if res.error:
            return res

        return res.success(WhileNode(condition, body, False))

    def call(self):
        res = ParseResult()
        atom = res.register(self.atom())
        if res.error:
            return res

        if self.current_tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            arg_nodes = []

            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()

            else:
                arg_nodes.append(res.register(self.expr()))
                if res.error:
                    return res.failure(
                        InvalidSyntaxError(
                            self.current_tok.pos_start,
                            self.current_tok.pos_end,
                            "Expected ')', 'define', 'if', 'for', 'while', 'function', int, float, identifier, '+', '-', '(', '[' or 'not'"
                        ))
                while self.current_tok.type == TT_COMMA:
                    res.register_advancement()
                    self.advance()
                    arg_nodes.append(res.register(self.expr()))
                    if res.error:
                        return res

                if self.current_tok.type != TT_RPAREN:
                    return res.failure(
                        InvalidSyntaxError(self.current_tok.pos_start,
                                           self.current_tok.pos_end,
                                           "Expected ',' or ')'"))
                res.register_advancement()
                self.advance()
            return res.success(CallNode(atom, arg_nodes))
        return res.success(atom)

    def list_expr(self):
        res = ParseResult()
        element_nodes = []
        pos_start = self.current_tok.pos_start.copy()

        if self.current_tok.type != TT_LSQUARE:
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end, "Expected '['"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_RSQUARE:
            res.register_advancement()
            self.advance()
        else:
            element_nodes.append(res.register(self.expr()))
            if res.error:
                return res.failure(
                    InvalidSyntaxError(
                        self.current_tok.pos_start, self.current_tok.pos_end,
                        "Expected ']', 'define', 'if', 'for', 'while', 'function', int, float, identifier, '+', '-', '(', '[' or 'not'"
                    ))
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()
                element_nodes.append(res.register(self.expr()))
                if res.error:
                    return res

            if self.current_tok.type != TT_RSQUARE:
                return res.failure(
                    InvalidSyntaxError(self.current_tok.pos_start,
                                       self.current_tok.pos_end,
                                       "Expected ',' or ']'"))
            res.register_advancement()
            self.advance()
        return res.success(
            ListNode(element_nodes, pos_start,
                     self.current_tok.pos_end.copy()))

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_INT, TT_FLOAT):
            res.register_advancement()
            self.advance()
            return res.success(NumberNode(tok))

        elif tok.type == TT_STRING:
            res.register_advancement()
            self.advance()
            return res.success(StringNode(tok))

        elif tok.type == TT_IDENTIFIER:
            res.register_advancement()
            self.advance()
            return res.success(VarAccessNode(tok))

        elif tok.type == TT_LPAREN:
            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())
            if res.error:
                return res
            if self.current_tok.type == TT_RPAREN:
                res.register_advancement()
                self.advance()
                return res.success(expr)
            else:
                return res.failure(
                    InvalidSyntaxError(tok.pos_start, tok.pos_end,
                                       "Expected ')'"))

        elif tok.type == TT_LSQUARE:
            list_expr = res.register(self.list_expr())
            if res.error:
                return res
            return res.success(list_expr)

        elif tok.matches(TT_KEYWORD, 'if'):
            if_expr = res.register(self.if_expr())
            if res.error:
                return res
            return res.success(if_expr)

        elif tok.matches(TT_KEYWORD, 'for'):
            for_expr = res.register(self.for_expr())
            if res.error:
                return res
            return res.success(for_expr)

        elif tok.matches(TT_KEYWORD, 'while'):
            while_expr = res.register(self.while_expr())
            if res.error:
                return res
            return res.success(while_expr)

        elif tok.matches(TT_KEYWORD, "function"):
            func_def = res.register(self.func_def())
            if res.error:
                return res
            return res.success(func_def)

        return res.failure(
            InvalidSyntaxError(
                tok.pos_start, tok.pos_end,
                "Expected int, float, identifier, '+', '-', '(', '[', 'if', 'for', 'while' or 'function'"
            ))

    def power(self):
        return self.bin_op(self.call, (TT_POW, ), self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type in (TT_PLUS, TT_MINUS):
            res.register_advancement()
            self.advance()
            factor = res.register(self.factor())
            if res.error:
                return res
            return res.success(UnaryOpNode(tok, factor))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def arith_expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def comp_expr(self):
        res = ParseResult()

        if self.current_tok.matches(TT_KEYWORD, 'not'):
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()

            node = res.register(self.comp_expr())
            if res.error:
                return res
            return res.success(UnaryOpNode(op_tok, node))

        node = res.register(
            self.bin_op(self.arith_expr,
                        (TT_EE, TT_NE, TT_LT, TT_GT, TT_GTE, TT_LTE)))

        if res.error:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected int, float, identifier, '+', '-', '(', '[' or 'not'"
                ))

        return res.success(node)

    def expr(self):
        res = ParseResult()
        if self.current_tok.matches(TT_KEYWORD, 'define'):
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_IDENTIFIER:
                return res.failure(
                    InvalidSyntaxError(self.current_tok.pos_start,
                                       self.current_tok.pos_end,
                                       "Expected identifier"))

            if self.current_tok.value in KEYWORDS or self.current_tok.value in BuiltInFunctionList or self.current_tok.value in BuiltInIdentifierList:
                pos_start = self.current_tok.pos_start.copy()
                res.register_advancement()
                self.advance()
                return res.failure(
                    InvalidSyntaxError(pos_start, self.current_tok.pos_start,
                                       "Identifier is keywords."))

            var_name = self.current_tok
            res.register_advancement()
            self.advance()

            if self.current_tok.type != TT_EQ:
                return res.failure(
                    InvalidSyntaxError(self.current_tok.pos_start,
                                       self.current_tok.pos_end,
                                       "Expected '='"))

            res.register_advancement()
            self.advance()
            expr = res.register(self.expr())

            if res.error:
                return res

            return res.success(VarAssignNode(var_name, expr))

        node = res.register(
            self.bin_op(self.comp_expr,
                        ((TT_KEYWORD, 'and'), (TT_KEYWORD, "or"))))

        if res.error:
            return res.failure(
                InvalidSyntaxError(
                    self.current_tok.pos_start, self.current_tok.pos_end,
                    "Expected 'define', 'if', 'for', 'while', 'function', int, float, identifier, '+', '-', '(', '[' or 'not'"
                ))

        return res.success(node)

    def func_def(self):
        res = ParseResult()

        if not self.current_tok.matches(TT_KEYWORD, 'function'):
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end,
                                   "Expected 'function'"))

        res.register_advancement()
        self.advance()

        if self.current_tok.value in KEYWORDS or self.current_tok.value in BuiltInFunctionList or self.current_tok.value in BuiltInIdentifierList:
            pos_start = self.current_tok.pos_start.copy()
            res.register_advancement()
            self.advance()
            pos_end = self.current_tok.pos_end.copy()
            pos_end.col = pos_end.col - 1
            return res.failure(
                InvalidSyntaxError(pos_start, pos_end,
                                   "Identifier is keywords."))

        if self.current_tok.type == TT_IDENTIFIER:
            # return res.failure(self.current_tok.pos_start, self.current_tok.pos_end, )
            var_name_tok = self.current_tok
            res.register_advancement()
            self.advance()
            if self.current_tok.type != TT_LPAREN:
                return res.failure(
                    InvalidSyntaxError(self.current_tok.pos_start,
                                       self.current_tok.pos_end,
                                       "Expected '('"))
        else:
            var_name_tok = None
            if self.current_tok.type != TT_LPAREN:
                return res.failure(
                    InvalidSyntaxError(self.current_tok.pos_start,
                                       self.current_tok.pos_end,
                                       "Expected identifier or '('"))

        res.register_advancement()
        self.advance()
        arg_name_toks = []

        if self.current_tok.type == TT_IDENTIFIER:
            arg_name_toks.append(self.current_tok)

            res.register_advancement()
            self.advance()
            while self.current_tok.type == TT_COMMA:
                res.register_advancement()
                self.advance()

                if self.current_tok.type != TT_IDENTIFIER:
                    return res.failure(
                        InvalidSyntaxError(self.current_tok.pos_start,
                                           self.current_tok.pos_end,
                                           "Expected identifier"))
                arg_name_toks.append(self.current_tok)
                res.register_advancement()
                self.advance()
            if self.current_tok.type != TT_RPAREN:
                return res.failure(
                    InvalidSyntaxError(self.current_tok.pos_start,
                                       self.current_tok.pos_end,
                                       "Expected ',' or ')'"))
        else:
            if self.current_tok.type != TT_RPAREN:
                return res.failure(
                    InvalidSyntaxError(self.current_tok.pos_start,
                                       self.current_tok.pos_end,
                                       "Expected identifier or ')'"))

        res.register_advancement()
        self.advance()

        if self.current_tok.type == TT_ARROW:
            # return res.failure(
            #     InvalidSyntaxError(self.current_tok.pos_start,
            #                        self.current_tok.pos_end, "Expected '->'"))

            res.register_advancement()
            self.advance()
            body = res.register(self.expr())
            if res.error:
                return res
            return res.success(
                FuncDefNode(var_name_tok, arg_name_toks, body, False))

        if self.current_tok.type != TT_NEWLINE:
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end,
                                   "Expected '->' or NEWLINE"))

        res.register_advancement()
        self.advance()

        body = res.register(self.expr())
        if res.error:
            return res

        if not self.current_tok.matches(TT_KEYWORD, 'end'):
            return res.failure(
                InvalidSyntaxError(self.current_tok.pos_start,
                                   self.current_tok.pos_end, "Expected 'end'"))

        res.register_advancement()
        self.advance()

        return res.success(FuncDefNode(var_name_tok, arg_name_toks, body,
                                       True))

    def bin_op(self, func_a, ops, func_b=None):
        if func_b is None:
            func_b = func_a
        res = ParseResult()
        left = res.register(func_a())
        if res.error:
            return res
        while self.current_tok.type in ops or (self.current_tok.type,
                                               self.current_tok.value) in ops:
            op_tok = self.current_tok
            res.register_advancement()
            self.advance()
            right = res.register(func_b())
            if res.error:
                return res
            left = BinOpNode(left, op_tok, right)

        return res.success(left)


class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None
        self.last_registered_advance_count = 0
        self.advance_count = 0
        self.to_reverse_count = 0

    def register_advancement(self):
        self.last_registered_advance_count = 1
        self.advance_count += 1

    def try_register(self, res):
        if res.error:
            self.to_reverse_count = res.advance_count
            return None
        return self.register(res)

    def register(self, res):
        self.last_registered_advance_count = res.advance_count
        self.advance_count += res.advance_count
        if res.error:
            self.error = res.error
        return res.node

    def success(self, node):
        self.node = node
        return self

    def failure(self, error):
        if not self.error or self.advance_count == 0:

            self.error = error
        return self
