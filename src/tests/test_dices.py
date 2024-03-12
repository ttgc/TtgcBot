#!usr/bin/env python3
#-*-coding:utf-8-*-

##    TtgcBot - a bot for discord
##    Copyright (C) 2017-2024  Thomas PIOT
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program. If not, see <http://www.gnu.org/licenses/>


from dices import Expression, ExpressionPatterns


class TestDices:
    def test_parenthesis(self) -> None:
        assert ExpressionPatterns.PARENTHESIS('foo (test) bar') == 'foo test bar'

    def test_dice(self) -> None:
        d100 = ExpressionPatterns.DICE('1d100')
        assert d100.isnumeric()
        assert int(d100) >= 1
        assert int(d100) <= 100

        d100 = ExpressionPatterns.DICE('1D100')
        assert d100.isnumeric()
        assert int(d100) >= 1
        assert int(d100) <= 100

        d100 = ExpressionPatterns.DICE('5d100')
        assert d100.isnumeric()
        assert int(d100) >= 5
        assert int(d100) <= 500

        assert ExpressionPatterns.DICE('10d1') == '10'

    def test_dice_spe(self) -> None:
        assert ExpressionPatterns.DICE_SPE(r'1d{foo,bar}') in ['foo', 'bar']
        assert ExpressionPatterns.DICE_SPE(r'1d{foo, bar}') in ['foo', 'bar']
        assert ExpressionPatterns.DICE_SPE(r'1d{foo}') == 'foo'
        assert ExpressionPatterns.DICE_SPE(r'5d{foo}') == 'foo, foo, foo, foo, foo'

    def test_mul(self) -> None:
        assert int(float(ExpressionPatterns.MUL('5*5'))) == 25

    def test_div(self) -> None:
        assert float(ExpressionPatterns.DIV('5/2')) == 2.5

    def test_divent(self) -> None:
        assert int(ExpressionPatterns.DIVENT('5//2')) == 2

    def test_mod(self) -> None:
        assert float(ExpressionPatterns.MOD('5%2')) == 1

    def test_add(self) -> None:
        assert int(float(ExpressionPatterns.ADD('1+1'))) == 2

    def test_sub(self) -> None:
        assert int(float(ExpressionPatterns.SUB('1-1'))) == 0

    def test_expressions(self) -> None:
        assert int(float(Expression('4 - 5 * (5+4-2d1)')())) == -31
        assert Expression(r'5+1d{foo}')() == '5+foo'
