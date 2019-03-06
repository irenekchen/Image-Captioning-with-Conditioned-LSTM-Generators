import data_cache
import utils as ut
import dataservice
import json

ut.set_debug_mode(True)
dataservice.set_config()

t = {"playerID": "willite01", "nameLast": "Williams", "bats": "R"}
r = data_cache.compute_key("people", {"playerID": "willite01", "nameLast": "Williams", "bats": "R"}, \
                           ['nameLast', "birthCity"])


def test1():
    data_cache.add_to_cache(r, t)
#test1()

def test2():
    result = data_cache.get_from_cache(r)
    print("Result = ", result)
    print(data_cache.check_query_cache("people", t, ['nameLast', "birthCity"]))


#test2()

def test3():

    tmp = { "teamID": "BOS", "yearID": "2004", "playerID": "ortizda01"}
    fields = ["playerID", "teamID", "yearID", "H", "AB", "HR"]
    resource = "Batting"

    for i in range(0,3):
        result = dataservice.retrieve_by_template(resource, tmp, fields=fields)
        print("test1: result[",i,"]=", json.dumps(result))

test3()