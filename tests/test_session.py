import os
from datetime import datetime
from http_session_file import FileStore
from cromlech.marshallers import PickleMarshaller
from freezegun import freeze_time


def alter_file_mtime(path):
    now = datetime.now()
    os.utime(str(path), times=(now.timestamp(), now.timestamp()))


def test_store_defaults(tmp_path):
    path = tmp_path / 'sessions'
    store = FileStore(path, 300)
    assert path.exists()
    assert store.TTL == 300
    assert store.marshaller is PickleMarshaller


def test_store_paths(tmp_path):
    path = tmp_path / 'sessions'
    store = FileStore(path, 300)
    path = store.get_session_path('test')
    assert path == tmp_path / 'sessions' / 'test'
    assert path.exists() is False

    fsess = store.get_session_file('test')
    assert fsess is None


def test_store_getter_setter(tmp_path):
    path = tmp_path / 'sessions'
    store = FileStore(path, 300)
    assert store.get('test') == {}

    store.set('test', {"key": "value"})
    assert store.get_session_file('test').exists()
    assert store.get('test') == {"key": "value"}


def test_timeout(tmp_path):
    path = tmp_path / 'sessions'
    store = FileStore(path, 300)

    with freeze_time("2021-10-20 12:00:00"):
        # We alter the file modification time for test purposes
        store.set('test', {"key": "value"})
        alter_file_mtime(store.get_session_file('test'))

    with freeze_time("2021-10-20 12:02:00"):
        assert store.get_session_file('test').exists()

    with freeze_time("2021-10-20 12:07:01"):
        assert store.get_session_file('test') is None


def test_touch(tmp_path):
    path = tmp_path / 'sessions'
    store = FileStore(path, 300)

    with freeze_time("2021-10-20 12:00:00"):
        # We alter the file modification time for test purposes
        store.set('test', {"key": "value"})
        alter_file_mtime(store.get_session_file('test'))

    with freeze_time("2021-10-20 12:02:01"):
        store.touch('test')

    with freeze_time("2021-10-20 12:05:01"):
        assert store.get_session_file('test').exists()


def test_flush(tmp_path):
    path = tmp_path / 'sessions'
    store = FileStore(path, 300)

    with freeze_time("2021-10-20 12:00:00"):
        # We alter the file modification time for test purposes
        store.set('test', {"key": "value"})
        alter_file_mtime(store.get_session_file('test'))

    with freeze_time("2021-10-20 12:05:00"):
        # We alter the file modification time for test purposes
        store.set('another_test', {"key": "value"})
        alter_file_mtime(store.get_session_file('another_test'))

    with freeze_time("2021-10-20 12:06:00"):
        files = list(store)
        assert len(files) == 2
        assert tmp_path / 'sessions' / 'test' in files
        assert tmp_path / 'sessions' / 'another_test' in files

        store.flush_expired_sessions()
        assert list(store) == [
            tmp_path / 'sessions' / 'another_test',
        ]

    with freeze_time("2021-10-20 12:10:01"):
        store.flush_expired_sessions()
        assert list(store) == []
