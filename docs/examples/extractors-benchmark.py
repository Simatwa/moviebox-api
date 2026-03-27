from moviebox_api.extractor import JsonDetailsExtractor, TagDetailsExtractor


def read_content(name: str = "avatar.page") -> str:
    with open(f"assets/data/{name}") as fh:
        return fh.read()


content = read_content("avatar.page")


def tag_extractor():
    extractor = TagDetailsExtractor(content)
    extractor.extract_all()

    # print(extractor)


def json_extractor():
    JsonDetailsExtractor.extract(content)


if __name__ == "__main__":
    import json
    from timeit import timeit

    exec_details = {}
    for execution_times in range(0, 100, 10):
        details = {}
        for extractor in [tag_extractor, json_extractor]:
            exec_time = timeit(tag_extractor, number=execution_times)
            extractor_name = extractor.__name__
            details[extractor_name] = exec_time
        exec_details[execution_times] = details
        print(execution_times, details, sep=" : ")

    with open("extractors_benchmark.json", "w") as fh:
        json.dump(exec_details, fh, indent=4)
