# License: MIT
# Copyright © 2025 Frequenz Energy-as-a-Service GmbH

# pylint: disable=too-many-lines

r"""Utilities for testing client implementations.

Based on:
https://github.com/frequenz-floss/frequenz-client-microgrid-python/blob/v0.17.x/tests/util.py
"""

from __future__ import annotations

import asyncio
import functools
import gc
import importlib
import inspect
import itertools
import logging
import sys
from collections.abc import AsyncIterable, AsyncIterator, Awaitable, Callable, Iterable
from contextlib import AsyncExitStack, ContextDecorator, aclosing
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Generic, Protocol, TypeVar, get_args, get_origin
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from frequenz.client.base.client import BaseApiClient
from grpc import StatusCode
from grpc.aio import AioRpcError, Channel, Metadata

_logger = logging.getLogger(__name__)

StubT = TypeVar("StubT")
"""Type variable for the gRPC stub type."""

ClientT = TypeVar("ClientT", bound=BaseApiClient[Any])
"""Type variable for the client type."""


@dataclass(frozen=True, kw_only=True)
class ApiClientTestCase:
    """A single test case for a gRPC client method."""

    client_args: tuple[Any, ...]
    """The positional arguments to use when calling the client method being tested."""

    client_kwargs: dict[str, Any]
    """The keyword arguments to use when calling the client method being tested."""

    assert_stub_method_call: Callable[[Any], None]
    """The assertion function to validate the gRPC request done by the client.

    The assertion function takes the actual gRPC request that was done, and should
    make assertions on it to validate that it matches the expected request.
    """

    grpc_response: Any
    """The response or exception to use to mock the gRPC call.

    If this is an exception, it will be raised when the gRPC call is made.
    If this is a value, it will be returned as the response.
    """

    assert_client_result: (
        Callable[[Any], None] | Callable[[Any], Awaitable[None]] | None
    ) = None
    """The assertion function to validate the result returned by the client.

    The assertion function takes the actual result returned by the client method,
    and it should make assertions on it to validate that it matches the expected
    result.

    This is only used if the gRPC call does not raise an exception.
    """

    assert_client_exception: Callable[[Exception], None] | None = None
    """The assertion function to validate the exception raised by the client.

    The assertion function takes the actual exception raised by the client method,
    and it should make assertions on it to validate that it matches the expected
    exception.

    This is only used if the gRPC call raises an exception.
    """

    def __post_init__(self) -> None:
        """Post-initialization checks for the TestCase class."""
        if self.assert_client_result is None and self.assert_client_exception is None:
            raise ValueError(
                "Either assert_client_result or assert_client_exception must be provided."
            )
        if (
            self.assert_client_result is not None
            and self.assert_client_exception is not None
        ):
            raise ValueError(
                "Only one of assert_client_result or assert_client_exception must be provided."
            )


