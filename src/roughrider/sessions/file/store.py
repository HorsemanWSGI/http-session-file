import time
from pathlib import Path
from datetime import datetime
from cromlech.session import Store
from cromlech.marshallers import Marshaller, PickleMarshaller


class FileStore(Store):
    """ Files based HTTP session.
    """
    def __init__(self,
                 root: Path,
                 delta: int,
                 marshaller: Type[Marshaller] = PickleMarshaller):
        root.mkdir(parents=True, exist_ok=False)
        self.delta = delta  # timedelta in seconds.
        self.marshaller = marshaller

    def get_session_path(self, sid):
        """Override to add a prefix or a namespace, if needed.
        """
        return self.root / sid

    def __iter__(self):
        """Override to add a prefix or a namespace, if needed.
        """
        for child in self.root.iterdir():
            yield child

    def get_session_file(self, sid, epoch: int = None):
        """Override to customize the behavior, add events or other
        kind of decorum.
        """
        path = self.get_session_path(sid)
        if path.exists():
            if epoch is None:
                epoch = time.time()
            fmod = path.stat().st_mtime
            if (fmod + self.delta) < epoch:
                path.unlink()  # File expired, we remove
                return None
            return path
        return None

    def get(self, sid):
        session_path = self.get_session_file(sid)
        if session_path is None:
            return self.new()
        session = self.marshaller.load_from(session_path)
        return session

    def set(self, sid: str, data: dict):
        assert isinstance(data, dict)
        session_path = self.get_session_path(sid)  # it might not exist
        self.marshaller.dump_to(data, session_path)

    def touch(self, sid: str):
        session_path = self.get_session_path(sid)
        if session_path is not None:
            session_path.touch()

    def clear(self, sid: str):
        session = self.get_session_path(sid)
        session.unlink()

    delete = clear

    def flush_expired_sessions(self):
        """This method should be used in an asynchroneous task.
        Running this during an HTTP request/response cycle, synchroneously
        can result in low performances.
        """
        now = time.time()
        for path in iter(self):
            fmod = path.stat().st_mtime
            if (fmod + self.delta) < now:
                path.unlink()  # File expired, we remove
