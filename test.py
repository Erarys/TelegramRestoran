old = {'Шашлык Баранина': 1}
new = {'Шашлык Баранина': 1, 'Шашлык Утка': 4}

diff = {}
for key in new:
    old_count = old.get(key, 0)
    new_count = new[key]
    if new_count != old_count:
        diff[key] = new_count - old_count

print(diff)