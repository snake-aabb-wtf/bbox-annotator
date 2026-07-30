"""
顶层冒烟测试：把整个项目“串起来”导入一次。
main.py 会 import config / selector / annotator，所以只要这一条通过，
就说明四个 Python 程序文件之间没有导入期错误、依赖都能装得上、语法都合法。

这是最接近“程序能不能跑起来”的一道闸门。
"""
def test_import_everything():
    import config   # noqa: F401
    import annotator  # noqa: F401
    import selector  # noqa: F401  (需要 tkinter)
    import main     # noqa: F401  (串联全部模块)


def test_main_exposes_entrypoint():
    import main
    assert callable(main.main)
