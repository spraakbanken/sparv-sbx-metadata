"""Exporter for creating metadata files for analyses."""

# ruff: noqa: PLC0415
import re
from pathlib import Path
from typing import Optional, Union

import yaml
from sparv.api import Config, Export, Output, exporter, get_logger
from sparv.api.util.misc import dump_yaml
from sparv.core import paths, registry
from sparv.core.snake_utils import make_param_dict

from . import metadata_utils
from .yaml_export import WARNING_MESSAGE

logger = get_logger(__name__)

METADATA_FILENAME = "metadata.yaml"


@exporter(description="YAML export of Sparv analysis metadata")
def analysis_metadata_export(
    out: Export = Export("sbx_metadata/.dummy"),
    md_contact: dict = Config("sbx_metadata.contact_info"),
) -> None:
    """Export metadata for Sparv analyses."""
    # Export dirs
    export_dir_analysis = Path(out).parent / "analysis"
    export_dir_utility = Path(out).parent / "utility"

    metadata_files, plugin_modules = find_metadata_files()
    written_counter = create_export_files(
        export_dir_analysis, export_dir_utility, md_contact, metadata_files, plugin_modules
    )

    # Create dummy output (since Sparv requires a known output)
    Path(out).touch()
    logger.info("%d metadata files exported", written_counter)


def create_export_files(
    export_dir_analysis: Path,
    export_dir_utility: Path,
    md_contact: dict,
    metadata_files: dict[str, Path],
    plugin_modules: set[str],
) -> int:
    """Create export files from metadata."""
    written_counter = 0

    for module_name, metadata_file in metadata_files.items():
        # Collect data to be used for validation
        known = collect_known(module_name)
        parents = {}
        all_ids = set()

        with metadata_file.open(encoding="utf-8") as f:
            metadata: list[dict] = list(yaml.load_all(f, Loader=yaml.SafeLoader))

        # Loop through metadata documents
        for data in metadata:
            # Inherit parent data
            if parent_id := data.pop("parent", None):
                parent_data = parents[parent_id].copy()
                parent_data.update(data)
                data = parent_data  # noqa: PLW2901

            if data.pop("abstract", False):
                # This metadata is only used when inherited by other metadata
                parents[data["id"]] = data
                continue

            # Some keys should not be part of the final result
            analysis_id = data.pop("id")
            if analysis_id in all_ids:
                logger.error("More than one analysis with the id '%s' in module '%s'", analysis_id, module_name)
                continue
            all_ids.add(analysis_id)
            annotations = data.pop("annotations", None)
            example_output = data.pop("example_output", None)

            if data.get("type") == "analysis" or annotations:
                if not annotations:
                    logger.error("No annotations found for analysis '%s' in module '%s'", analysis_id, module_name)
                    continue

                annotation_info, unknown_annotations = get_annotation_info(annotations, known)

                if unknown_annotations:
                    logger.error(
                        "Unknown annotations in analysis '%s' for module '%s': %s",
                        analysis_id,
                        module_name,
                        ", ".join(unknown_annotations),
                    )
                    continue

                data["type"] = "analysis"
                export_dir = export_dir_analysis

                set_analysis_unit(data, annotations, annotation_info)
                generate_analysis_example(
                    data, annotations, annotation_info, plugin_modules, module_name, example_output
                )

            elif data.get("type") == "utility" or data.get("sparv_handler"):
                data["type"] = "utility"
                export_dir = export_dir_utility
                handler = data["sparv_handler"]

                if handler in known["importers"]:
                    handler_type = "importer"
                elif handler in known["exporters"]:
                    handler_type = "exporter"
                else:
                    logger.error("Unknown handler in '%s' for module '%s': '%s'", analysis_id, module_name, handler)
                    continue

                generate_utility_example(data, handler, handler_type)
            else:
                logger.error("Analysis metadata '%s' in module '%s' is of an unknown type.", analysis_id, module_name)
                continue

            if not data.get("tool"):
                data["tool"] = "Sparv"

            if not data.get("contact_info") and md_contact:
                data["contact_info"] = metadata_utils.SBX_DEFAULT_CONTACT if md_contact == "sbx-default" else md_contact

            # Remove empty fields
            data = {k: v for k, v in data.items() if v}

            export_dir.mkdir(exist_ok=True, parents=True)
            (export_dir / f"{analysis_id}.yaml").write_text(WARNING_MESSAGE + dump_yaml(data), encoding="utf-8")
            logger.debug("%s/%s.yaml written", export_dir, analysis_id)
            written_counter += 1
    return written_counter


def get_annotation_info(annotations: list[str], known: dict) -> tuple[dict, set]:
    """Get annotation info for the analysis' list of annotations."""
    # Handle wildcard annotations by using regex
    known_annotation_patterns = {re.sub(r"\\{.+?\\}", ".+", re.escape(a)): d for a, d in known["annotations"].items()}
    unknown_annotations = set()
    annotation_info = {}
    for annotation in annotations:
        for pattern, ann_info in known_annotation_patterns.items():
            if re.fullmatch(pattern, annotation):
                annotation_info[annotation] = ann_info
                break
        else:
            unknown_annotations.add(annotation)
    return annotation_info, unknown_annotations