@dataclass(frozen=True, kw_only=True)
class ApiClientTestCaseSpec:
    """A specification for a test case.

    This is used to load the test case data from a file and run the test.
    """

    name: str
    """The name of the test case."""

    client_method_name: str
    """The name of the gRPC client method being tested."""

    path: Path
    """The absolute path to the test case file."""

    relative_path: Path
    """The test case file path relative to current working directory."""

    def __str__(self) -> str:
        """Return a string representation of the test case specification."""
        return self.name

    def load_test_module(self) -> Any:
        """Return the loaded test case module from the test case file."""
        module_name = self.path.stem
        if module_name in sys.modules:
            raise ValueError(
                f"The module name for test case {self.name} is already in use"
            )

        # Register the module name with pytest to allow for better error reporting
        # when the test case fails.
        pytest.register_assert_rewrite(module_name)

        # We load the module as a top-level module to avoid requiring adding
        # `__init__.py` files to the test directories. We make sure to unload
        # the module (and other modules that might have been loaded by the test
        # case) after the test case is run to avoid polluting the module namespace.
        original_modules = sys.modules.copy()
        original_sys_path = sys.path.copy()
        sys.path.insert(0, str(self.path.parent))
        try:
            module = importlib.import_module(module_name)
        except ImportError as exc:
            raise ImportError(
                f"Test case {self.name} could not be imported from {self.relative_path}, "
                f"make sure the file exists and is a valid Python module: {exc}"
            ) from exc
        finally:
            sys.path = original_sys_path
            sys.modules = original_modules
            importlib.invalidate_caches()
            gc.collect()

        return module

    def load_test_case(self) -> ApiClientTestCase:
        """Return the loaded test case from the test case file."""
        module = self.load_test_module()

        required_attrs = ["assert_stub_method_call", "grpc_response"]
        if missing_attrs := [
            attr for attr in required_attrs if not hasattr(module, attr)
        ]:
            raise AttributeError(
                f"Test case file {self.relative_path} is missing required attributes: "
                + ", ".join(missing_attrs)
            )

        try:
            test_case = ApiClientTestCase(
                client_args=getattr(module, "client_args", ()),
                client_kwargs=getattr(module, "client_kwargs", {}),
                assert_stub_method_call=module.assert_stub_method_call,
                grpc_response=module.grpc_response,
                assert_client_result=getattr(module, "assert_client_result", None),
                assert_client_exception=getattr(
                    module, "assert_client_exception", None
                ),
            )
        except ValueError as exc:
            raise ValueError(
                f"Test case file {self.relative_path} is invalid: {exc}"
            ) from exc

        return test_case

    async def test_call(
        self,
        *,
        client: ClientProtocol,
        stub_method_name: str,
        call_client_method: Callable[
            [ClientProtocol, str, ApiClientTestCase, AsyncExitStack],
            Awaitable[tuple[MagicMock, Any, Exception | None]],
        ],
        exit_stack: AsyncExitStack,
    ) -> None:
        """Run a test for a unary-unary gRPC call."""
        _logger.debug(
            "Running test case %r for `%s()` (%s)",
            self.name,
            self.client_method_name,
            stub_method_name,
        )
        test_case = self.load_test_case()
        _logger.debug("Loaded test case %r from %s", self.name, self.relative_path)
        client_should_raise = test_case.assert_client_exception is not None

        # Call the client method and collect the result/exception
        stub_method_mock, client_result, client_raised_exception = (
            await call_client_method(client, stub_method_name, test_case, exit_stack)
        )

        if client_raised_exception is not None:
            if not client_should_raise:
                # Expected a result, but got an exception. Test premise failed.
                # We raise an AssertionError here to indicate that the test case
                # failed, but we chain it to the original exception to keep the
                # original traceback.
                # We need to check this before running the assert_stub_method_call() because
                # if an exception was raised, the stub method might not have been
                # called at all.
                _logger.debug(
                    "Raising AssertionError because the client raised an unexpected exception: %r",
                    client_raised_exception,
                )
                raise AssertionError(
                    f"{self.relative_path}: The client call to method {self.client_method_name}() "
                    f"raised an exception {client_raised_exception!r}, but a result was expected "
                    "(the test case provided a assert_client_result() function and not a "
                    "assert_client_exception() function)"
                ) from client_raised_exception

            _logger.debug(
                "The client raised an expected exception, calling `assert_client_exception(%r)`",
                client_raised_exception,
            )
            # Expected an exception, and got one, so run the user's
            # assertion function on the exception before we validate the
            # gRPC call, because if the wrong exception was raised, the stub
            # method might not have been called at all.
            # We also chain the exception to the original exception to keep the
            # original traceback for a better debugging experience.
            assert test_case.assert_client_exception is not None
            try:
                test_case.assert_client_exception(client_raised_exception)
            except AssertionError as err:
                raise err from client_raised_exception

        # Validate the gRPC stub call was made correctly
        # This will report any failed assertions as a test FAIL, and any other
        # unexpected exception as a test ERROR, always pointing to the exact
        # location where the issue originated.
        test_case.assert_stub_method_call(stub_method_mock)

        if client_raised_exception is None:
            if client_should_raise:
                # Expected an exception, but got a result. Test premise failed.
                pytest.fail(
                    f"{self.relative_path}: The client call to method "
                    f"{self.client_method_name}() didn't raise the expected exception "
                    f"{test_case.grpc_response!r}, instead it returned {client_result!r}",
                    pytrace=False,
                )

            # Expected a result, and got one, so run the user's assertion
            # function on the result.
            elif test_case.assert_client_result is None:
                pytest.fail(
                    f"{self.relative_path}: The client method "
                    f"{self.client_method_name}() returned a result, but an "
                    "exception was expected (the test case provided a "
                    "assert_client_exception() function and not a "
                    "assert_client_result() function)",
                    pytrace=False,
                )

            if inspect.iscoroutinefunction(test_case.assert_client_result):
                _logger.debug("Awaiting `assert_client_result(%r)`", client_result)
                async with asyncio.timeout(60):
                    await test_case.assert_client_result(client_result)
            else:
                _logger.debug("Calling `assert_client_result(%r)`", client_result)
                test_case.assert_client_result(client_result)

    async def test_unary_unary_call(
        self,
        client: ClientProtocol,
        stub_method_name: str,
    ) -> None:
        """Run a test for a unary-unary gRPC call."""
        async with AsyncExitStack() as exit_stack:
            await self.test_call(
                client=client,
                stub_method_name=stub_method_name,
                call_client_method=self.call_unary_method,
                exit_stack=exit_stack,
            )

    async def test_unary_stream_call(
        self,
        client: ClientProtocol,
        stub_method_name: str,
    ) -> None:
        """Run a test for a unary-stream gRPC call."""
        async with AsyncExitStack() as exit_stack:
            await self.test_call(
                client=client,
                stub_method_name=stub_method_name,
                call_client_method=self.call_stream_method,
                exit_stack=exit_stack,
            )

    async def call_unary_method(
        self,
        client: ClientProtocol,
        stub_method_name: str,
        test_case: ApiClientTestCase,
        _: AsyncExitStack,
    ) -> tuple[AsyncMock, Any, Exception | None]:
        """Call a unary method on the client."""
        _logger.debug("Preparing stub gRPC unary call `%s()`", stub_method_name)
        # Prepare the mock for the gRPC stub method
        stub_method_mock = AsyncMock(name=stub_method_name)
        if isinstance(test_case.grpc_response, Exception):
            stub_method_mock.side_effect = test_case.grpc_response
        else:
            stub_method_mock.return_value = test_case.grpc_response
        _logger.debug(
            "Patching %s.%s with %s", client.stub, stub_method_name, stub_method_mock
        )
        setattr(client.stub, stub_method_name, stub_method_mock)

        # Call the client method and collect the result/exception
        client_method = getattr(client, self.client_method_name)
        # We use a separate variable for the result if it is an exception to be able
        # to support weird cases where the method actually returns an exception
        # instead of raising it.
        client_result: Any = None
        client_raised_exception: Exception | None = None
        try:
            _logger.debug(
                "Calling client method `%s(*%r, **%r)`",
                self.client_method_name,
                test_case.client_args,
                test_case.client_kwargs,
            )
            client_result = await client_method(
                *test_case.client_args, **test_case.client_kwargs
            )
            _logger.debug("Client method result: %r", client_result)
        except Exception as err:  # pylint: disable=broad-exception-caught
            _logger.debug("Client method raised an exception: %r", err)
            client_raised_exception = err

        return (stub_method_mock, client_result, client_raised_exception)

    async def call_stream_method(
        self,
        client: ClientProtocol,
        stub_method_name: str,
        test_case: ApiClientTestCase,
        exit_stack: AsyncExitStack,
    ) -> tuple[MagicMock, Any, Exception | None]:
        """Call a stream method on the client."""
        _logger.debug("Preparing stub gRPC stream call `%s()`", stub_method_name)
        stub_method_mock = MagicMock(name=stub_method_name)

        if isinstance(test_case.grpc_response, Exception):
            _logger.debug(
                "`grpc_response` is an exception, setting as side_effect: %r",
                test_case.grpc_response,
            )
            stub_method_mock.side_effect = test_case.grpc_response
        else:

            def create_response_wrapper(*_: Any, **__: Any) -> AsyncIterator[Any]:
                """Create a response wrapper for the gRPC response."""
                wrapper = _IterableResponseWrapper(test_case.grpc_response)
                exit_stack.push_async_exit(aclosing(wrapper))
                return wrapper

            stub_method_mock.side_effect = create_response_wrapper
        _logger.debug(
            "Patching %s.%s with %s", client.stub, stub_method_name, stub_method_mock
        )
        setattr(client.stub, stub_method_name, stub_method_mock)

        # Call the client method and collect the result/exception
        client_method = getattr(client, self.client_method_name)
        # We use a separate variable for the result if it is an exception to be able
        # to support weird cases where the method actually returns an exception
        # instead of raising it.
        client_result: Any = None
        client_raised_exception: Exception | None = None
        try:
            _logger.debug(
                "Calling client method `%s(*%r, **%r)`",
                self.client_method_name,
                test_case.client_args,
                test_case.client_kwargs,
            )
            client_result = client_method(
                *test_case.client_args, **test_case.client_kwargs
            )
            _logger.debug("Client method result: %r", client_result)
        except Exception as err:  # pylint: disable=broad-exception-caught
            _logger.debug("Client method raised an exception: %r", err)
            client_raised_exception = err

        # Yield control to allow the gRPC streamer to start running
        await asyncio.sleep(0)

        return (stub_method_mock, client_result, client_raised_exception)


