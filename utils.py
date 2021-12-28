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
