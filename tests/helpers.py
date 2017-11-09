import tornado.concurrent


def future_returning(result):
    future = tornado.concurrent.Future()
    future.set_result(result)
    return future


def future_raising(exception):
    future = tornado.concurrent.Future()
    future.set_exception(exception)
    return future
