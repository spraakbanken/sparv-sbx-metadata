# Analysis Metadata

[Språkbanken Text's list of analyses](https://spraakbanken.gu.se/analyser) is created from metadata files, similar to
those used for resources like corpora, lexicons, and models. While these metadata files can be created manually, for
Sparv plugins, we strongly recommend letting Sparv generate them for you based on a Sparv-specific metadata file
included in your plugin.

This Sparv-specific metadata file is a YAML file named `metadata.yaml`, placed in the same directory as the
`__init__.py` file of the plugin (see example below). If your plugin produces multiple analyses, they should all be
included in this file. More details about handling multiple analyses are provided in a separate section below.

```text
sparv-sbx-uppercase/
├── sbx_uppercase
│   ├── metadata.yaml
│   ├── uppercase.py
│   └── __init__.py
├── LICENSE
├── pyproject.toml
└── README.md
```

> [!NOTE]
>
> To avoid confusion, we will refer to the metadata files included in Sparv plugins as "Sparv metadata files," and the
> resulting metadata files (used for rendering the analysis section on the website) as "SBX metadata files."

The Sparv metadata file format shares most of its fields with the regular SBX metadata files, but with some differences.
We won't go into detail about the common fields here; for that, refer to the template for [SBX metadata files for
analyses](https://raw.githubusercontent.com/spraakbanken/metadata/refs/heads/main/yaml_templates/analysis.yaml). Below
is a description of the fields that are specific to analyses.

> [!NOTE]
>
> While this document mainly mention *analyses*, most of what is written here also applies to *utilities*. Utilities are
> basically analyses that don't produce annotations, like different import or export formats. Utilities also show up on
> the analyses page.

## Metadata Fields Specific for Analyses and Utilities

The following fields are specific to analyses. They are also included in the above template, but we will describe them
here in more detail.

- **id**: The `id` field for analyses differs from other resources, as it follows a specific format. The ID consists of
  four or five segments: `organization-language_code-task-tool-model`. If any segment contains multiple words, separate
  them with underscores. All segments except `model` are required. This ID also serves as the name of the analysis. The
  segments are:
  - A short name for the organization responsible for creating the Sparv plugin. For Språkbanken Text, use `sbx`.
  - The language that the analysis supports. The language code should be in ISO 639-3 format (e.g., `swe` for Swedish).
    Use `mul` for multiple languages or `zxx` for non-language-related utilities.
  - The task should be a short (one or two words) description of the analysis (e.g., `msd`, `lemmatization`,
    `sentiment`). Check the existing analyses for inspiration and to avoid creating unnecessary synonyms.
  - The tool should be a short name for any external tool or library used (e.g., `stanza`, `malt`). If no external tool
    is used, or if the tool is SBX internal, use `sparv` as the tool. Whether a Python library has tool status or not is
    not an easy question, but generally, if the analysis is completely dependent on the library, and the library cannot
    be exchanged for another one, it probably has tool status.
  - The model segment is used to identify the model used, if applicable. If no specific model is used, this segment can
    also be used to identify the tagset used, or in some way distinguish the analysis from others. For example, Sparv's
    XML export uses this field to specify the XML format (e.g., `xml_scrambled`).
- **description**: A longer description of the analysis, with translations in Swedish (`swe`) and English (`eng`).
  Markdown or HTML is allowed.
- **short_description**: A brief description in plain text, with translations in Swedish (`swe`) and English (`eng`).
  This will be shown in the analysis list view.
- **type**: Either `analysis` or `utility`. Defaults to `analysis` if left out.
- **task**: Analysis/utility task in English (e.g., 'part-of-speech tagging', 'dependency parsing'). Check the existing
  analyses for inspiration and to avoid creating unnecessary synonyms.
- **plugin_url**: URL to where the plugin can be found, e.g., the GitHub repository.
- **analysis_unit**: (Optional) The text unit on which the analysis is applied (e.g., `token`, `sentence`, `paragraph`,
  `text`).
- **tools**: (Optional) Information about external tools producing the analysis, including `name`, `url`, `description`,
  and `license`.
- **models**: (Optional) Models used for the analysis, including `name`, `url`, `description`, and `license`.
- **example**: (Optional) Example of how to use the analysis and its output. This field should normally be left empty,
  as Sparv will fill it in automatically. Only use it if you want to override the default.
- **trained_on**: (Optional) Training data used.
- **tagset**: (Optional) Tagset used by the analysis.
- **evaluation_results**: (Optional) Evaluation results.
- **license**: (Optional) License for the code (e.g., license for the Sparv plugin). Defaults to 'MIT License' if left out.

## Fields Only Used in Sparv

The following fields are not part of the final SBX metadata files but are used by Sparv while generating them:

- **annotations**: List of annotations produced by the analysis. Required for analyses, but not utilities.
- **example_output**: (Optional) Example output of the analysis.
- **example_extra**: (Optional) Extra information to be appended to the example text.
- **abstract**: (Optional) Set to `true` to indicate that this is a parent metadata section. Used when several analyses
  share some data.
- **parent**: (Optional) The ID of the parent metadata section.

These fields are explained in more detail below.

### Annotations

The `annotations` field is a list of annotations produced by the analysis. Each annotation in this list should be an
annotation that is produced by an `annotator` in your plugin. For example:

```yaml
annotations:
  - <token>:malt.ref
  - <token>:malt.dephead_ref
  - <token>:malt.deprel
```

### Example and Usage Instructions

The `example` field in the final SBX metadata file should include instructions on how to use the analysis in Sparv, and
an example of the output. You rarely want to set this field manually. Instead, by using the fields `annotations`,
`example_output`, and optionally `example_extra`, Sparv can generate the `example` field for you.

`example_output` should include a short example of the output, preferably in XML format. The `example_extra` field is
optional and can be used to include any extra information about how to use the analysis, which will be included at the
end of the example. Examples of "extra information" could be configuration variables that need to be set to use the
analysis, or a description of the output format.

For example:

````yaml
annotations:
    - segment.token
example_output: |-
    ```xml
    <token>Det</token>
    <token>här</token>
    <token>är</token>
    <token>en</token>
    <token>korpus</token>
    <token>.</token>
    ```
example_extra: |-
    In order to use this tokenizer you need to add the following setting to your Sparv corpus configuration file:
    ```yaml
    segment:
        token_segmenter: linebreaks
    ```
````

Have a look at the final result of the above on [the analysis page
here](https://spraakbanken.gu.se/en/analyses/sbx-mul-tokenization-sparv-linebreaks).

### Multiple Analyses

If your plugin contains multiple Sparv annotators, producing different analyses, you need to create one metadata section
per analysis in the Sparv metadata file. Each section should be separated by a `---` line. Note that "one analysis" does
not equal "one annotation." One analysis may consist of multiple annotations. For example, the default dependency
analysis consists of three different annotations.

Often, the different analyses will share some metadata, such as contact info, list of tools, or license. To avoid
repetition, you can create a "parent" metadata section, which contains the common metadata. This section should
include the `abstract` field, set to `true`, to indicate that this section is not a complete metadata section, but a
"parent" section. The different analyses can then inherit the metadata from the parent section by referencing the
parent `id` using the `parent` field. Parent sections will not result in a separate SBX metadata file.

Note that the `id` of the parent section doesn't have to follow the same format as the other analyses, but it should
be suffixed with `-parent`.

See [the SALDO metadata
file](https://raw.githubusercontent.com/spraakbanken/sparv/refs/heads/dev/sparv/modules/saldo/metadata.yaml) for an
example of how to use the `parent` field.

### Other Things to Note

- The `name` field is not used for analyses and can be left out. Instead, the `id` field is used as the name of the
  analysis.
- You can leave out the `type` field if the type is `analysis`, as this will be set by default.
- If `license` is not specified, Sparv will set it to `MIT License`.
- If `contact_info` is not specified, Sparv will set it to the default SBX contact info.
- If the annotations produced are on one of the levels `token`, `sentence`, `paragraph`, or `text`, the `analysis_unit`
  field will be set automatically by Sparv.

## Generating the SBX Metadata File

Once your Sparv metadata file is ready, you can generate the SBX metadata file. To do this, you first need to make sure
that your plugin is installed in *editable mode* (using the `-e` flag during installation) for Sparv to have access to
the `metadata.yaml` file. Otherwise, no SBX metadata file will be generated. Then, install the `sparv-sbx-metadata`
plugin, available on [GitHub](https://github.com/spraakbanken/sparv-sbx-metadata).

Next, navigate to any directory containing a `config.yaml` file (e.g., a [corpus
directory](https://spraakbanken.gu.se/sparv/user-manual/preparing-your-corpus/#the-corpus-directory)) in the terminal,
and run the following command:

```sh
sparv run sbx_metadata:plugin_analysis_metadata_export
```

This will generate SBX metadata files and place them in the `export/sbx_metadata/` directory. Note that metadata will be
generated for *all* installed plugins, not just your plugin.

Next, add the relevant generated metadata files to [Språkbanken Text's metadata
repository](https://github.com/spraakbanken/metadata/tree/main/yaml) in the `yaml/analysis` or `yaml/utility` directory.
This step must be done manually but can be easily accomplished directly in the GitHub web interface. Use the "Add file"
button (ensure you are in the correct directory).

Once the SBX metadata files are added to the repository, your analyses should appear on the analyses page within a few
hours.
