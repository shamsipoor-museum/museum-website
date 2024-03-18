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

from typing import Union

from jinja2 import Template

import blogger as b
from . import common as c
from . import parts as p
from . import scientists as s


# Reverse


def write_data_to_md(pd: Union[s.ScientistData, p.PartData],
                     template: Template, path: str, mode: str = "w"):
    with open(path, mode) as f:
        f.write(template.render(pd.__dict__))


parts = b.SecSpec(
    name="fa_ir_parts",
    dst_path="docs/fa_IR/parts",
    url_prefix=p.PREFIX,
    src_path="scripts/original_content/fa_IR/parts",
    data_spec=p.PartData,
    dst_template_path="scripts/templates/fa_IR/parts/parts_template.html",
    src_template_path="scripts/templates/fa_IR/parts/parts_template.md",
    data_extractor=p.extract_data_from_md,
    # custom_data_writer=p.write_data,  ## To be removed
    rules=b.Rules(move_selected_data=False),
    # extract_data_from_md=p.extract_data_from_md,
    # write_data_to_html=None,
    # extract_data_from_html=p.extract_data_from_html,
    # write_data_to_md=write_data_to_md,
    index_template_path="scripts/templates/fa_IR/parts/parts_index_template.html",
    index_extractor=p.extract_index_row,
    index_title="فهرست قطعات",
    # custom_index_writer=p.write_index,
    # qr_template_path="scripts/templates/fa_IR/parts/qr_pages_table_template.html",
    qrpages_template_path="scripts/templates/fa_IR/parts/qr_pages_triangle_template.html",
)
scientists = b.SecSpec(
    name="fa_ir_scientists",
    dst_path="docs/fa_IR/scientists",
    url_prefix=s.PREFIX,
    src_path="scripts/original_content/fa_IR/scientists",
    data_spec=s.ScientistData,
    dst_template_path="scripts/templates/fa_IR/scientists/scientists_template.html",
    src_template_path="scripts/templates/fa_IR/scientists/scientists_template.md",
    data_extractor=s.extract_data_from_md,
    # custom_data_writer=s.write_data,  ## To be removed
    rules=b.Rules(move_selected_data=False),
    # extract_data_from_md=s.extract_data_from_md,
    # write_data_to_html=None,
    # extract_data_from_html=s.extract_data_from_html,
    # write_data_to_md=write_data_to_md,
    index_template_path="scripts/templates/fa_IR/scientists/scientists_index_template.html",
    index_extractor=s.extract_index_row,
    index_title="فهرست دانشمندان",
    # custom_index_writer=s.write_index,
    # qr_template_path="scripts/templates/fa_IR/scientists/qr_pages_table_template.html",
    qrpages_template_path="scripts/templates/fa_IR/scientists/qr_pages_triangle_template.html",
)

root = b.SecSpec(
    name="fa_ir",
    dst_path="docs/fa_IR",
    url_prefix=c.FA_IR_PREFIX,
    sub_specs=[parts, scientists],
    rules=b.Rules(
        recursive_convert=False,
        move_selected_data=False,
        recursive_move=False
    )
)
