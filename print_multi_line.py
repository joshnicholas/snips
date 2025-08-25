def print_list_multiline(strings, per_line=5):
    print("[", end="") 
    for i in range(0, len(strings), per_line):
        line = ", ".join(repr(s) for s in strings[i:i+per_line])
        if i + per_line >= len(strings):
            print(line + "]")
        else:
            print(line + ",")
