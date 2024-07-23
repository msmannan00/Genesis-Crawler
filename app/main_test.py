import multiprocessing


def test_function(ss):
    for i in range(1999):
        print(ss, flush=True)


t1 = multiprocessing.Process(target=test_function("xx1"))
t2 = multiprocessing.Process(target=test_function("yy1"))
t1.start()
t2.start()