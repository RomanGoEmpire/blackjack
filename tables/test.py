def flatten_array(arr):
    result = []
    for item in arr:
        if isinstance(item, list):
            result.extend(flatten_array(item))
        else:
            result.append(item)
    return result

nested_array = [[11, 3], [[10, 4], [5, 6]]]
flattened_array = flatten_array(nested_array)
print(flattened_array)
