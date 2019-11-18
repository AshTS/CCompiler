class Context:
    def __init__(self, visited_files=None, defines=None):
        self.visited_files = visited_files if visited_files is not None else []
        self.defines = defines if defines is not None else {}

    def define(self, name, value, file_name, line, col, func_data):
        self.defines[name] = value, (file_name, line, col), func_data


def preprocess(data,file_name="[unknown]", context=None):
    if context is None:
        context = Context([file_name], {})

    line_map = {}

    current_line = 1

    result = ""

    for i, line in enumerate(data.split("\n")):
        if line.strip().startswith("#"):
            pre_chars, line = line.index("#"), line.strip()
            item = line.split(" ")[0][1:]
            args = line.split(" ")[1:]
            
            if item == "include":
                included_file_name = args[0][1:-1]

                if included_file_name in context.visited_files:
                    # print("Preprocessor Skipping file '%s', already visited" % included_file_name)
                    continue

                context.visited_files.append(included_file_name)

                included_file_data = open(included_file_name, "r").read()

                processed, included_line_map, _ = preprocess(included_file_data, included_file_name, context)
                result += processed + "\n"


                for key in included_line_map.keys():
                    line_map[key - 1 + current_line] = included_line_map[key]

                current_line += len(processed.split("\n")) - 1

            elif item == "define":
                title = args[0]
                i = 1
                if "(" in title:
                    while not ")" in title:
                        title += " " + args[i]
                        i += 1

                value = " ".join(args[i:])

                func_data = None

                if "(" in title:
                    func_data = [item.strip() for item in title.split("(")[1].split(")")[0].split(",")]

                context.define(title.split("(")[0], value, file_name, i, pre_chars + 9 + len(args[0]), func_data)
        else:
            result += line + "\n"

        line_map[current_line] = (i + 1, file_name)

        current_line += 1

    return result, line_map, context

