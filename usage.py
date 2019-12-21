def usage_entry(val, info):
    print("  %s%s" % (val.ljust(15), info))

def usage():
    print("usage: python3 main.py cfile [options]")
    usage_entry("-o outfile", "Sets the file to output assembly code to")
    usage_entry("-A", "Outputs the assembly code to the terminal")
    usage_entry("-O", "Shows the intermediate code before and after optimization")
    usage_entry("-t", "Outputs the parse tree to the console")
    usage_entry("-I", "Outputs post-optimization intermediate code to console")