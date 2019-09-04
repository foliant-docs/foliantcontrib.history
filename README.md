# History

History is a preprocessor that generates single linear history of releases for multiple Git repositories based on their changelogs.

## Installation

```bash
$ pip install foliantcontrib.history
```

## Config

To enable the preprocessor, add `history` to `preprocessors` section in the project config:

```yaml
preprocessors:
    - history
```

The preprocessor has a number of options with the following default values:

```yaml
- history:
    repos: []
    revision: master
    changelog: changelog.md
    title: History of Releases
    source_heading_level: 1
    target_top_level: 1
    date_format: year_first
    link: False
    limit: 0
```

`repos`
:   List of URLs of Git repositories that it’s necessary to generate history for.

    Example:

    ```yaml
    repos:
        - https://github.com/foliant-docs/foliant.git
        - https://github.com/foliant-docs/foliantcontrib.includes.git
    ```

`revision`
:   Revision or branch name to use. Branches that are used for stable releases must have the same names in all listed repositories.

`changelog`
:   Path to changelog file. Changelogs must be located at the same paths in all listed repositories.

`title`
:   Content of the top-level heading of the history.

`source_heading_level`
:   Level of headings that precede descriptions of releases in the source Markdown content. It must be the same for all listed repositories.

`target_top_level`
:   Level of the heading that contains `title` in the target Markdown content of generated history.

`date_format`
:   Output date format. If the default value `year_first` is used, dates are represented as `2019-09-04`. If the `day_first` value is used, dates are represented as `04.09.2019`.

`link`
:   Flag that tells the preprocessor to add the link to the repository to each heading of history item.

`limit`
:   Maximum number of items to include into the history; `0` means no limit.

## Usage

To insert some history into Markdown content, use the `<<history></history>` tags:

```markdown
Some optional content here.

<<history></history>

More optional content.
```

If no attributes specified, the values of options from the project config will be used.

You may override each config option value with the attribute of the same name. Example:

```
<<history repos="https://github.com/foliant-docs/foliantcontrib.mkdocs.git" revision="develop" link="True" limit="5"></history>
```
