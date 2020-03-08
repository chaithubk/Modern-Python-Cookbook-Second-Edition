"""Python Cookbook 2nd ed.

Chapter 9, recipe 2, Replacing a file while preserving the previous version

Note: Output from this is used in Chapter 4 examples.
"""

from pathlib import Path
import csv
from dataclasses import dataclass, asdict, fields
from typing import Callable, Any


@dataclass
class Quotient:
    numerator: int
    denominator: int


def save_data(output_path: Path, data: Quotient) -> None:
    with output_path.open('w', newline='') as output_file:
        headers = [f.name for f in fields(Quotient)]
        writer = csv.DictWriter(output_file, headers)
        writer.writeheader()
        writer.writerow(asdict(data))

def safe_write(output_path: Path, data: Quotient) -> None:
    ext = output_path.suffix
    output_new_path = output_path.with_suffix(f'{ext}.new')
    save_data(output_new_path, data)

    # Clear any previous .{ext}.old
    output_old_path = output_path.with_suffix(f'{ext}.old')
    try:
        output_old_path.unlink()
    except FileNotFoundError as ex:
        # No previous file
        pass

    # Try to preserve current as old
    try:
        output_path.rename(output_old_path)
    except FileNotFoundError as ex:
        # No previous file. That's okay.
        pass

    # Try to replace current .{ext} with new .{ext}.new
    try:
        output_new_path.rename(output_path)
    except IOError as ex:
        # Possible recovery...
        output_old_path.rename(output_path)

test_step1 = """
>>> d1 = Quotient(355, 113)
>>> safe_write(Path("data")/"quotient.csv", d1)
>>> (Path("data")/"quotient.csv").read_text()
'numerator,denominator\\n355,113\\n'
"""

test_step2 = """
>>> d2 = Quotient(87, 32)
>>> safe_write(Path("data")/"quotient.csv", d2)
>>> (Path("data")/"quotient.csv").read_text()
'numerator,denominator\\n87,32\\n'
>>> (Path("data")/"quotient.csv.old").read_text()
'numerator,denominator\\n355,113\\n'
"""

# Bonus: Decorator implementation

from typing import Callable

Writer = Callable[..., None]

def safe(function: Writer) -> Writer:
    def concrete_function(output_path: Path, *args):
        ext = output_path.suffix
        output_new_path = output_path.with_suffix(f'{ext}.new')

        function(output_path, *args)

        output_old_path = output_path.with_suffix(f'{ext}.old')
        try:
            output_old_path.unlink()
        except FileNotFoundError as ex:
            pass

        try:
            output_path.rename(output_old_path)
        except FileNotFoundError as ex:
            pass

        try:
            output_new_path.rename(output_path)
        except IOError as ex:
            output_old_path.rename(output_path)
    return concrete_function

@safe
def write_quotient(output_path: Path, data: Quotient) -> None:
    with output_path.open('w', newline='') as output_file:
        headers = [f.name for f in fields(Quotient)]
        writer = csv.DictWriter(output_file, headers)
        writer.writeheader()
        writer.writerow(asdict(data))

__test__ = {n: v for n, v in locals().items() if n.startswith("test_")}