def get_test_specs(
    client_method_name: str,
    *,
    tests_dir: str | Path,
    suffixes: Iterable[str] = ("_case",),
) -> Iterable[ApiClientTestCaseSpec]:
    """Get all test names for a specific stub call.

    Args:
        client_method_name: The name of the client method being tested.
        tests_dir: The directory where the test cases are located (inside the
            `client_method_name` sub-directory).
        suffixes: The file suffixes to look for.

    Returns:
        A iterable of test case specs.

    Raises:
        ValueError: If the test directory does not exist or is not a directory,
            the `test_cases_subdir` is not a relative path, or if no test files
            are found in the test directory.
    """
    tests_dir = Path(tests_dir)
    if not tests_dir.is_absolute():
        raise ValueError(f"{tests_dir} must be an absolute path")

    test_dir = tests_dir / client_method_name
    if not test_dir.exists():
        raise ValueError(f"Tests directory {test_dir} does not exist")
    if not test_dir.is_dir():
        raise ValueError(f"Tests directory {test_dir} is not a directory")

    specs = list(
        itertools.chain(
            (
                ApiClientTestCaseSpec(
                    name=p.stem[: -len(suffix)],
                    client_method_name=client_method_name,
                    path=p.resolve(),
                    relative_path=p.relative_to(Path.cwd()),
                )
                for suffix in suffixes
                for p in test_dir.glob(f"*{suffix}.py")
            )
        )
    )
    if not specs:
        globs = [f"*{suffix}.py" for suffix in suffixes]
        raise ValueError(
            f"No test files found in {test_dir} matching {', '.join(globs)}"
        )

    return specs


