

class Match:
    def __init__(self, row):
        self.data = [float(x) if str.isnumeric(x) else x for x in row[:-1]]
        self.match = int(row[-1])


def load_match(filename):
    rows = []
    with open(filename, 'r') as file:
        lines = file.read()
        for line in lines.split('\n'):
            rows.append(Match(line.split(',')))
    return rows