def generate_analysis_example(
    data: dict,
    annotations: list[str],
    annotation_info: dict,
    plugin_modules: set[str],
    module_name: str,
    example_output: Optional[str],
) -> None:
    """Update data dictionary with a generated example unless one is already manually set."""
    plugin_info = ""
    if module_name in plugin_modules:
        plugin_url = data.pop("plugin_url", None)
        plugin_link = f"[{module_name}]({plugin_url})" if plugin_url else module_name
        plugin_info = (
            f"You also need to install the following plugin: *{plugin_link}*.\n\n"
            "For general information on how to install plugins, see [here]"
            "(https://spraakbanken.gu.se/sparv/#/user-manual/installation-and-setup?id=plugins).\n\n"
        )
    # TODO: Add link to Mink if the analysis is available there (based on collection or something else)
    if not data.get("example"):
        example_extra = data.pop("example_extra", None)
        data["example"] = (
            "This analysis is used with Sparv. Check out [Sparv's quick start guide]"
            "(https://spraakbanken.gu.se/sparv/#/user-manual/quick-start) to get started!\n"
            "\n"
            "To use this analysis, add the following "
            f"line{'s' if len(annotations) > 1 else ''} under `export.annotations` in the Sparv "
            "[corpus configuration file]"
            "(https://spraakbanken.gu.se/sparv/#/user-manual/quick-start?id=creating-the-config-file):\n"
            "\n"
            "```yaml\n"
            f"{"\n".join(f"- {a}  # {annotation_info[a].description}" for a in annotations)}\n"
            "```\n"
            "\n"
            f"{example_extra + '\n\n' if example_extra else ''}"
            f"{plugin_info}"
            "For more info on how to use Sparv, check out the [Sparv documentation]"
            "(https://spraakbanken.gu.se/sparv).\n"
        )
    if example_output:
        data["example"] += f"\nExample output:\n{example_output.strip()}"


def generate_utility_example(data: dict, handler: str, handler_type: str) -> None:
    """Update data dictionary with a generated example unless one is already manually set."""
    if not data.get("example"):
        example_extra = data.get("example_extra")
        data["example"] = (
            f"This {handler_type} is used with Sparv. Check out [Sparv's quick start guide]"
            "(https://spraakbanken.gu.se/sparv/#/user-manual/quick-start) to get started!\n"
            "\n"
            f"To use this {handler_type}, run Sparv with the argument '{handler}':\n\n"
            "```sh\n"
            f"sparv run {handler}\n"
            "```\n"
            "\n"
            f"{example_extra + '\n\n' if example_extra else ''}"
            "For more info on how to use Sparv, check out the [Sparv documentation]"
            "(https://spraakbanken.gu.se/sparv).\n"
        )


def set_analysis_unit(data: dict, annotations: list[str], annotation_info: dict[str, Output]) -> None:
    """Set analysis unit based on annotations, unless provided."""
    if "analysis_unit" not in data and annotations:
        for annotation in annotations:
            if annotation.startswith("<token>") or annotation_info[annotation].cls == "token":
                data["analysis_unit"] = "token"
                break
            if annotation.startswith("<sentence>") or annotation_info[annotation].cls == "sentence":
                data["analysis_unit"] = "sentence"
                break
            if annotation.startswith("<paragraph>") or annotation_info[annotation].cls == "paragraph":
                data["analysis_unit"] = "paragraph"
                break
            if annotation.startswith("<text>") or annotation_info[annotation].cls == "text":
                data["analysis_unit"] = "text"
                break


def find_metadata_files() -> tuple[dict[str, Path], set[str]]:
    """Find all metadata files for Sparv modules and plugins."""
    import importlib
    import pkgutil

    from importlib_metadata import entry_points

    # Find all Sparv modules and installed plugins
    modules = pkgutil.iter_modules([str(paths.sparv_path / paths.modules_dir)])
    plugins = entry_points(group="sparv.plugin")

    metadata_files = {}
    plugin_modules = set()

    # Find all regular Sparv modules with metadata.yaml files
    for module_info in modules:
        with importlib.resources.as_file(
            importlib.resources.files("sparv") / paths.modules_dir / module_info.name
        ) as path:
            metadata_path = path / METADATA_FILENAME
            if metadata_path.exists():
                metadata_files[module_info.name] = metadata_path

                # Import standard Sparv module
                module = importlib.import_module(f"sparv.{paths.modules_dir}.{module_info.name}")
                registry.add_module_to_registry(module, module_info.name, skip_language_check=True)

    # Find all Sparv plugins with metadata.yaml files
    for entry_point in plugins:
        if entry_point.name == "sbx_metadata":
            # Don't load this plugin, as it has already been loaded by run_snake.py
            continue
        plugin_modules.add(entry_point.name)
        with importlib.resources.as_file(importlib.resources.files(entry_point.name)) as path:
            metadata_path = path / METADATA_FILENAME
            if metadata_path.exists():
                metadata_files[entry_point.name] = metadata_path

                # Import Sparv plugin
                module = entry_point.load()
                registry.add_module_to_registry(module, entry_point.name, skip_language_check=True)

    return metadata_files, plugin_modules


def collect_known(module_name: str) -> dict:
    """Collect data about a module, to be used for validation."""
    import inspect

    known = {
        "annotations": {},
        "importers": set(),
        "exporters": set(),
    }
    for f_name, f in registry.modules[module_name].functions.items():
        if f["type"] == registry.Annotator.annotator:
            params = make_param_dict(inspect.signature(f["function"]).parameters)
            for param in params:
                if params[param][1] is Output:
                    known["annotations"][params[param][0].name] = params[param][0]
        elif f["type"] == registry.Annotator.importer:
            known["importers"].add(f"{module_name}:{f_name}")
        elif f["type"] == registry.Annotator.exporter:
            known["exporters"].add(f"{module_name}:{f_name}")
    return known