class ClientProtocol(Protocol):
    """Protocol for client objects with a stub property."""

    @property
    def stub(self) -> Any:
        """Return the gRPC stub."""
        ...  # pylint: disable=unnecessary-ellipsis


def make_grpc_error(
    code: StatusCode,
    *,
    initial_metadata: Metadata = Metadata(),
    trailing_metadata: Metadata = Metadata(),
    details: str | None = None,
    debug_error_string: str | None = None,
) -> AioRpcError:
    """Create a gRPC error for testing purposes."""
    return AioRpcError(
        code=code,
        initial_metadata=initial_metadata,
        trailing_metadata=trailing_metadata,
        details=details,
        debug_error_string=debug_error_string,
    )


# generic_cls uses Any because it doesn't really take a `type` (which might be
# what looks more intuitive), technically is a `typing._GenericAlias`, but this
# is not a public API and we don't want to depend on it. There is also
# `types.GenericAlias` but this one is only used for built-in generics, like
# `list[int]`, so we can't use it either.
@functools.lru_cache(maxsize=1024)
def is_subclass_of_generic(cls: type[Any], generic_cls: Any) -> bool:
    """Return whether `cls` is a subclass of a parameterized generic `generic_cls`.

    Check at runtime whether `cls` is a subclass of a parameterized generic
    `generic_cls`., e.g. `is_subclass_generic(DerivedInt, GenericBase[int])`.

    Args:
        cls: The class to check.
        generic_cls: The parameterized generic type to check against.

    Returns:
        True if `cls` is a subclass of `generic_cls`, False otherwise.

    Raises:
        TypeError: If `generic_cls` is not a parameterized generic type.
    """
    # Check if 'generic_cls' is actually a parameterized generic type
    # (like list[int], GenericBase[str], etc.).
    # get_origin returns None for non-generics or non-parameterized generics.
    origin = get_origin(generic_cls)
    if origin is None:
        raise TypeError(f"generic_cls {generic_cls!r} must be a parameterized generic")

    # First check the raw generic relationship (e.g., is DerivedInt a subclass
    # of GenericBase?).
    if not issubclass(cls, origin):
        return False

    # Inspect __orig_bases__ throughout the MRO (Method Resolution Order).
    # This handles inheritance chains correctly (sub-sub classes).
    # We iterate through getmro(cls) to check not just direct parents, but all
    # ancestors.
    for base in inspect.getmro(cls):
        # __orig_bases__ stores the base classes *as they were written*,
        # including type parameters. Might not exist on all classes (like 'object').
        # getattr avoids an AttributeError if __orig_bases__ is missing.
        # Python3.12 provides types.get_original_bases(cls) to get __orig_bases__,
        # this can be updated when we drop support for older versions.
        for orig_base in getattr(base, "__orig_bases__", ()):
            # Check if the origin of this specific original base matches our
            # target origin AND if the arguments match our target arguments.
            # get_args returns a tuple, so this correctly handles multi-generic
            # bases by comparing tuples element-wise (e.g., (str, int) == (str,
            # int)).
            if get_origin(orig_base) is origin and get_args(orig_base) == get_args(
                generic_cls
            ):
                return True

    return False


