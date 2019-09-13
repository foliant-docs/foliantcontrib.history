# History

History is a preprocessor that generates single linear history of releases for multiple Git repositories based on their changelogs. The history may be represented as Markdown, and as RSS feed.

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
    source_heading_level: 1
    target_heading_level: 1
    target_heading_template: '[%date%] [%repo%](%link%) %version%'
    date_format: year_first
    limit: 0
    rss: false
    rss_file: rss.xml
    rss_title: 'History of Releases'
    rss_link: ''
    rss_description: ''
    rss_language: en-US
    rss_item_title_template: '%repo% %version%'
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

`source_heading_level`
:   Level of headings that precede descriptions of releases in the source Markdown content. It must be the same for all listed repositories.

`target_heading_level`
:   Level of headings that precede descriptions of releases in the target Markdown content of generated history.

`target_heading_template`
:   Template for top-level headings in the target Markdown content. You may use any characters, and the variables: `%date%`—date, `%repo%`—repo name, `%link%`—repo URL, `%version%`—content of source changelog heading (usually includes release version).

`date_format`
:   Output date format to use in the target Markdown content. If the default value `year_first` is used, the date “September 4, 2019” will be represented as `2019-09-04`. If the `day_first` value is used, this date will be represented as `04.09.2019`.

`limit`
:   Maximum number of items to include into the target Markdown content; `0` means no limit.

`rss`
:   Flag that tells the preprocessor to export the history into RSS feed. Note that the parameters `target_heading_level`, `target_heading_template`, `date_format`, and `limit` are applied to Markdown content only, not to RSS feed content.

`rss_file`
:   Subpath to the file with RSS feed. It’s relative to the temporary working directory during building, to the directory of built project after building, and to the `rss_link` value in URLs.

`rss_title`
:   RSS channel title.

`rss_link`
:   RSS channel link, e.g. `https://foliant-docs.github.io/docs/`. If the `rss` parameter value is `rss.xml`, the RSS feed URL will be `https://foliant-docs.github.io/docs/rss.xml`.

`rss_description`
:   RSS channel description.

`rss_language`
:   RSS channel language.

`rss_item_title_template`
:   Template for titles of RSS feed items. You may use any characters, and the variables: `%repo%`—repo name, `%version%`—content of source changelog heading (usually includes release version).

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
<<history
    repos="https://github.com/foliant-docs/foliantcontrib.mkdocs.git"
    revision="develop"
    limit="5"
    rss="true"
    rss_file="some_another.xml"
    ...
>
</history>
```
