# Blender Addon Template

Proper python dev workflow for blender addons

1. Clone this repository

2. Update the project information in `pyproject.toml` and `src/__init__.py`

3. Install [PDM](https://pdm.fming.dev/latest/) for python
    ```shell
    pip install pdm
    ```

4. Run `pdm install` to get all the dev dependencies

5. The following actions are available

    - `pdm build` - creates a zip archive of your addon (requires an existing git tag)
    - `pdm test` - runs tests
    - `pdm format` - runs black to fomat your source code (configurable in pyproject.toml)
    - `pdm check` - runs mypy for type checking (configurable in pyproject.toml)
