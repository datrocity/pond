from datetime import date

from pond.yaml import yaml_dump, yaml_load


def test_load_yaml():
    values = yaml_load("""
        value: 123
        version: 2021-02-03
    """)
    assert values['value'] == 123
    assert values['version'] == '2021-02-03'


def test_dump():
    values = {
        'value': 123,
        'version': date(year=2021, month=2, day=3),
    }

    dumped = yaml_dump(values)

    expected = """
value: 123
version: 2021-02-03
    """.strip()
    assert dumped.strip() == expected.strip()
