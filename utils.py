def read_rules():
    rules = []
    with open('controllers/simple.fcl') as f:
        rule_str = []
        is_rule = False
        for line in f:
            line = line.strip()
            if line.startswith('RULE '):
                is_rule = True
            if is_rule:
                rule_str.append(line)
                if line.endswith(';'):
                    rules.append(' '.join(rule_str))
                    is_rule = False
                    rule_str = []

    fixed_rules = {}
    for rule_str in rules:
        i = rule_str.index(':')
        rule_name = rule_str[:i]
        i = rule_str.index('IF')
        rule_str = rule_str[i + 3:]
        condition, result = [i.strip() for i in rule_str.split(' THEN ')]

        condition_list = []
        for mul in condition.split(' OR '):
            ands = []
            for s in mul.split(' AND '):
                equality = []
                for literal in s.split(' IS '):
                    if literal[0] == '(' or literal[0] == ')':
                        literal = literal[1:]
                    if literal[-1] == '(' or literal[-1] == ')':
                        literal = literal[:-1]
                    equality.append(literal)
                ands.append(tuple(equality))
            condition_list.append(ands)

        result_list = []
        for literal in result.split(' IS '):
            literal = literal[:-1]
            if literal[0] == '(' or literal[0] == ')':
                literal = literal[1:]
            if literal[-1] == '(' or literal[-1] == ')':
                literal = literal[:-1]
            result_list.append(literal)

        current_rule = {'IF': condition_list, 'THEN': tuple(result_list)}
        fixed_rules[rule_name] = current_rule

    return fixed_rules


def load_fuzzy_sets():
    return {
            'pa': {
                'up_more_right': [(0, 0), (30, 1), (60, 0)],
                'up_right': [(30, 0), (60, 1), (90, 0)],
                'up': [(60, 0), (90, 1), (120, 0)],
                'up_left': [(90, 0), (120, 1), (150, 0)],
                'up_more_left': [(120, 0), (150, 1), (180, 0)],
                'down_more_left': [(180, 0), (210, 1), (240, 0)],
                'down_left': [(210, 0), (240, 1), (270, 0)],
                'down': [(240, 0), (270, 1), (300, 0)],
                'down_right': [(270, 0), (300, 1), (330, 0)],
                'down_more_right': [(300, 0), (330, 1), (360, 0)]
            },

            'pv': {
                'cw_fast': [(-200, 1), (-100, 0)],
                'cw_slow': [(-200, 0), (-100, 1), (0, 0)],
                'stop': [(-100, 0), (0, 1), (100, 0)],
                'ccw_slow': [(0, 0), (100, 1), (200, 0)],
                'ccw_fast': [(100, 0), (200, 1)],
            },

            'forc': {
                'left_fast': [(-100, 0), (-80, 1), (-60, 0)],
                'left_slow': [(-80, 0), (-60, 1), (0, 0)],
                'stop': [(-60, 0), (0, 1), (60, 0)],
                'right_slow': [(0, 0), (60, 1), (80, 0)],
                'right_fast': [(60, 0), (80, 1), (100, 0)],
            },

            'cp': {
                'left_far': [(-10, 1), (-5, 0)],
                'left_near': [(-10, 0), (-2.5, 1), (0, 0)],
                'stop': [(-2.5, 0), (0, 1), (2.5, 0)],
                'right_near': [(0, 0), (2.5, 1), (10, 0)],
                'right_far': [(5, 0), (10, 1)],
            },

            'cv': {
                'left_fast': [(-5, 1), (-2.5, 0)],
                'left_slow': [(-80, 0), (-60, 1), (0, 0)],
                'stop': [(-60, 0), (0, 1), (60, 0)],
                'right_slow': [(0, 0), (60, 1), (80, 0)],
                'right_fast': [(60, 0), (80, 1), (100, 0)],
            }
        }