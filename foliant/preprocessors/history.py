'''
Preprocessor for Foliant documentation authoring tool.
Generates history of releases for some set of Git repositories.
'''


import re
from datetime import datetime
from hashlib import md5
from markdown import markdown
from operator import itemgetter
from pathlib import Path
from subprocess import run, PIPE, STDOUT, CalledProcessError

from foliant.preprocessors.base import BasePreprocessor
from foliant.preprocessors import includes


class Preprocessor(BasePreprocessor):
    defaults = {
        'repos': [],
        'revision': 'master',
        'changelog': 'changelog.md',
        'source_heading_level': 1,
        'target_heading_level': 1,
        'target_heading_template': '[%date%] [%repo%](%link%) %version%',
        'date_format': 'year_first',
        'limit': 0,
        'rss': False,
        'rss_file': 'rss.xml',
        'rss_title': 'History of Releases',
        'rss_link': '',
        'rss_description': '',
        'rss_language': 'en-US',
        'rss_item_title_template': '%repo% %version%'
    }

    tags = 'history',

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('history')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def _get_repo_history(
        self,
        repo_url: str,
        changelog_file_path: Path,
        source_heading_level: int
    ) -> list:
        self.logger.debug('Running git log command to get changelog file history')

        changelog_git_history = run(
            f'git log --reverse --patch --date=iso -- "{changelog_file_path}"',
            cwd=changelog_file_path.parent,
            shell=True,
            check=True,
            stdout=PIPE,
            stderr=STDOUT
        )

        repo_history = []

        if changelog_git_history.stdout:
            self.logger.debug('Processing the command output and the changelog file')

            changelog_git_history_decoded = changelog_git_history.stdout.decode('utf8', errors='ignore')

            changelog_git_history_decoded = changelog_git_history_decoded.replace('\r\n', '\n')

            with open(changelog_file_path, encoding='utf8') as changelog_file:
                changelog_file_content = changelog_file.read()

            for heading in re.finditer(
                r'^\#{' + rf'{source_heading_level}' + r'}\s+(?P<content>.*)?\s*$',
                changelog_file_content,
                flags=re.MULTILINE
            ):
                heading_full = heading.group(0)

                self.logger.debug(f'Heading found: {heading_full}')

                heading_content = heading.group('content')

                commit_summary = re.search(
                    r'\nDate: +(?P<date>.+)\n' + r'((?!Date: ).*\n|\n)+' + rf'\+{re.escape(heading_full)}',
                    changelog_git_history_decoded,
                )

                if commit_summary:
                    self.logger.debug('Calling Includes preprocessor to get changelog part')

                    description = includes.Preprocessor(
                        self.context,
                        self.logger
                    )._process_include(
                        included_file_path=changelog_file_path,
                        from_heading=heading_content,
                        sethead=1,
                        nohead=True
                    )

                    repo_name = repo_url.split('/')[-1].rsplit('.', maxsplit=1)[0]

                    repo_history.append(
                        {
                            'date': commit_summary.group('date'),
                            'repo_name': repo_name,
                            'repo_url': repo_url,
                            'version': heading_content,
                            'description': description
                        }
                    )

                else:
                    self.logger.debug('Related commit not found')

        else:
            self.logger.debug('The command returned nothing')

        return repo_history

    def _generate_history_markdown (
        self,
        history: list,
        target_heading_level: int,
        target_heading_template: str,
        date_format: str,
        limit: int
    ) -> str:
        history_markdown = ''
        items_count = 0

        for history_item in history:
            markdown_date = history_item['date']

            date_pattern = re.compile(
                r'^(?P<year>\d{4})\-(?P<month>\d{2})\-(?P<day>\d{2}) (?P<time>\S+) (?P<timezone>\S+)$'
            )

            if date_format == 'year_first':
                markdown_date = re.sub(
                    date_pattern,
                    r'\g<year>-\g<month>-\g<day>',
                    markdown_date
                )

            elif date_format == 'day_first':
                markdown_date = re.sub(
                    date_pattern,
                    r'\g<day>.\g<month>.\g<year>',
                    markdown_date
                )

            markdown_heading = (
                target_heading_template
            ).replace(
                '%date%', markdown_date
            ).replace(
                '%repo%', history_item['repo_name']
            ).replace(
                '%link%', history_item['repo_url']
            ).replace(
                '%version%', history_item['version']
            )

            history_markdown += f'# {markdown_heading}\n\n{history_item["description"]}\n\n'

            items_count += 1

            if items_count == limit:
                self.logger.debug(f'Limit reached: {items_count}')

                break

        self.logger.debug(f'Calling Includes preprocessor to shift heading level to {target_heading_level}')

        history_markdown = includes.Preprocessor(
            self.context,
            self.logger
        )._cut_from_position_to_position(
            content=history_markdown,
            sethead=target_heading_level
        )

        return history_markdown

    def _generate_history_rss(
        self,
        history: list,
        rss_file_subpath: str,
        rss_channel_title: str,
        rss_channel_link: str,
        rss_channel_description: str,
        rss_channel_language: str,
        rss_item_title_template: str
    ) -> None:
        if rss_channel_link.endswith('/'):
            atom_link_href = f'{rss_channel_link}{rss_file_subpath}'

        else:
            atom_link_href = f'{rss_channel_link}/{rss_file_subpath}'

        history_rss = f'''<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title>{rss_channel_title}</title>
        <link>{rss_channel_link}</link>
        <atom:link href="{atom_link_href}" rel="self" type="application/rss+xml" />
        <description>{rss_channel_description}</description>
        <language>{rss_channel_language}</language>
'''

        for history_item in history:
            rss_item_pub_date = datetime.strftime(
                datetime.strptime(history_item['date'], '%Y-%m-%d %H:%M:%S %z'),
                '%a, %d %b %Y %H:%M:%S %z'
            )

            rss_item_guid = f'{history_item["repo_url"]}#' + md5(
                (
                    f'{history_item["repo_name"]} ' +
                    f'{history_item["version"]} ' +
                    f'{history_item["date"]} ' +
                    f'{history_item["description"]}'
                ).encode()
            ).hexdigest()

            rss_item_title = (
                rss_item_title_template
            ).replace(
                '%repo%', history_item['repo_name']
            ).replace(
                '%version%', history_item['version']
            ).replace(
                '&', '&amp;'
            ).replace(
                '<', '&lt;'
            ).replace(
                '>', '&gt;'
            ).replace(
                '"', '&quot;'
            ).replace(
                "'", '&#39;'
            )

            history_rss += f'''        <item>
            <title>{rss_item_title}</title>
            <link>{history_item["repo_url"]}</link>
            <guid>{rss_item_guid}</guid>
            <pubDate>{rss_item_pub_date}</pubDate>
            <description><![CDATA[{markdown(history_item["description"])}]]></description>
        </item>
'''

        history_rss += '    </channel>\n</rss>\n'

        with open(self.working_dir / rss_file_subpath, 'w', encoding='utf8') as rss_file:
           rss_file.write(history_rss)

        return None

    def _process_history(self, options: dict) -> str:
        self.logger.debug(f'History statement found, options: {options}')

        repo_urls = options.get('repos', self.options['repos'])
        revision = options.get('revision', self.options['revision'])
        changelog_file_subpath = options.get('changelog', self.options['changelog'])
        source_heading_level = options.get('source_heading_level', self.options['source_heading_level'])
        target_heading_level = options.get('target_heading_level', self.options['target_heading_level'])
        target_heading_template = options.get('target_heading_template', self.options['target_heading_template'])
        date_format = options.get('date_format', self.options['date_format'])
        limit = options.get('limit', self.options['limit'])
        rss_enable = options.get('rss', self.options['rss'])
        rss_file_subpath = options.get('rss_file', self.options['rss_file'])
        rss_channel_title = options.get('rss_title', self.options['rss_title'])
        rss_channel_link = options.get('rss_link', self.options['rss_link'])
        rss_channel_description = options.get('rss_description', self.options['rss_description'])
        rss_channel_language = options.get('rss_language', self.options['rss_language'])
        rss_item_title_template = options.get('rss_item_title_template', self.options['rss_item_title_template'])

        if not isinstance(repo_urls, list):
            repo_urls = [repo_urls]

        self.logger.debug(
            f'Repo URLs: {repo_urls}, ' +
            f'revision: {revision}, ' +
            f'changelog subpath: {changelog_file_subpath}, ' +
            f'source heading level: {source_heading_level}, ' +
            f'target heading level: {target_heading_level}, ' +
            f'target heading template: {target_heading_template}, ' +
            f'date format: {date_format}, ' +
            f'limit: {limit}, ' +
            f'RSS generation enabled: {rss_enable}, ' +
            f'RSS file subpath: {rss_file_subpath}, ' +
            f'RSS channel title: {rss_channel_title}, ' +
            f'RSS channel link: {rss_channel_link}, ' +
            f'RSS channel description: {rss_channel_description}, ' +
            f'RSS channel language: {rss_channel_language}, ' +
            f'RSS item title template: {rss_item_title_template}'
        )

        history = []

        for repo_url in repo_urls:
            self.logger.debug('Calling Includes preprocessor to fetch from Git repo')

            repo_path = includes.Preprocessor(
                self.context,
                self.logger
            )._sync_repo(repo_url, revision)

            self.logger.debug(f'Repo: {repo_url}, path: {repo_path}')

            changelog_file_path = (repo_path / changelog_file_subpath).resolve()

            self.logger.debug(f'Full changelog file path: {changelog_file_path}')

            if changelog_file_path.exists():
                self.logger.debug('Getting repo history')

                repo_history = self._get_repo_history(repo_url, changelog_file_path, source_heading_level)

                self.logger.debug(f'Repo history: {repo_history}')

                history.extend(repo_history)

            else:
                self.logger.debug('Changelog file not found')

        history.sort(key=itemgetter('date'), reverse=True)

        self.logger.debug(f'Final history: {history}')

        self.logger.debug('Generating history Markdown content')

        history_markdown = self._generate_history_markdown(
            history,
            target_heading_level,
            target_heading_template,
            date_format,
            limit
        )

        if rss_enable:
            self.logger.debug('Generating history RSS content')

            self._generate_history_rss(
                history,
                rss_file_subpath,
                rss_channel_title,
                rss_channel_link,
                rss_channel_description,
                rss_channel_language,
                rss_item_title_template
            )

        self.logger.debug('History generation completed')

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
