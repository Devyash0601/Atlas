"""Unit tests for Storage, Cache, Task Queue, Serializers, Monitoring, and Filesystem."""

import time

import pytest

from src.infrastructure.cache.cache_manager import CacheManager, MemoryCache
from src.infrastructure.filesystem.file_manager import (
    FileManager,
    PathResolver,
    SafeFileWriter,
    TemporaryDirectoryManager,
)
from src.infrastructure.monitoring.monitoring import (
    ExecutionProfiler,
    HealthMonitor,
    MemoryTracker,
    MetricsCollector,
    PerformanceTimer,
)
from src.infrastructure.queue.queue_manager import InMemoryTaskQueue, Job, QueueManager
from src.infrastructure.serialization.serializers import (
    BinarySerializer,
    DTOSerializer,
    JsonSerializer,
    YamlSerializer,
)
from src.infrastructure.storage.storage_manager import StorageManager, TemporaryStorage


@pytest.mark.asyncio
async def test_temporary_storage() -> None:
    """Verify TemporaryStorage read and write."""
    storage = TemporaryStorage()
    await storage.write("data.bin", b"hello world")
    data = await storage.read("data.bin")
    assert data == b"hello world"

    with pytest.raises(FileNotFoundError):
        await storage.read("missing.bin")

    manager = StorageManager("artifacts")
    assert manager.artifact_storage.get_artifact_path("out.tif").name == "out.tif"


def test_memory_cache() -> None:
    """Verify MemoryCache set, get, TTL, and delete."""
    cache = MemoryCache()
    cache.set("k1", "v1")
    assert cache.get("k1") == "v1"

    # Expired TTL
    cache.set("k2", "v2", ttl_seconds=-1)
    assert cache.get("k2") is None

    cache.delete("k1")
    assert cache.get("k1") is None

    cm = CacheManager()
    assert cm.memory_cache is not None


@pytest.mark.asyncio
async def test_in_memory_task_queue() -> None:
    """Verify InMemoryTaskQueue enqueue and dequeue."""
    queue = InMemoryTaskQueue()
    job = Job(job_id="j1", task_name="calibrate", payload={"band": 10})
    await queue.enqueue(job)

    dequeued = await queue.dequeue()
    assert dequeued == job
    assert await queue.dequeue() is None

    qm = QueueManager()
    assert qm.default_queue is not None


def test_serializers() -> None:
    """Verify JsonSerializer, YamlSerializer, BinarySerializer, and DTOSerializer."""
    data = {"a": 1, "b": "test"}
    json_str = JsonSerializer.serialize(data)
    assert JsonSerializer.deserialize(json_str) == data

    yaml_str = YamlSerializer.serialize(data)
    assert "a: 1" in yaml_str

    b = BinarySerializer.serialize("test")
    assert BinarySerializer.deserialize(b) == "test"

    dto_json = DTOSerializer.serialize(data)
    assert "a" in dto_json


def test_monitoring_and_filesystem() -> None:
    """Verify HealthMonitor, MetricsCollector, PerformanceTimer, and FileManager."""
    hm = HealthMonitor()
    health = hm.check_health()
    assert health["status"] == "healthy"

    mc = MetricsCollector()
    mc.increment("requests")
    mc.gauge("memory", 500.0)
    metrics = mc.get_metrics()
    assert metrics["counters"]["requests"] == 1

    timer = PerformanceTimer()
    with timer.measure():
        time.sleep(0.01)
    assert timer.elapsed_seconds > 0.0

    prof = ExecutionProfiler()
    prof.record_step("step_1", 0.5)

    assert MemoryTracker.get_memory_usage_mb() > 0.0

    temp_dir_mgr = TemporaryDirectoryManager()
    assert temp_dir_mgr.path.exists()
    temp_dir_mgr.cleanup()

    target_file = PathResolver.resolve("./artifacts/test_safe.txt")
    SafeFileWriter.write_text(target_file, "safe content")
    assert target_file.read_text(encoding="utf-8") == "safe content"
    target_file.unlink(missing_ok=True)

    fm = FileManager("artifacts")
    assert fm.artifact_paths is not None
