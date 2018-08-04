def book_records_by_classification(book_records):
    if book_records == []:
        return []
    first_item = book_records[0].copy()
    first_item['index'] = 1
    ret = [[first_item]]
    index = 2
    for book_record in book_records[1:]:
        next_item = book_record.copy()
        next_item['index'] = index
        if book_record['classification'] == ret[-1][-1]['classification']:
            ret[-1].append(next_item)
        else:
            ret.append([next_item])
        index += 1
    return ret
