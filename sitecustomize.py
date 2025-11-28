# Compatibility shim to provide a deprecated huggingface_hub.cached_download API
# for libraries (e.g., sentence-transformers 2.x) that still import it.
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import unquote, urlparse


def _install_cached_download_shim() -> None:
    try:
        import huggingface_hub as _hf  # type: ignore
    except Exception:  # pragma: no cover
        return

    if hasattr(_hf, "cached_download") or not hasattr(_hf, "hf_hub_download"):
        return

    def _cached_download(
        url: str,
        library_name: Optional[str] = None,
        library_version: Optional[str] = None,
        cache_dir: Optional[str | Path] = None,
        force_filename: Optional[str] = None,
        resume_download: Optional[bool] = None,
        proxies: Optional[Dict[str, str]] = None,
        etag_timeout: float = 10,
        local_files_only: bool = False,
        use_auth_token: Optional[str | bool] = None,
        user_agent: Optional[Dict[str, Any] | str] = None,
        force_download: bool = False,
        **kwargs: Any,
    ) -> str:
        """Approximate the old cached_download signature using hf_hub_download."""

        parsed = urlparse(url)
        parts = [part for part in unquote(parsed.path).strip("/").split("/") if part]
        if "resolve" not in parts:
            raise ValueError(f"Cannot parse huggingface URL: {url}")
        idx = parts.index("resolve")
        repo_id = "/".join(parts[:idx])
        revision = parts[idx + 1] if idx + 1 < len(parts) else "main"
        filename = "/".join(parts[idx + 2 :])
        if not filename:
            raise ValueError(f"Cannot infer filename from huggingface URL: {url}")

        return _hf.hf_hub_download(  # type: ignore[attr-defined]
            repo_id=repo_id,
            filename=filename,
            revision=revision,
            library_name=library_name,
            library_version=library_version,
            cache_dir=cache_dir,
            force_filename=force_filename,
            resume_download=resume_download,
            proxies=proxies,
            etag_timeout=etag_timeout,
            token=use_auth_token,
            user_agent=user_agent,
            force_download=force_download,
            local_files_only=local_files_only,
        )

    _hf.cached_download = _cached_download  # type: ignore[attr-defined]


_install_cached_download_shim()
