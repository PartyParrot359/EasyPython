# -*- coding:utf-8 -*-
from EasyScript.EasyPyErrors import *
import EasyScript.EasyInterpreter as EasyInterpreter
from EasyScript.EasyRuntimeResult import *
from EasyScript.EasyContext import *
from EasyScript.EasySymbolTable import *


class Value:
    def __init__(self):
        self.set_pos()
        self.set_context()

    def set_context(self, context=None):
        self.context = context
        return self

    def set_pos(self, pos_start=None, pos_end=None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def added_to(self, other):
        return None, self.illegal_operation(other)

    def subbed_by(self, other):
        return None, self.illegal_operation(other)

    def multed_by(self, other):
        return None, self.illegal_operation(other)

    def dived_by(self, other):
        return None, self.illegal_operation(other)

    def powed_by(self, other):
        return None, self.illegal_operation(other)

    def copy(self):
        raise Exception('No copy method defined')

    def get_comparison_eq(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_ne(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gt(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_lte(self, other):
        return None, self.illegal_operation(other)

    def get_comparison_gte(self, other):
        return None, self.illegal_operation(other)

    def anded_by(self, other):
        return None, self.illegal_operation(other)

    def is_true(self):
        return self.value != 0

    def ored_by(self, other):
        return None, self.illegal_operation(other)

    def notted(self):
        return None, self.illegal_operation()

    def execute(self, args):
        return None, self.illegal_operation()

    def illegal_operation(self, other=None):
        if not other:
            other = self
        return RTError(self.pos_start, other.pos_end, 'Illegal operation',
                       self.context)

    def __repr__(self):
        return str(self.value)


class Number(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def subbed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def multed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def dived_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end,
                                     "Division by zero", self.context)
            return Number(self.value / other.value).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def powed_by(self, other):
        if isinstance(other, Number):
            return Number(self.value**other.value).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def copy(self):
        copy = Number(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def get_comparison_eq(self, other):
        if isinstance(other, Number):
            return Number(int(self.value == other.value)).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def get_comparison_ne(self, other):
        if isinstance(other, Number):
            return Number(int(self.value != other.value)).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def get_comparison_lt(self, other):
        if isinstance(other, Number):
            return Number(int(self.value < other.value)).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def get_comparison_gt(self, other):
        if isinstance(other, Number):
            # if self.value > other.value:
            #     print(self.value)
            #     print(other.value)
            #     print(self.value > other.value)
            #     return Number(1)
            # else:
            #     return Number(0)
            return Number(int(self.value > other.value)).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def get_comparison_lte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value <= other.value)).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def get_comparison_gte(self, other):
        if isinstance(other, Number):
            return Number(int(self.value >= other.value)).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def anded_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value
                              and other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def is_true(self):
        return self.value != 0

    def ored_by(self, other):
        if isinstance(other, Number):
            return Number(int(self.value
                              or other.value)).set_context(self.context), None
        else:
            return None, Value.illegal_operation(self.pos_start, other.pos_end)

    def notted(self):
        return Number(1 if self.value == 0 else 0).set_context(
            self.context), None

    def __repr__(self):
        return str(self.value)


class String(Value):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def added_to(self, other):
        if isinstance(other, String):
            return String(self.value + other.value).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def multed_by(self, other):
        if isinstance(other, Number):
            return String(self.value * other.value).set_context(
                self.context), None
        else:
            return None, Value.illegal_operation(self, other)

    def is_true(self):
        return len(self.value) > 0

    def copy(self):
        copy = String(self.value)
        copy.set_pos(self.pos_start, self.pos_end)
        copy.set_context(self.context)
        return copy

    def __repr__(self):
        return f'"{self.value}"'


class Function(Value):
    def __init__(self, name, body_node, arg_names):
        super().__init__()
        self.name = name or "<anonymous>"
        self.body_node = body_node
        self.arg_names = arg_names

    def execute(self, args):
        res = RTResult()
        interpreter = EasyInterpreter.Interpreter()
        new_context = Context(self.name, self.context, self.pos_start)
        new_context.symbol_table = SymbolTable(new_context.parent.symbol_table)

        if len(args) > len(self.arg_names):
            return res.failure(
                RTError(
                    self.pos_start, self.pos_end,
                    f"{len(args) - len(self.arg_names)} too many args passed into '{self.name}'",
                    self.context))

        if len(args) < len(self.arg_names):
            return res.failure(
                RTError(
                    self.pos_start, self.pos_end,
                    f"{len(self.arg_names) - len(args)} too few args passed into '{self.name}'",
                    self.context))

        for i in range(len(args)):
            arg_name = self.arg_names[i]
            arg_value = args[i]
            arg_value.set_context(new_context)
            new_context.symbol_table.set(arg_name, arg_value)

        value = res.register(interpreter.visit(self.body_node, new_context))
        if res.error:
            return res
        return res.success(value)

    def copy(self):
        copy = Function(self.name, self.body_node, self.arg_names)
        copy.set_context(self.context)
        copy.set_pos(self.pos_start, self.pos_end)
        return copy

    def __repr__(self):
        return f"<function {self.name}>"
