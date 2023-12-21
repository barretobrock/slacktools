

class TestBotObj:
    def __getattr__(self, item):
        return f'{item}'
