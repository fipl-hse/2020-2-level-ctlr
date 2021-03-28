def get_month(m):
    if m.find('нвар') != -1:
        return '01'
    if m.find('рал') != -1:
        return '02'
    if m.find('арт') != -1:
        return '03'
    if m.find('прел') != -1:
        return '04'
    if m.find('Ма') != -1:
        return '05'
    if m.find('Июн') != -1:
        return '06'
    if m.find('Июл') != -1:
        return '07'
    if m.find('Авгус') != -1:
        return '08'
    if m.find('Сент') != -1:
        return '09'
    if m.find('Окт') != -1:
        return '10'
    if m.find('Нояб') != -1:
        return '11'
    if m.find('Декаб') != -1:
        return '12'
    return ''
