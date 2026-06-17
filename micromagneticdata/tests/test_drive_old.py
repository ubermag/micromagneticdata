from micromagneticdata.testing.drive import *  # noqa: F403


class TestDrive:
    def setup_method(self):
        self.dirname = os.path.join(os.path.dirname(__file__), "test_sample")
        self.name = "rectangle"
        self.data = md.Data(name=self.name, dirname=self.dirname)
