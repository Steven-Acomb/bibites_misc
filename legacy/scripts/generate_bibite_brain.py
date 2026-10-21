def make_layer_snippet(x: int) -> str:
    """
    Return the exact text block the simulator expects for the two new hidden
    neurons tied to input X.

    Parameters
    ----------
    x : int
        Must be ≥ 1.  Values ≤ 0 are rejected.

    Returns
    -------
    str
        A literal string starting with a comma and newline, then the two JSON-ish
        objects with fields populated per the rules:

        - First object:
            Index  = 50 + x
            Inov   = Index + 1
            Desc   = "L1N{x}"
        - Second object:
            Index  = 51 + x
            Inov   = Index + 1
            Desc   = "L2N{x}"
        - All other keys are constant.
    """
    if x < 1:
        raise ValueError("X must be >= 1")

    first_index  = 48 + 2*x
    second_index = 49 + 2*x

    return (
        f",\n    {{\n"
        f'      "Type": 4, \n'
        f'      "Index": {first_index}, \n'
        f'      "Inov": {first_index + 1}, \n'
        f'      "Desc": "L1N{x}", \n'
        f'      "baseActivation": 0.0 \n'
        f"    }},\n    {{\n"
        f'      "Type": 4,\n'
        f'      "Index": {second_index},\n'
        f'      "Inov": {second_index + 1},\n'
        f'      "Desc": "L2N{x}",\n'
        f'      "baseActivation": 0.0\n'
        f"    }}"
    )

def make_connection_snippet(x: int, y: int) -> str:
    """
    Build the exact text block of connection objects the simulator expects.

    Parameters
    ----------
    x : int
        The value to use for every `"NodeOut"`.
    y : int
        Offset added to every base innovation number
        (base innovations run from 1‥33).

    Returns
    -------
    str
        A single formatted string identical in layout to the example, but with
        `"NodeOut"` = x and each `"Inov"` = base + y.
    """
    # Fixed order of input-side node indices from the exemplar
    base_node_in = [
        21, 20, 18, 17, 16, 15, 11, 23, 12, 6, 3, 9, 0,
        10, 22, 13, 14, 19, 32, 24, 25, 26, 27, 28, 29,
        1, 2, 4, 5, 7, 8, 30, 31,
    ]

    blocks = []
    
    offset = 63

    for idx, node_in in enumerate(base_node_in, start=1):
        # Innovation number with requested offset
        inov = idx + y + offset
        indent_outer = "" if idx == 1 else "    "
        indent_inner = indent_outer + "  "  # two spaces deeper

        block = (
            f"{indent_outer}{{\n"
            f'{indent_inner}"Inov": {inov},\n'
            f'{indent_inner}"NodeIn": {node_in},\n'
            f'{indent_inner}"NodeOut": {x},\n'
            f'{indent_inner}"Weight": 0.0,\n'
            f'{indent_inner}"En": true\n'
            f"{indent_outer}}}"
        )
        blocks.append(block)

    # Add a comma after every object except the last
    snippet = ",\n".join(blocks)
    return snippet

def make_inverse_connection_snippet(node_in: int, y: int = 0) -> str:
    """
    Like `make_connection_snippet`, but:
      * `NodeIn` is a single constant (the first argument).
      * `NodeOut` cycles through a fixed list of constants.
      * Innovation numbers start at 50 and each gets the offset `y`.

    Parameters
    ----------
    node_in : int
        The value to repeat for every `"NodeIn"`.
    y : int, optional
        Offset added to each base innovation number (default 0).

    Returns
    -------
    str
        A formatted string that starts with `",\n"` so it can be appended
        directly after a previous object list.
    """
    base_node_out = [
        33, 45, 39, 34, 41, 38, 47, 36, 46, 37,
        35, 40, 42, 43, 44
    ]
    start_inov = 107  # first innovation number for this block
    offset = 15

    blocks = []
    for idx, node_out in enumerate(base_node_out, start=start_inov):
        inov = idx + (y-1) * offset
        indent_outer = "    "      # four spaces
        indent_inner = indent_outer + "  "  # six spaces
        block = (
            f"{indent_outer}{{\n"
            f'{indent_inner}"Inov": {inov},\n'
            f'{indent_inner}"NodeIn": {node_in},\n'
            f'{indent_inner}"NodeOut": {node_out},\n'
            f'{indent_inner}"Weight": 0.0,\n'
            f'{indent_inner}"En": true\n'
            f"{indent_outer}}}"
        )
        blocks.append(block)

    snippet = ",\n".join(blocks)
    # Prepend leading comma + newline so caller can concatenate safely
    return ",\n" + snippet

# print(make_layer_snippet(2)+make_layer_snippet(3)+make_layer_snippet(4)+make_layer_snippet(5)+make_layer_snippet(6))
str = make_layer_snippet(2)+make_layer_snippet(3)+make_layer_snippet(4)+make_layer_snippet(5)+make_layer_snippet(6)
filename = "nodes.txt"    
with open(filename, 'w', encoding='utf-8') as f:
        f.write(str)

# print(make_connection_snippet(49, 0))

# print(make_connection_snippet(52, 1))
x_vals = [2, 3, 4, 5, 6]
# x_vals = [2, 3]
str = ""
for x in x_vals:
    x_input = 48 + 2*x
    y_input = x-1
    str = str + make_connection_snippet(x_input, y_input)

filename = "connections.txt"    
with open(filename, 'w', encoding='utf-8') as f:
        f.write(str)


# output connections
x_vals = [2, 3, 4, 5, 6]
str = ""
for x in x_vals:
    x_input = 49 + 2*x
    y_input = x-1
    str = str + make_inverse_connection_snippet(x_input, y_input)

filename = "connections_out.txt"    
with open(filename, 'w', encoding='utf-8') as f:
        f.write(str)
