from pathlib import Path
from typing import List
from gallery_dl import config, job

def download_image(url: str) -> List[Path]:
    download_path = Path("downloads").resolve()
    download_path.mkdir(parents=True, exist_ok=True)

    # Load existing configuration
    config.load()

    # Set configuration using the correct internal API
    # Based on the source: set(path, key, value)
    config.set((), "base-directory", str(download_path))
    
    # Set extractor configuration
    config.set(("extractor",), "instagram", {
        "cookies": "cache/cookies.txt",
    })

    try:
        download_job = job.DownloadJob(url)
        download_job.run()
    except Exception as error:
        raise ValueError(f"Failed to download {url}", error)

    downloaded_files = [f for f in download_path.rglob("*") if f.is_file()]
    return downloaded_files[::-1]