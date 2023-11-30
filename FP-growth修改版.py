import math

total_count = 0


class treeNode:
    def __init__(self) -> None:
        self.name = None
        self.child = []
        self.parent = None
        self.value = 0

    def addChild(self, temp):
        self.child.append(temp)
        temp.parent = self


class header_table_item:
    def __init__(self, input_name, input_cnt) -> None:
        self.cnt = input_cnt
        self.name = input_name
        self.links = []

    def __repr__(self):
        return f"item(name={self.name}, cnt={self.cnt})"


def insert_data_into_tree(root, item_list, item_list_cnt, header_table):
    temp = root
    for num in item_list:
        found_in_children = False
        for child in temp.child:
            if child.name == num:
                temp = child
                temp.value += item_list_cnt
                found_in_children = True
                break
        if not found_in_children:
            new_child = treeNode()
            new_child.value = item_list_cnt
            new_child.name = num
            temp.addChild(new_child)
            temp = new_child
            for header_table_item in header_table:
                if header_table_item.name == new_child.name:
                    header_table_item.links.append(new_child)
                    break


def get_prefix_path(temp):
    path = []
    temp = temp.parent
    while temp.parent is not None:  # Stop one level before root
        path.append(temp.name)
        temp = temp.parent
    return path[::-1]  # Reverse to get path from root to node


# debug
def print_tree(root, indent=""):
    print(indent + str(root.name) + " " + str(root.value))
    for child in root.child:
        print_tree(child, indent + "    ")


# debug
def print_header_table(header_table):
    for item in header_table:
        print(item)
        for link in item.links:
            print(get_prefix_path(link))


# turn data into ordered
def ordered_frequent_item_set(header_table, data):
    ordered_list = list()
    for item in header_table:
        if item.name in data:
            ordered_list.append(item.name)
    return ordered_list


def is_single_path(root):
    temp = root
    while temp is not None:
        if len(temp.child) > 1:
            return False
        elif len(temp.child) == 1:
            temp = temp.child[0]  # Continue with the only child
        else:
            temp = None  # No more children, end the loop
    return True


def get_path_size(root):
    if root is None or len(root.child) == 0:
        return 0
    else:
        size = 0
        node = root.child[0]  # Start from the first child of root
        while node is not None:
            size += 1
            if len(node.child) > 0:
                node = node.child[0]  # Continue with the only child
            else:
                node = None  # End the loop when no more children
        return size


def C(n, m):
    return math.factorial(n) // (math.factorial(m) * math.factorial(n - m))


def count_ans(root):
    ret = 0
    size = get_path_size(root)
    for item_set_size in range(1, min(size, 5)):
        for left_size in range(0, item_set_size):
            ret += C(size - 1, left_size) * C(
                size - 1 - left_size, item_set_size - left_size
            )
    return ret


# datas => a dict of {frozenset : cnt}
def build_FP_tree(datas, min_support_num):
    header_table = []
    root = treeNode()

    # scan datas first, build header table items
    # data => frozenset, datas[data] = cnt
    for data in datas:
        for num in data:
            have_add_flag = 0
            for table_item in header_table:
                if table_item.name == num:
                    table_item.cnt += datas[data]
                    have_add_flag = 1
                    break
            if have_add_flag == 0:
                header_table.append(header_table_item(num, datas[data]))

    # remove header table item that cnt < min_support_num
    new_header_table = []
    for table_item in header_table:
        if int(table_item.cnt) >= int(min_support_num):
            new_header_table.append(table_item)
    header_table = new_header_table

    # sort
    header_table = sorted(header_table, key=lambda item: (-item.cnt, item.name))

    # scan datas second, get frequent item set for each data, then insert this item set into root
    for data in datas:
        insert_data_into_tree(
            root,
            ordered_frequent_item_set(header_table, data),
            datas[data],
            header_table,
        )

    # if FP tree only have one path
    if is_single_path(root):
        global total_count
        total_count += len(header_table) * count_ans(root)  # Update this line

    # FP tree mining
    else:
        for item in reversed(header_table):
            end_list = item.links
            sub_data = {}
            for node in end_list:
                prefix_path = frozenset(get_prefix_path(node))
                if prefix_path in sub_data:
                    sub_data[prefix_path] += node.value
                else:
                    sub_data[prefix_path] = node.value
            build_FP_tree(sub_data, item.cnt * 0.8)


# read original data
with open("mushroom.dat", "r") as file:
    datas = {}

    for line in file:
        numbers = line.split()
        temp_set = frozenset(numbers)
        if temp_set in datas:
            datas[temp_set] += 1
        else:
            datas[temp_set] = 1

    build_FP_tree(datas, 813)
    print(total_count)
