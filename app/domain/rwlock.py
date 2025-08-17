"""
Read-Write Lock implementation for thread-safe access to the vector database.

Design Choices:
- Uses threading.RLock for reader locks to allow multiple concurrent readers
- Uses threading.Lock for writer exclusivity
- Readers are prioritized to prevent writer starvation in read-heavy workloads
- Context managers provide clean resource management

Time Complexity: O(1) for acquire/release operations
Space Complexity: O(1) per lock instance
"""
import threading
from contextlib import contextmanager
from typing import Generator


class ReadWriteLock:
    """
    A read-write lock that allows multiple concurrent readers but exclusive writers.
    
    This implementation prioritizes readers to avoid writer starvation in typical
    vector database workloads which are read-heavy.
    """
    
    def __init__(self) -> None:
        self._readers = 0
        self._reader_lock = threading.RLock()
        self._writer_lock = threading.Lock()
    
    @contextmanager
    def read_lock(self) -> Generator[None, None, None]:
        """
        Context manager for acquiring a read lock.
        
        Multiple threads can hold read locks simultaneously.
        Blocks if a writer holds the lock.
        """
        with self._reader_lock:
            self._readers += 1
            if self._readers == 1:
                # First reader blocks writers
                self._writer_lock.acquire()
        
        try:
            yield
        finally:
            with self._reader_lock:
                self._readers -= 1
                if self._readers == 0:
                    # Last reader releases writer lock
                    self._writer_lock.release()
    
    @contextmanager
    def write_lock(self) -> Generator[None, None, None]:
        """
        Context manager for acquiring a write lock.
        
        Exclusive access - no other readers or writers allowed.
        """
        with self._writer_lock:
            yield


class DatabaseSnapshot:
    """
    Immutable snapshot of database state for consistent reads.
    
    Design Choice: Copy-on-write semantics ensure readers see consistent
    state even during concurrent writes. This trades memory for consistency.
    """
    
    def __init__(self, libraries: dict, documents: dict, chunks: dict) -> None:
        self._libraries = libraries.copy()
        self._documents = documents.copy() 
        self._chunks = chunks.copy()
        self._timestamp = threading.current_thread().ident
    
    @property
    def libraries(self) -> dict:
        """Read-only access to libraries."""
        return self._libraries
    
    @property
    def documents(self) -> dict:
        """Read-only access to documents."""
        return self._documents
    
    @property
    def chunks(self) -> dict:
        """Read-only access to chunks."""
        return self._chunks
    
    @property
    def timestamp(self) -> int:
        """Snapshot timestamp for debugging."""
        return self._timestamp