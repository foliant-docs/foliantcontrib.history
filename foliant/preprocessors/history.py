'''
Preprocessor for Foliant documentation authoring tool.
Generates history of releases for some set of Git repositories.
'''


import re
from pathlib import Path
from operator import itemgetter
from subprocess import run, PIPE, STDOUT, CalledProcessError

from foliant.preprocessors.base import BasePreprocessor
from foliant.preprocessors import includes


class Preprocessor(BasePreprocessor):
    defaults = {
        'repos': [],
        'revision': 'master',
        'changelog': 'changelog.md',
        'title': 'History of Releases',
        'level': 1,
        'date_format': 'year_first',
        'link': False,
        'limit': 0
    }

    tags = 'history',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('history')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def _get_repo_history(self, repo_url: str, changelog_file_path: Path) -> list:
        repo_history = []

        changelog_git_history = run(
            f'git log --patch --date=short -- "{changelog_file_path}"',
            cwd=changelog_file_path.parent,
            shell=True,
            check=True,
            stdout=PIPE,
            stderr=STDOUT
        )

        if changelog_git_history.stdout:
            changelog_git_history_decoded = changelog_git_history.stdout.decode('utf8', errors='ignore')

            with open(changelog_file_path, encoding='utf8') as changelog_file:
                changelog_file_content = changelog_file.read()

            for heading in re.finditer(
                r'^\#\s+(?P<content>.*)?\s*$',
                changelog_file_content,
                flags=re.MULTILINE
            ):
                heading_full = heading.group(0)
                heading_content = heading.group('content')

                commit_summary = re.search(
                    r'\nDate: +(?P<date>.+)\n' + r'((?!Date: ).*\n|\n)+' + rf'\+{heading_full}',
                    changelog_git_history_decoded,
                )

                repo_history.append(
                    {
                        'date': commit_summary.group('date'),
                        'repo': repo_url,
                        'changelog': changelog_file_path,
                        'version': heading_content
                    }
                )

        return repo_history

    def _process_history(self, options: dict) -> str:
        self.logger.debug(f'History statement found, options: {options}')

        repo_urls = options.get('repos', self.options['repos'])
        revision = options.get('revision', self.options['revision'])
        changelog_file_subpath = options.get('changelog', self.options['changelog'])
        title = options.get('title', self.options['title'])
        first_heading_level = options.get('level', self.options['level'])
        date_format = options.get('date_format', self.options['date_format'])
        generate_link = options.get('link', self.options['link'])
        limit = options.get('limit', self.options['limit'])

        if not isinstance(repo_urls, list):
            repo_urls_to_append = []
            repo_urls_to_append.append(repo_urls)
            repo_urls = repo_urls_to_append

        self.logger.debug(
            f'Repo URLs: {repo_urls}, ' +
            f'revision: {revision}, ' +
            f'changelog subpath: {changelog_file_subpath}, ' +
            f'title: {title}, ' +
            f'first heading level: {first_heading_level}, ' +
            f'date format: {date_format}, ' +
            f'link generation: {generate_link}, ' +
            f'limit: {limit}'
        )

        history = []

        for repo_url in repo_urls:
            repo_path = includes.Preprocessor(
                self.context,
                self.logger
            )._sync_repo(repo_url, revision)

            self.logger.debug(f'Repo: {repo_url}, path: {repo_path}')

            changelog_file_path = (repo_path / changelog_file_subpath).resolve()

            if changelog_file_path.exists():
                repo_history = self._get_repo_history(repo_url, changelog_file_path)

                self.logger.debug(f'Repo history: {repo_history}')

                history.extend(repo_history)

            else:
                self.logger.debug('Changelog file not found')

        history.sort(key=itemgetter('version'), reverse=True)
        history.sort(key=itemgetter('repo'))
        history.sort(key=itemgetter('date'), reverse=True)

        self.logger.debug(f'Sorted history: {history}')

        history_markdown = f'# {title}\n\n'

        items_count = 0

        for history_item in history:
            history_markdown_part = includes.Preprocessor(
                self.context,
                self.logger
            )._process_include(
                included_file_path=history_item['changelog'],
                from_heading=history_item['version'],
                nohead=True
            )

            repo_name = history_item['repo'].split('/')[-1].rsplit('.', maxsplit=1)[0]

            output_date = history_item["date"]

            if date_format == 'day_first':
                output_date = re.sub(
                    r'^(?P<year>\d{4})\-(?P<month>\d{2})\-(?P<day>\d{2})$',
                    r'\g<day>.\g<month>.\g<year>',
                    output_date
                )

            history_markdown += f'## [{output_date}] '

            if generate_link:
                history_markdown += f'[{repo_name}]({history_item["repo"]}) '

            else:
                history_markdown += f'{repo_name} '

            history_markdown += f'{history_item["version"]}\n\n{history_markdown_part}\n'

            items_count += 1

            if items_count == limit:
                self.logger.debug(f'Limit reached: {items_count}')

                break

        if first_heading_level > 1:
            history_markdown = includes.Preprocessor(
                self.context,
                self.logger
            )._cut_from_position_to_position(
                content=history_markdown,
                sethead=first_heading_level
            )

        return history_markdown

    def process_history(self, content: str) -> str:
        def _sub(history_statement) -> str:
            return self._process_history(
                self.get_options(history_statement.group('options'))
            )

        processed_content = self.pattern.sub(_sub, content)

        return processed_content

    def apply(self):
        self.logger.info('Applying preprocessor')

        for markdown_file_path in self.working_dir.rglob('*.md'):
            self.logger.debug(f'Processing Markdown file: {markdown_file_path}')

            with open(markdown_file_path, encoding='utf8') as markdown_file:
                content = markdown_file.read()

            processed_content = self.process_history(content)

            if processed_content:
                with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                    markdown_file.write(processed_content)

        self.logger.info('Preprocessor applied')
