import json
import math
import redis
import tornado.ioloop
import tornado.web


class FactorialService(object):

    def __init__(self, cache):
        self.cache = cache
        self.key = "factorials"

    def calc(self, n):
        s = self.cache.hget(self.key, str(n))
        if s:
            return int(s), True
        s = 1
        for i in range(1, n):
            s *= i
        self.cache.hset(self.key, str(n), str(s))
        return s, False


class PiService(object):

    def __init__(self, cache):
        self.cache = cache
        self.key = "pis"

    def calc(self, n):
        s = self.cache.hget(self.key, str(n))
        if s:
            return float(s), True
        s = 0.0
        for i in range(n):
            s += 1.0 / (2 * i + 1) / (2 * i + 1)
        s = math.sqrt(s * 8)
        self.cache.hset(self.key, str(n), str(s))
        return s, False


class FactorialHandler(tornado.web.RequestHandler):

    def initialize(self, factorial):
        self.factorial = factorial

    def get(self):
        n = int(self.get_argument("n") or 1)
        fact, cached = self.factorial.calc(n)
        result = {
            "n": n,
            "fact": fact,
            "cached": cached
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))


class PiHandler(tornado.web.RequestHandler):

    def initialize(self, pi):
        self.pi = pi

    def get(self):
        n = int(self.get_argument("n") or 1)
        pi, cached = self.pi.calc(n)
        result = {
            "n": n,
            "pi": pi,
            "cached": cached
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(json.dumps(result))


def make_app():
    cache = redis.StrictRedis("localhost", 6379)
    factorial = FactorialService(cache)
    pi = PiService(cache)
    return tornado.web.Application([
        (r"/fact", FactorialHandler, {"factorial": factorial}),
        (r"/pi", PiHandler, {"pi": pi}),
    ])


if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
