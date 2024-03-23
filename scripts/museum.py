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

import blogger as b
import global_values as gv
import fair


document_root = b.SecSpec(
    name="root",
    dst_path="docs",
    url_prefix=gv.PREFIX,
    src_path="scripts/original_content",
    sub_secs=[fair.root],
    generate_index=False,
    generate_qr=False,
    generate_qrpages=False,
    rules=b.Rules(
        nuke_dst_path=True,
        copy_selected_data=True,
        recursive_convert=False,
        recursive_copy=False,
    )
)


def main():
    b.generator(
        document_root,
        qr_pages_rows=1,
        qr_pages_cols=4,
        # verbose=True
    )


if __name__ == "__main__":
    main()
