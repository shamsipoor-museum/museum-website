# Copyright 2023 MohammadMohsen Akbarpoor Darabi (M. MAD)

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

from typing import Union, Collection

import global_values as gv
FA_IR_PREFIX = gv.PREFIX + "fa_IR/"


def persian_stringifier(c: Union[None, str, Collection[str]]) -> str:
    """stringify a collection of strings using persian commas if it's not a string already
    if c is None; "-" will be returned"""
    return "-" if c is None else c if isinstance(c, str) else "، ".join(c)