class patch_client_class(  # pylint: disable=invalid-name
    ContextDecorator, Generic[ClientT, StubT]
):
    """Patches the client class for testing.

    This avoids the class to really connect anywhere, and creates a mock
    channel and stub instead.

    It can be used as a context manager or decorator.

    Example: Usage as a context manager

        ```python
        @patch_client_class(SomeApiClient, SomeApiStub)
        def test_some_function(client_class: SomeApiClient):
            client = client_class(...)
            client.stub.some_method.return_value = ...
            # Your test code here
        ```

    Example: Usage as a decorator
        ```python
        def test_some_function():
            with patch_client_class(SomeApiClient, SomeApiStub) as client_class:
                client = client_class(...)
                client.stub.some_method.return_value = ...
                # Your test code here
        ```
    """

    def __init__(self, client_class: type[ClientT], stub_class: type[StubT]) -> None:
        """Context manager that patches the client for testing.

        Args:
            client_class: The client class to patch.
            stub_class: The stub class to patch.
        """
        # We need the type ignores here because:
        # 1. mypy doesn't consider types hashable (needed for the
        #    is_subclass_of_generic cache), but they are, based on their memory
        #    address, which is enough for us.
        # 2. mypy expect classes, TypeVar or other type expressions, but we are
        #    using a *regular variable* here. In general this is wrong, and
        #    can't be properly type checked, but it does what it should at
        #    runtime.
        assert is_subclass_of_generic(
            client_class, BaseApiClient[stub_class]  # type: ignore[valid-type]
        )
        self._client_class: type[ClientT] = client_class
        self._patched_client_class = patch.object(
            client_class, "connect", autospec=True, side_effect=self._fake_connect
        )

    def __enter__(self) -> type[ClientT]:
        """Enter the context manager."""
        self._patched_client_class.__enter__()
        return self._client_class

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        """Exit the context manager."""
        self._patched_client_class.__exit__(*args, **kwargs)

    def _fake_connect(
        self,
        client: ClientT,
        server_url: str | None = None,
        auth_key: str | None = None,  # pylint: disable=unused-argument
        sign_secret: str | None = None,  # pylint: disable=unused-argument
    ) -> None:
        """Fake connect method that does nothing."""
        # pylint: disable=protected-access
        if server_url is not None and server_url != client._server_url:  # URL changed
            client._server_url = server_url
        elif client.is_connected:
            return
        client._channel = MagicMock(name="_channel", spec=Channel)
        # We don't spec the stub because we would need the `AsyncStub` for that,
        # but it only exists for type hints, so it can't be used at runtime.
        client._stub = MagicMock(name="_stub")
        # pylint: enable=protected-access


