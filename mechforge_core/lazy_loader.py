"""
MechForge Lazy Loader

延迟加载模块和组件,优化启动时间:
- 按需导入重型依赖
- 延迟初始化资源密集型组件
- 代理模式包装器

使用示例:
    # 延迟导入重型库
    np = lazy_import("numpy")

    # 延迟初始化组件
    llm_client = LazyLoader(lambda: LLMClient())
"""

import importlib
import threading
from collections.abc import Callable
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class LazyImport:
    """
    延迟导入模块

    使用示例:
        np = LazyImport("numpy")
        arr = np.array([1, 2, 3])  # 第一次使用时才真正导入
    """

    def __init__(self, module_name: str, package: str | None = None):
        self._module_name = module_name
        self._package = package
        self._module: Any | None = None
        self._lock = threading.Lock()

    def _load(self) -> Any:
        """加载模块"""
        if self._module is None:
            with self._lock:
                if self._module is None:
                    self._module = importlib.import_module(self._module_name, self._package)
        return self._module

    def __getattr__(self, name: str) -> Any:
        """代理属性访问"""
        module = self._load()
        return getattr(module, name)

    def __call__(self, *args, **kwargs):
        """如果模块可调用"""
        module = self._load()
        return module(*args, **kwargs)

    def __dir__(self):
        """支持 dir()"""
        module = self._load()
        return dir(module)

    @property
    def __class__(self):
        """返回实际模块类型"""
        module = self._load()
        return module.__class__


class LazyLoader(Generic[T]):
    """
    延迟加载器

    包装一个工厂函数,在第一次访问时才创建实例

    使用示例:
        llm_client = LazyLoader(lambda: LLMClient())

        # 第一次访问时创建实例
        result = llm_client.call("hello")
    """

    def __init__(
        self,
        factory: Callable[[], T],
        name: str | None = None,
    ):
        self._factory = factory
        self._name = name or factory.__name__
        self._instance: T | None = None
        self._lock = threading.Lock()
        self._initialized = False

    def _get_instance(self) -> T:
        """获取或创建实例"""
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._instance = self._factory()
                    self._initialized = True
        return self._instance

    def __getattr__(self, name: str) -> Any:
        """代理所有属性访问"""
        instance = self._get_instance()
        return getattr(instance, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """处理属性设置"""
        if name in ("_factory", "_name", "_instance", "_lock", "_initialized"):
            super().__setattr__(name, value)
        else:
            instance = self._get_instance()
            setattr(instance, name, value)

    def __call__(self, *args, **kwargs) -> Any:
        """代理调用"""
        instance = self._get_instance()
        return instance(*args, **kwargs)

    def __getitem__(self, key) -> Any:
        """代理索引访问"""
        instance = self._get_instance()
        return instance[key]

    def __setitem__(self, key, value) -> None:
        """代理索引设置"""
        instance = self._get_instance()
        instance[key] = value

    def __contains__(self, item) -> bool:
        """代理 contains"""
        instance = self._get_instance()
        return item in instance

    def __iter__(self):
        """代理迭代"""
        instance = self._get_instance()
        return iter(instance)

    def __len__(self) -> int:
        """代理 len"""
        instance = self._get_instance()
        return len(instance)

    def __str__(self) -> str:
        """字符串表示"""
        if self._initialized:
            return str(self._instance)
        return f"<LazyLoader({self._name}) - not loaded>"

    def __repr__(self) -> str:
        """详细表示"""
        if self._initialized:
            return repr(self._instance)
        return f"LazyLoader({self._name}, initialized=False)"

    @property
    def is_loaded(self) -> bool:
        """检查是否已加载"""
        return self._initialized

    def force_load(self) -> T:
        """强制立即加载"""
        return self._get_instance()

    def reset(self) -> None:
        """重置加载器,下次访问时重新创建"""
        with self._lock:
            self._instance = None
            self._initialized = False


class LazyProperty:
    """
    延迟加载属性装饰器

    使用示例:
        class MyClass:
            @LazyProperty
            def expensive_resource(self):
                return ExpensiveResource()
    """

    def __init__(self, getter: Callable):
        self.getter = getter
        self.attr_name = f"_lazy_{getter.__name__}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if not hasattr(instance, self.attr_name):
            value = self.getter(instance)
            setattr(instance, self.attr_name, value)

        return getattr(instance, self.attr_name)

    def __set__(self, instance, value):
        setattr(instance, self.attr_name, value)

    def __delete__(self, instance):
        if hasattr(instance, self.attr_name):
            delattr(instance, self.attr_name)


def lazy_import(module_name: str, package: str | None = None) -> LazyImport:
    """
    延迟导入模块的便捷函数

    示例:
        np = lazy_import("numpy")
        pd = lazy_import("pandas")
        torch = lazy_import("torch")
    """
    return LazyImport(module_name, package)


def lazy_load(factory: Callable[[], T], name: str | None = None) -> LazyLoader[T]:
    """
    创建延迟加载器的便捷函数

    示例:
        llm = lazy_load(lambda: LLMClient(), "LLMClient")
        rag = lazy_load(lambda: RAGEngine(), "RAGEngine")
    """
    return LazyLoader(factory, name)


def lazy_property(func: Callable) -> LazyProperty:
    """
    延迟属性装饰器的便捷函数

    示例:
        class Service:
            @lazy_property
            def database(self):
                return Database()
    """
    return LazyProperty(func)


# ==================== 模块级延迟加载器 ====================

# 重型科学计算库
numpy = lazy_import("numpy")
pandas = lazy_import("pandas")

# 机器学习库
torch = lazy_import("torch")
transformers = lazy_import("transformers")

# 可视化库
matplotlib = lazy_import("matplotlib")
pyvista = lazy_import("pyvista")

# CAE 库
gmsh = lazy_import("gmsh")


# 可选: 创建常用组件的延迟加载器
def get_lazy_llm_client():
    """延迟加载 LLM 客户端"""
    from mechforge_ai.llm_client import LLMClient

    return LLMClient()


def get_lazy_rag_engine():
    """延迟加载 RAG 引擎"""
    from mechforge_ai.rag_engine import RAGEngine

    return RAGEngine()


def get_lazy_database():
    """延迟加载数据库"""
    from mechforge_core.database import get_database

    return get_database()


def get_lazy_cache():
    """延迟加载缓存"""
    from mechforge_core.cache import get_cache

    return get_cache()
