# -*- coding:utf-8 -*-
'''
作者: __init__(PartyParrot)
Github 地址: https://github.com/PartyParrot359
Gitee 地址: https://gitee.com/JUST_SANS
邮件: 2100970361@qq.com
Date: 2021-11-19 13:29:08
最后一次编辑人: __init__(PartyParrot)
LastEditTime: 2021-11-19 16:50:58
'''
# 导入库
from EasyScript.EasyLexer import *
from EasyScript.EasyParser import *
from EasyScript.EasyInterpreter import *
from EasyScript.EasyContext import *
from EasyScript.EasySymbolTable import *
import yaml

# 生成变量表
global_symbol_table = SymbolTable()
global_symbol_table.set('Null', Number.null)   # 设置NULL的值为0
global_symbol_table.set('True', Number.true)   # 设置TRUE的值为1
global_symbol_table.set('False', Number.false)  # 设置FALSE的值为0
global_symbol_table.set('println', BuiltInFunction.println)
global_symbol_table.set('printf', BuiltInFunction.printf)
global_symbol_table.set('str', BuiltInFunction.str)
global_symbol_table.set('type', BuiltInFunction.type)
global_symbol_table.set('int', BuiltInFunction.int)
global_symbol_table.set('input', BuiltInFunction.input)
global_symbol_table.set('clear', BuiltInFunction.clear)
global_symbol_table.set('is_num', BuiltInFunction.is_number)
global_symbol_table.set('is_str', BuiltInFunction.is_string)
global_symbol_table.set('is_list', BuiltInFunction.is_list)
global_symbol_table.set('is_func', BuiltInFunction.is_function)
global_symbol_table.set('append', BuiltInFunction.append)
global_symbol_table.set('pop', BuiltInFunction.pop)
global_symbol_table.set('extend', BuiltInFunction.extend)
releaseMode = yaml.safe_load(open("EasyScript/config.yml").read())['options']['release-mode']


# 创建函数 run
def run(fn, text):
    # 实例化 Lexer
    lexers = Lexer(fn, text)
    # 获取 tokens 和 error
    tokens, error = lexers.make_tokens()
    if error:
        return None, error
    if not releaseMode:
        print(tokens)

    # 实例化 parser
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error:
        return None, ast.error

    # 实例化 Interpreter
    interpreter = Interpreter()
    context = Context('<program>')
    context.symbol_table = global_symbol_table
    # print(ast.node)
    # print(type(ast.node).__name__)
    result = interpreter.visit(ast.node, context)

    # 返回值和错误
    return result.value, result.error
