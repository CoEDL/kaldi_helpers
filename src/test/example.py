from scripts.clean import x


class TestMain:

    @pytest.fixture(scope="class")
    def main_app(self):
        # Setup
        app = QApplication(sys.argv)
        app.setWindowIcon(ApplicationIcon())
        yield app
        # Teardown
        app = None

    def test_primary_window_exists(self, main_app: QApplication):
        assert isinstance(main_app, QApplication)
        main = PrimaryWindow(main_app)
        assert main is not None and isinstance(main, PrimaryWindow)