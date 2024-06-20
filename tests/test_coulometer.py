from koolstof import coulometer as ksc

filename = "tests/data/test_coulometer.txt"


def test_get_coulometer():
    dic = ksc.read_coulometer(filename)
    samples = ksc.get_samples(dic)
