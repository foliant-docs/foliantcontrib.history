[![](https://img.shields.io/pypi/v/foliantcontrib.history.svg)](https://pypi.org/project/foliantcontrib.history/) [![](https://img.shields.io/github/v/tag/foliant-docs/foliantcontrib.history.svg?label=GitHub)](https://github.com/foliant-docs/foliantcontrib.history)

# History

History is a preprocessor that generates single linear history of releases for multiple Git repositories based on their changelog files, tags, or commits. The history may be represented as Markdown, and as RSS feed.

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
    revision: ''
    name_from_readme: false
    readme: README.md
    from: changelog
    merge_commits: true
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
:   Revision or branch name to use. If `revision` is not specified, the default branch of the repository will be used. If you specify a revision or branch name, it will be used for all specified repositories.

`name_from_readme`
:   Flag that tells the preprocessor to try to use the content of the first heading of README file in each listed repository as the repo name. If the flag set to `false`, or an attempt to get the first heading content is unsuccessful, the repo name will be based on the repo URL.

`readme`
:   Path to README file. README files must be located at the same paths in all listed repositories.

`from`
:   Data source to generate history: `changelog`—changelog file, `tags`—tags, `commits`—all commits. Data sources of the same type will be used for all listed repositories.

`merge_commits`
:   Flag that tells the preprocessor to include merge commits into history when `from: commits` is used.

`changelog`
:   Path to changelog file. Changelogs must be located at the same paths in all listed repositories.

`source_heading_level`
:   Level of headings that precede descriptions of releases in the source Markdown content. It must be the same for all listed repositories.

`target_heading_level`
:   Level of headings that precede descriptions of releases in the target Markdown content of generated history.

`target_heading_template`
:   Template for top-level headings in the target Markdown content. You may use any characters, and the variables: `%date%`—date, `%repo%`—repo name, `%link%`—repo URL, `%version%`—version data (content of source changelog heading, tag value, or commit hash).

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
:   Template for titles of RSS feed items. You may use any characters, and the variables: `%repo%`—repo name, `%version%`—version data.

## Usage

To insert some history into Markdown content, use the `<history></history>` tags:

```markdown
Some optional content here.

<history></history>

More optional content.
```

If no attributes specified, the values of options from the project config will be used.

You may override each config option value with the attribute of the same name. Example:

```
<history
    repos="https://github.com/foliant-docs/foliantcontrib.mkdocs.git"
    revision="develop"
    limit="5"
    rss="true"
    rss_file="some_another.xml"
    ...
>
</history>
```
