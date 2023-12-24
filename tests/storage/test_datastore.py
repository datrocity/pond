from pond.conventions import TXT_ENCODING
from pond.storage.datastore import Datastore


class DummyDataStore(Datastore):
    def __init__(self, read_content):
        super().__init__(id='foostore')
        self.read_content = read_content

    def open(self, path, mode):
        pass

    def read(self, path):
        return self.read_content.encode(TXT_ENCODING)

    def write(self, path, data):
        self.read_content = data.decode(TXT_ENCODING)

    def makedirs(self, uri):
        pass

    def exists(self, uri):
        pass

    def delete(self):
        pass


def test_read_string():
    read_content = 'æɝ'
    store = DummyDataStore(read_content)
    str_ = store.read_string('dummy')
    assert str_ == read_content


def test_write_string():
    store = DummyDataStore('')
    content = 'æɝ'
    store.write_string('dummy/path', content)
    read_content = store.read_string('dummy/path')
    assert read_content == content


def test_read_yaml():
    read_content = """
value: æɝ
version: 2021-02-03
    """.strip()

    store = DummyDataStore(read_content)
    dict_ = store.read_yaml('dummy')

    expected = {
        'value': 'æɝ',
        'version': '2021-02-03',
    }
    assert dict_ == expected


def test_write_yaml():
    content = {
        'value': 'æɝ',
        'version': '2021-02-03',
    }
    store = DummyDataStore('')
    store.write_yaml('dummy', content)
    read_content = store.read_yaml('dummy')

    assert read_content == content


def test_read_json():
    read_content = """
{
   "value": "æɝ",
   "version": "2021-02-03"
}
    """.strip()

    store = DummyDataStore(read_content)
    dict_ = store.read_json('dummy')

    expected = {
        'value': 'æɝ',
        'version': '2021-02-03',
    }
    assert dict_ == expected


def test_write_json():
    content = {
        'value': 'æɝ',
        'version': '2021-02-03',
    }
    store = DummyDataStore('')
    store.write_json('dummy', content)
    read_content = store.read_json('dummy')

    assert read_content == content
