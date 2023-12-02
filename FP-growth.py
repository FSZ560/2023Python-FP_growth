import csv
import itertools
import time


class Node:
    def __init__(self, num, freq, parent):
        self.num = num
        self.freq = freq
        self.parent = parent
        self.child = {}
        self.nxt = None


def getFromFile(name):
    itemSetList = {}
    with open(name, "r") as file:
        reader = csv.reader(file)
        tmp = []
        for line in reader:  # 遍歷每一行資料，加入 list
            line = list(filter(None, line))
            tmp.append(line)
        for item in tmp:
            itemSetList[frozenset(item)] = 1
    return itemSetList


def buildTree(itemSetList, minSup):
    headertb = {}

    for itemSet in itemSetList:
        for item in itemSet:
            headertb[item] = headertb.get(item, 0) + itemSetList[itemSet]

    # remove item less than minSup
    headertb = {i: headertb[i] for i in headertb if headertb[i] >= minSup}

    if len(headertb) == 0:
        return None, None

    freqItemSet = set(headertb.keys())

    for item in headertb:
        headertb[item] = [headertb[item], None]

    fpTreeRoot = Node("Null", 1, None)

    for itemSet, cnt in itemSetList.items():
        item_temp = {}
        for item in itemSet:
            if item in freqItemSet:
                item_temp.update({item: headertb[item][0]})
        # sorting by descending order
        items = [
            i[0]
            for i in sorted(
                item_temp.items(), key=lambda p: (p[1], str(p[0])), reverse=True
            )
        ]
        updateTree(items, fpTreeRoot, headertb, cnt)

    return fpTreeRoot, headertb


def UpdateHeaderTable(item, node):
    while item.nxt != None:
        item = item.nxt
    item.nxt = node


def updateTree(items, node, headertb, freq):
    item = items[0]
    if item not in node.child:
        node.child[item] = Node(item, freq, node)
        if not headertb[item][1]:
            headertb[item][1] = node.child[item]
        else:
            UpdateHeaderTable(headertb[item][1], node.child[item])
    else:
        node.child[item].freq += freq
    if len(items) > 1:
        updateTree(items[1:], node.child[item], headertb, freq)


def traceBackToRoot(node, prefix):
    if node.parent != None:
        prefix.append(node.num)
        traceBackToRoot(node.parent, prefix)


def findprefix(base, headertb):  # 找到所有前綴路徑
    node = headertb[base][1]
    res = {}
    while node != None:
        prefix = []
        traceBackToRoot(node, prefix)
        res.update({frozenset(prefix[1:]): node.freq})
        node = node.nxt
    return res


def mine(headertb, minSup, prefix, freqItemList, mp):
    # sort by frequency in increasing order
    sortedItemList = [
        item[0] for item in sorted(headertb.items(), key=lambda p: str(p[1]))
    ]

    for item in sortedItemList:
        newfreq = prefix.copy()
        newfreq.add(item)

        if len(newfreq) > 5:
            continue

        newfreq = set(sorted(list(newfreq)))
        freqItemList.append(newfreq)

        conditionalBase = findprefix(item, headertb)
        sum_freq = sum(conditionalBase.values())
        mp.update({frozenset(newfreq): sum_freq})

        conditionalTreeRoot, newheadertb = buildTree(conditionalBase, minSup)
        if newheadertb is not None:
            mine(newheadertb, minSup, newfreq, freqItemList, mp)


def associationRule(mp, minConf):
    rules = 0
    for items in mp:
        for n in range(1, len(items)):
            for subset in itertools.combinations(items, n):
                if mp[frozenset(items)] / mp[frozenset(subset)] >= minConf:
                    rules += 1
    return rules


def fpgrowth(fileName, minSup, minConf):
    itemSetList = getFromFile(fileName)
    minSup = len(itemSetList) * minSup
    fpTreeRoot, headertb = buildTree(itemSetList, minSup)
    freqitems = []
    mp = {}
    mine(headertb, minSup, set(), freqitems, mp)
    rules = associationRule(mp, minConf)
    return freqitems, rules


if __name__ == "__main__":
    start_time = time.time()
    freqitems, rules = fpgrowth("mushroom.csv", 0.1, 0.8)
    end_time = time.time()
    print("Total Execution Time: " + str(end_time - start_time) + " seconds.\n")

    cnt = [0, 0, 0, 0, 0]
    for i in freqitems:
        if len(i) == 1:
            cnt[0] += 1
        elif len(i) == 2:
            cnt[1] += 1
        elif len(i) == 3:
            cnt[2] += 1
        elif len(i) == 4:
            cnt[3] += 1
        elif len(i) == 5:
            cnt[4] += 1

    print("Frequent Item Sets:")
    for i in range(0, 5):
        print("|L^" + str(i + 1) + "|=" + str(cnt[i]))

    print("\n滿足條件的 association rule 數目為 :")
    print(rules)
