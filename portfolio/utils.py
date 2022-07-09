
def construct_name(stack_name, region_name):
    return stack_name + region_name.replace('-', '').upper()
