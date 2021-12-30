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
        result = result[:-1]
        for literal in result.split(' IS '):
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
            'up_more_right': [(0, 1), (30, 1), (60, 0)],
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

        'force': {
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


def get_subset_names(var):
    subsets = {
        'pa': ['up_more_right', 'up_right', 'up', 'up_left', 'up_more_left', 'down_more_left', 'down_left', 'down',
               'down_right', 'down_more_right'],
        'pv': ['cw_fast', 'cw_slow', 'stop', 'ccw_slow', 'ccw_fast'],
        'force': ['left_fast', 'left_slow', 'stop', 'right_slow', 'right_fast'],
        'cp': ['left_far', 'left_near', 'stop', 'right_near', 'right_far'],
        'cv': ['left_fast', 'left_slow', 'stop', 'right_slow', 'right_fast']
        }
    return subsets[var]


def get_centroid(points):
    shapes = []  # (Area, center)
    for i, point in enumerate(points):
        if i == 0:
            continue
        xp = points[i - 1][0]
        dp = points[i - 1][1]
        x = point[0]
        d = point[1]
        # Each part of shape is a kind of trapezoid containing one triangle and one rectangle
        shapes.append((dp * (x - xp), float(x + xp) / 2))
        shapes.append((float(d - dp) * (x - xp) / 2, float(2 * x + xp) / 3))

    sum_of_areas = 0
    accumulator = 0
    for shape in shapes:
        accumulator += shape[0] * shape[1]
        sum_of_areas += shape[0]

    if sum_of_areas == 0:
        return 0
    return accumulator / sum_of_areas


def get_x_of(y, point1, point2):
    # y = ax + b
    a, b = get_line(point1, point2)
    return (y - b) / a


def get_y_of(x, point1, point2):
    # y = ax + b
    a, b = get_line(point1, point2)
    return a * x + b


def get_line(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    slope = float(y2 - y1) / float(x2 - x1)
    bias = y1 - slope * x1
    return slope, bias


def get_value_from_points(points, value):
    for i, point in enumerate(points):
        if i == 0:
            continue
        x, d = point
        xp, dp = points[i - 1]
        if xp <= value < x:
            return get_y_of(value, point, points[i - 1])
    return 0.0


def mix_points(points):
    new_points = []
    for i, point in enumerate(points):
        if i == 0 or i == len(points) - 1:
            new_points.append(point)
            continue

        prev_point = points[i - 1]
        # If current point is behind previous point
        if point[0] < prev_point[0]:
            a, b = get_line(prev_point, points[i - 2])
            c, d = get_line(point, points[i + 1])
            new_x = (d - b) / (a - c)
            new_y = get_y_of(new_x, point, points[i + 1])
            del new_points[-1]
            new_points.append((new_x, new_y))
        else:
            new_points.append(point)

    return new_points


def cut_points(points, max_value):
    new_points = []
    if max_value == 0:
        return []
    for i, point in enumerate(points):
        x = point[0]
        d = point[1]

        if d > max_value:
            if i == 0:
                new_x = get_x_of(max_value, point, points[1])
                new_points.append((x, max_value))
                new_points.append((new_x, max_value))
            elif i == len(points) - 1:
                new_x = get_x_of(max_value, points[-2], point)
                new_points.append((x, max_value))
                new_points.append((new_x, max_value))
            else:
                new_x1 = get_x_of(max_value, point, points[i + 1])
                new_x2 = get_x_of(max_value, points[i - 1], point)
                new_points.append((new_x2, max_value))
                new_points.append((new_x1, max_value))
        else:
            new_points.append(point)

    return new_points


print cut_points([(0, 0), (1, 1), (2, 0)], 0.5)
