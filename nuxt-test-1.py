import json

def read_json():
    with open("titanic-info.json", "rb") as fh:
        return json.load(fh)

def process_json(data:list):
    resp = []

    def resolve_value(value):

        if type(value) is list:
            return [resolve_value(data[index] if type(index)==int else index) for index in value]

        elif type(value) is dict:
            processed_value = {}
            for k, v in value.items():
                processed_value[k] = resolve_value(data[v])
            return processed_value

        return value

    for entry in data:
        if type(entry) is dict:
            details = {}
            for key, index in entry.items():
                details[key] = resolve_value(data[index])

            resp.append(details)
        if resp:
            return resp[0]

    #return resp[0]

def print_json(data:dict):
    out = json.dumps(
        data, indent=4
    )
    print(out)

def dump_json(data):
    with open("resp-2.json", "w") as fh:
        json.dump(data, fh, indent=4)

if __name__=="__main__":
    data = read_json()
    data1 = process_json(data)
    #print_json(data1)
    dump_json(data1)