async def _iter_to_async_iter(it: Iterable[Any]) -> AsyncIterator[Any]:
    """Return an async iterator from an iterable."""
    for item in it:
        yield item


class _IterableResponseWrapper(AsyncIterator[Any]):
    """Wrap a response to make it an async iterator.

    Supports
    """

    def __init__(self, response: Any) -> None:
        """Initialize the wrapper with the response."""
        self._response = response
        self._iter_is_async = False
        self._iter_is_generator = False
        self._iter: Any

        if inspect.isasyncgenfunction(response):
            _logger.debug(
                "`grpc_response` is an async generator function: %r", response
            )
            self._iter_is_async = True
            self._iter_is_generator = True
            self._iter = response()
        elif inspect.isgeneratorfunction(response):
            _logger.debug("`grpc_response` is a generator function: %r", response)
            self._iter_is_generator = True
            self._iter = response()
        elif inspect.isasyncgen(response):
            _logger.debug("`grpc_response` is an async generator: %r", response)
            self._iter_is_async = True
            self._iter_is_generator = True
            self._iter = response
        elif inspect.isgenerator(response):
            _logger.debug("`grpc_response` is a generator: %r", response)
            self._iter_is_generator = True
            self._iter = response
        elif isinstance(response, AsyncIterable):
            _logger.debug("`grpc_response` is an async iterable: %r", response)
            self._iter_is_async = True
            self._iter = aiter(response)
        # We check for str and bytes here because they are iterable, but it
        # would be very unlikely that users want to use them as iterator.
        # If they do, they can just use grpc_response = iter([...]) to explicitly
        # create an iterator from it.
        elif isinstance(response, (str, bytes)):
            _logger.debug(
                "`grpc_response` is a string or bytes, wrapping in a list as an iterator: %r",
                response,
            )
            self._iter = iter([response])
        elif isinstance(response, Iterable):
            _logger.debug("`grpc_response` is an iterable: %r", response)
            self._iter = iter(response)
        else:
            _logger.debug(
                "`grpc_response` is not iterable, wrapping in a list as an iterator: %r",
                response,
            )
            self._iter = iter([response])

    def __aiter__(self) -> _IterableResponseWrapper:
        """Return the iterator."""
        return self

    async def __anext__(self) -> Any:
        """Return the next item from the iterator."""
        if self._iter_is_async:
            _logger.debug("`grpc_response` is async, awaiting next item")
            return await anext(self._iter)

        try:
            _logger.debug("`grpc_response` is sync, getting next item without await")
            return next(self._iter)
        except StopIteration as exc:
            raise StopAsyncIteration from exc

    async def aclose(self) -> None:
        """Close the iterator."""
        if self._iter_is_generator:
            if self._iter_is_async:
                _logger.debug(
                    "`grpc_response` is async generator, awaiting for `aclose()`"
                )
                await self._iter.aclose()
            else:
                _logger.debug("`grpc_response` is generator, calling `close()`")
                self._iter.close()
