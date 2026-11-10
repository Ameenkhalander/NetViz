from content import MODULES, PROTOCOLS
def test_nine_learning_modules_exist():
    assert len(MODULES) >= 9
    for module in MODULES.values():
        for key in ("intro","why","topics","details","lab","interview","refs"):
            assert module[key]
def test_protocol_rows_are_complete():
    assert len(PROTOCOLS) >= 15
    assert all(len(row)==5 and all(str(x).strip() for x in row) for row in PROTOCOLS)
