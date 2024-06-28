class State:
    """ State used to label tree nodes """

    __slots__ = ("labels",)

    def __init__(self):
        self.labels = {}
    #判断指定的目标是否存在于当前状态的标记中，如果存在则返回True，否则返回False
    def has_goal(self, goal):
        return goal in self.labels
    #获取指定目标的当前最小成本，即标记中存储的成本值
    def get_cost(self, goal):
        return self.labels[goal][0]
    #获取指定目标的匹配规则，即标记中存储的匹配规则。
    def get_rule(self, goal):
        return self.labels[goal][1]
    #将指定目标的成本和匹配规则存储到标记中。如果该目标已经存在于标记中，且当前成本小于已有成本，则更新成本和匹配规则。如果该目标不存在于标记中，则添加新的标记。
    def set_cost(self, goal, cost, rule):
        """
            Mark that this tree can be matched with a rule for a certain cost
        """
        if self.has_goal(goal):
            if self.get_cost(goal) > cost:
                self.labels[goal] = (cost, rule)
        else:
            self.labels[goal] = (cost, rule)


class BaseMatcher:
    """ Base class for matcher objects. """
    #根据给定的规则rule和树节点tree，返回一个包含所有子节点的列表，即该树节点的所有孩子节点。
    def kids(self, tree, rule):
        return self.kid_functions[rule](tree)
    #根据给定的规则rule，返回该规则所对应的非终结符
    def nts(self, rule):
        return self.nts_map[rule]
    #对给定的树节点tree及其所有子节点进行标记，即根据语法规则给每个节点打上标记
    def burm_label(self, tree):
        """ Label all nodes in the tree bottom up """
        for c in tree.children:
            self.burm_label(c)
        self.burm_state(tree)
    #根据给定的目标goal和树节点tree，应用匹配规则，返回匹配结果。
    def apply_rules(self, tree, goal):
        rule = tree.state.get_rule(goal)
        results = [
            self.apply_rules(kid_tree, kid_goal)
            for kid_tree, kid_goal in zip(
                self.kids(tree, rule), self.nts(rule)
            )
        ]
        return self.pat_f[rule](tree, *results)
