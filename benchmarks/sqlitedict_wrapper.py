from sqlitedict import SqliteDict


class SqliteDict_Wrapper(SqliteDict):
    """ Dictionary that uses a low amount of memory. Use as built-in dict. """

    def __init__(self, commit_every=1000):
        super().__init__(':memory:', outer_stack=False)
        self.opcount = 0
        self.commit_every = commit_every

    def _on_write_op(self):
        self.opcount += 1
        if self.opcount > self.commit_every:
            self.commit()
            self.opcount = 0

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self._on_write_op()

    def __delitem__(self, key):
        super().__delitem__(key)
        self._on_write_op()

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)
        self.commit()

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default
