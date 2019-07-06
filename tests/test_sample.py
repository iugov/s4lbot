from src import sample


class TestSample:
    def test_say_hello(self):
        assert "hello!" == sample.say_hello()
